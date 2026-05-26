import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from libs.infrastructure.database.models import Base, Tenant, Conversation, Message, ConversationStatus, MessageSenderType
from libs.core.conversation.routing_engine import MessageRoutingEngine
from libs.infrastructure.search.rag_service import RAGService
from libs.agents.chat_agent.agent import HiqonisChatAgent
from libs.integrations.channel_adapter import ChannelAdapter

# 1. Setup in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# 2. Setup mock channel adapter to inspect routed messages
class MockChannelAdapter(ChannelAdapter):
    def __init__(self):
        self.sent_messages = []

    async def send_text_message(self, recipient_id: str, text: str) -> bool:
        self.sent_messages.append({"recipient": recipient_id, "text": text, "type": "text"})
        return True

    async def send_media_message(self, recipient_id: str, media_url: str, media_type: str) -> bool:
        self.sent_messages.append({"recipient": recipient_id, "url": media_url, "media_type": media_type, "type": "media"})
        return True

    async def send_template_message(self, recipient_id: str, template_name: str, language_code: str, components=None) -> bool:
        self.sent_messages.append({"recipient": recipient_id, "template": template_name, "type": "template"})
        return True

# 3. Setup mock ChatAgent to prevent live network requirements during tests
class MockChatAgent(HiqonisChatAgent):
    async def chat(self, prompt: str) -> str:
        return "Hiqonis AI automated response matching the context."

@pytest.mark.asyncio
async def test_message_routing_automation_and_takeover():
    # A. Initialize database tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with TestSessionLocal() as db:
        # B. Setup mock entities
        tenant = Tenant(name="Hiqonis Monolith")
        db.add(tenant)
        await db.flush()
        
        # C. Initialize dependencies
        rag = RAGService(api_key=None)
        agent = MockChatAgent(system_instructions="You are an AI.")
        wa_adapter = MockChannelAdapter()
        adapters = {"whatsapp": wa_adapter}
        
        engine = MessageRoutingEngine(
            rag_service=rag,
            chat_agent=agent,
            channel_adapters=adapters
        )
        
        # Callback observer collector
        emitted_events = []
        async def mock_callback(event):
            emitted_events.append(event)
            
        engine.register_message_callback(mock_callback)
        
        # D. Test Scenario 1: AI Mode active (is_human_takeover = False)
        res_ai = await engine.route_incoming_message(
            db=db,
            tenant_id=tenant.id,
            channel="whatsapp",
            sender_id="user_phone_123",
            content="Halo, tolong infokan promo hari ini."
        )
        
        assert res_ai["status"] == "ai_handled"
        assert res_ai["ai_responded"] is True
        assert res_ai["reply"] == "Hiqonis AI automated response matching the context."
        
        # Check that adapter sent the message
        assert len(wa_adapter.sent_messages) == 1
        assert wa_adapter.sent_messages[0]["text"] == "Hiqonis AI automated response matching the context."
        
        # Check that 2 socket events were emitted (one for User, one for AI)
        assert len(emitted_events) == 2
        assert emitted_events[0]["sender_type"] == "user"
        assert emitted_events[1]["sender_type"] == "ai"
        
        # Verify messages are written to DB
        result_messages = await db.execute(select(Message).filter(Message.conversation_id == res_ai["conversation_id"]))
        db_messages = list(result_messages.scalars().all())
        assert len(db_messages) == 2
        assert db_messages[0].sender_type == MessageSenderType.USER
        assert db_messages[1].sender_type == MessageSenderType.AI
        
        # E. Test Scenario 2: Human Takeover active (is_human_takeover = True)
        # Fetch the active conversation
        result_conv = await db.execute(select(Conversation).filter(Conversation.id == res_ai["conversation_id"]))
        conv = result_conv.scalars().first()
        conv.is_human_takeover = True
        await db.commit()
        
        # Clear event collectors
        emitted_events.clear()
        wa_adapter.sent_messages.clear()
        
        # Route another user message
        res_human = await engine.route_incoming_message(
            db=db,
            tenant_id=tenant.id,
            channel="whatsapp",
            sender_id="user_phone_123",
            content="Saya ingin berbicara dengan staf sales."
        )
        
        # AI should stay silent and only User message gets logged & emitted
        assert res_human["status"] == "human_takeover"
        assert res_human["ai_responded"] is False
        assert len(wa_adapter.sent_messages) == 0
        assert len(emitted_events) == 1
        assert emitted_events[0]["sender_type"] == "user"
        
        # Check db messages length is now 3 (2 from previous, +1 new user message)
        result_all = await db.execute(select(Message).filter(Message.conversation_id == res_ai["conversation_id"]))
        all_msgs = list(result_all.scalars().all())
        assert len(all_msgs) == 3
        assert all_msgs[2].sender_type == MessageSenderType.USER
