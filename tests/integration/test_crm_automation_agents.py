import pytest
import os
import shutil
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.future import select

from libs.infrastructure.database.models import (
    Base, Tenant, Contact, Invoice, InvoiceItem, InvoiceStatus,
    Appointment, AppointmentStatus, Conversation, Message, MessageSenderType,
    ConversationStatus
)
from libs.agents.invoice_agent.agent import (
    create_invoice_tool, generate_invoice_pdf_tool, HiqonisInvoiceAgent
)
from libs.agents.appointment_agent.agent import (
    create_appointment_tool, check_availability_tool, HiqonisAppointmentAgent
)
from libs.core.conversation.follow_up import HiqonisFollowUpService
from libs.core.conversation.broadcast import HiqonisBroadcastService
from libs.agents.chat_agent.agent import HiqonisChatAgent
from libs.integrations.channel_adapter import ChannelAdapter

# Setup in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Monkeypatch the database session factories for test execution
import libs.infrastructure.database.session as session_module
session_module.AsyncSessionLocal = TestSessionLocal

import libs.agents.invoice_agent.agent as invoice_agent_module
invoice_agent_module.AsyncSessionLocal = TestSessionLocal

import libs.agents.appointment_agent.agent as appointment_agent_module
appointment_agent_module.AsyncSessionLocal = TestSessionLocal

import libs.core.conversation.follow_up as follow_up_module
follow_up_module.AsyncSessionLocal = TestSessionLocal

# Mock ChannelAdapter for testing routing and message deliveries
class MockChannelAdapter(ChannelAdapter):
    def __init__(self):
        self.sent_messages = []

    async def send_text_message(self, recipient_id: str, text: str) -> bool:
        self.sent_messages.append({"recipient": recipient_id, "text": text, "type": "text"})
        return True

    async def send_media_message(self, recipient_id: str, media_url: str, media_type: str) -> bool:
        return True

    async def send_template_message(self, recipient_id: str, template_name: str, language_code: str, components=None) -> bool:
        self.sent_messages.append({"recipient": recipient_id, "template": template_name, "type": "template"})
        return True

# Mock ChatAgent to bypass OpenAI/Gemini network constraints
class MockChatAgent(HiqonisChatAgent):
    async def chat(self, prompt: str) -> str:
        return "Hi, ini pesan re-engagement otomatis dari Hiqonis AI. Bagaimana kabar Anda?"

@pytest.mark.asyncio
async def test_crm_automation_and_agents_flow():
    # 1. Initialize tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as db:
        # 2. Setup mock Tenant & Contact
        tenant = Tenant(name="Hiqonis Automation Corp")
        db.add(tenant)
        await db.flush()

        contact = Contact(
            tenant_id=tenant.id,
            name="John Doe",
            email="john@doe.com",
            phone="+6289999"
        )
        db.add(contact)
        await db.commit()

        # --- A. Test Invoice Agent Tools ---
        invoice_items = [
            {"description": "Konsultasi AI Integration", "quantity": 2, "unit_price": 150.0},
            {"description": "Setting up LiteLLM Gateway", "quantity": 1, "unit_price": 200.0}
        ]
        
        # Test create_invoice_tool
        res_inv = await create_invoice_tool(
            tenant_id=tenant.id,
            contact_id=contact.id,
            items=invoice_items,
            invoice_number="INV-TEST-999"
        )
        assert "Successfully created invoice" in res_inv
        assert "Total: 500.0" in res_inv

        # Verify in DB
        result_inv = await db.execute(select(Invoice).filter(Invoice.invoice_number == "INV-TEST-999"))
        inv = result_inv.scalars().first()
        assert inv is not None
        assert inv.total_amount == 500.0
        assert inv.status == InvoiceStatus.PENDING

        result_inv_items = await db.execute(select(InvoiceItem).filter(InvoiceItem.invoice_id == inv.id))
        items = list(result_inv_items.scalars().all())
        assert len(items) == 2
        assert items[0].description == "Konsultasi AI Integration"
        assert items[0].amount == 300.0

        # Test generate_invoice_pdf_tool
        res_pdf = await generate_invoice_pdf_tool(invoice_id=inv.id)
        assert "Successfully generated invoice PDF at" in res_pdf
        
        # Verify file actually created
        expected_path = f"/home/momo/Dokumen/Insyaallah Sukses/storage/invoices/invoice_INV-TEST-999.pdf"
        assert os.path.exists(expected_path)
        with open(expected_path, "r") as f:
            content = f.read()
            assert "John Doe" in content
            assert "LiteLLM" in content
            assert "500.00" in content

        # Clean up created file
        if os.path.exists(expected_path):
            os.remove(expected_path)

        # --- B. Test Appointment Agent Tools ---
        start_time = "2026-05-27T14:00:00"
        end_time = "2026-05-27T15:00:00"
        
        # Test create_appointment_tool
        res_appt = await create_appointment_tool(
            tenant_id=tenant.id,
            contact_id=contact.id,
            title="Meeting Kickoff Hiqonis",
            start_time=start_time,
            end_time=end_time,
            description="Discussing multi-agent architectures"
        )
        assert "Successfully scheduled appointment" in res_appt

        # Verify in DB
        result_appt = await db.execute(select(Appointment).filter(Appointment.title == "Meeting Kickoff Hiqonis"))
        appt = result_appt.scalars().first()
        assert appt is not None
        assert appt.start_time.hour == 14
        assert appt.status == AppointmentStatus.SCHEDULED

        # Test check_availability_tool
        res_avail = await check_availability_tool(tenant_id=tenant.id, date_str="2026-05-27")
        assert "Scheduled appointments on 2026-05-27:" in res_avail
        assert "14:00 - 15:00: Meeting Kickoff Hiqonis" in res_avail

        res_empty = await check_availability_tool(tenant_id=tenant.id, date_str="2026-05-28")
        assert "No scheduled appointments on 2026-05-28" in res_empty

        # --- C. Test Follow-up Automation Service ---
        # Create a conversation with an idle message (25 hours ago)
        conv = Conversation(
            tenant_id=tenant.id,
            channel="whatsapp",
            status=ConversationStatus.OPEN,
            is_human_takeover=False
        )
        db.add(conv)
        await db.flush()

        msg = Message(
            conversation_id=conv.id,
            sender_id="john_customer",
            sender_type=MessageSenderType.USER,
            content="Saya mau tanya lagi tentang fiturnya.",
            timestamp=datetime.utcnow() - timedelta(hours=25)
        )
        db.add(msg)
        await db.commit()

        # Initialize mock components
        chat_agent = MockChatAgent(system_instructions="Re-engage them")
        wa_adapter = MockChannelAdapter()
        adapters = {"whatsapp": wa_adapter}

        emitted_events = []
        async def mock_callback(event):
            emitted_events.append(event)

        followup_service = HiqonisFollowUpService(
            chat_agent=chat_agent,
            on_message_callback=mock_callback
        )

        # Trigger follow-up check (conversations idle > 24 hours)
        triggered = await followup_service.trigger_automated_follow_ups(
            db=db,
            tenant_id=tenant.id,
            channel_adapters=adapters,
            idle_hours=24.0
        )
        assert triggered == 1

        # Verify follow-up message sent via channel adapter
        assert len(wa_adapter.sent_messages) == 1
        assert wa_adapter.sent_messages[0]["recipient"] == "john_customer"
        assert "pesan re-engagement otomatis" in wa_adapter.sent_messages[0]["text"]

        # Verify socket event emitted
        assert len(emitted_events) == 1
        assert emitted_events[0]["sender_id"] == "hiqonis_followup_bot"
        assert "pesan re-engagement" in emitted_events[0]["content"]

        # Verify saved in DB
        result_messages = await db.execute(
            select(Message)
            .filter(Message.conversation_id == conv.id)
            .order_by(Message.timestamp.asc())
        )
        all_messages = list(result_messages.scalars().all())
        assert len(all_messages) == 2
        assert all_messages[0].sender_type == MessageSenderType.USER
        assert all_messages[1].sender_type == MessageSenderType.AI
        assert all_messages[1].sender_id == "hiqonis_followup_bot"

        # --- D. Test Broadcast Campaign Service ---
        # Clear event collectors and adapter records
        emitted_events.clear()
        wa_adapter.sent_messages.clear()

        broadcast_service = HiqonisBroadcastService(on_message_callback=mock_callback)

        campaign_result = await broadcast_service.send_broadcast_campaign(
            db=db,
            tenant_id=tenant.id,
            contact_ids=[contact.id],
            template_name="hiqonis_welcome_promo",
            language_code="id",
            channel_adapters=adapters
        )

        assert campaign_result["status"] == "completed"
        assert campaign_result["success_count"] == 1
        assert campaign_result["failed_count"] == 0

        # Verify message was routed to the contact's phone
        assert len(wa_adapter.sent_messages) == 1
        assert wa_adapter.sent_messages[0]["recipient"] == "+6289999"
        assert wa_adapter.sent_messages[0]["template"] == "hiqonis_welcome_promo"
        assert wa_adapter.sent_messages[0]["type"] == "template"

        # Verify logged in DB as SYSTEM message
        stmt_b_msg = (
            select(Message)
            .filter(Message.sender_id == "hiqonis_broadcast_campaign")
        )
        res_b_msg = await db.execute(stmt_b_msg)
        db_b_msg = res_b_msg.scalars().first()
        assert db_b_msg is not None
        assert "[Broadcast Campaign] Sent WhatsApp template" in db_b_msg.content
