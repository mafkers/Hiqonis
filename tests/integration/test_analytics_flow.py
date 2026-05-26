import pytest
import os
import shutil
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.future import select

from libs.infrastructure.database.models import (
    Base, Tenant, Conversation, Message, ConversationStatus, MessageSenderType,
    ConversationMetric, CSATSurvey
)
from libs.core.conversation.analytics import HiqonisAnalyticsService

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

# Monkeypatch database session factories for test execution
import libs.infrastructure.database.session as session_module
session_module.AsyncSessionLocal = TestSessionLocal

import libs.core.conversation.analytics as analytics_module
analytics_module.AsyncSessionLocal = TestSessionLocal

@pytest.mark.asyncio
async def test_analytics_and_csat_flow():
    # 1. Initialize tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as db:
        # 2. Setup mock Tenant
        tenant = Tenant(name="Hiqonis Analytics Corp")
        db.add(tenant)
        await db.flush()

        # 3. Create simulated Conversation session
        # Start: 3 minutes ago
        start_time = datetime.utcnow() - timedelta(minutes=3)
        conv = Conversation(
            tenant_id=tenant.id,
            channel="whatsapp",
            status=ConversationStatus.OPEN,
            is_human_takeover=False,
            created_at=start_time,
            updated_at=start_time
        )
        db.add(conv)
        await db.flush()

        # Message 1: Customer (User) at start_time
        m1 = Message(
            conversation_id=conv.id,
            sender_id="customer_1",
            sender_type=MessageSenderType.USER,
            content="Halo, apakah saya bisa memesan produk A?",
            timestamp=start_time
        )
        db.add(m1)

        # Message 2: AI reply after 60 seconds (first response time)
        reply_time = start_time + timedelta(seconds=60)
        m2 = Message(
            conversation_id=conv.id,
            sender_id="hiqonis_ai",
            sender_type=MessageSenderType.AI,
            content="Tentu bisa! Silakan sebutkan jumlahnya.",
            timestamp=reply_time
        )
        db.add(m2)

        # Message 3: Customer response after 90 seconds
        m3 = Message(
            conversation_id=conv.id,
            sender_id="customer_1",
            sender_type=MessageSenderType.USER,
            content="Saya mau beli 2 pcs.",
            timestamp=start_time + timedelta(seconds=90)
        )
        db.add(m3)

        # Message 4: AI response after 120 seconds
        m4 = Message(
            conversation_id=conv.id,
            sender_id="hiqonis_ai",
            sender_type=MessageSenderType.AI,
            content="Pesanan dicatat. Silakan cek invoice di chat.",
            timestamp=start_time + timedelta(seconds=120)
        )
        db.add(m4)

        # Mark conversation as RESOLVED after 180 seconds (resolution time)
        resolution_time = start_time + timedelta(seconds=180)
        conv.status = ConversationStatus.RESOLVED
        conv.updated_at = resolution_time
        await db.commit()

        # --- A. Test Metrics Calculation ---
        analytics_service = HiqonisAnalyticsService()
        metric = await analytics_service.calculate_and_save_metrics(db=db, conversation_id=conv.id)
        
        assert metric is not None
        assert metric.message_count == 4
        assert metric.ai_message_count == 2
        assert metric.human_message_count == 0
        assert metric.first_response_time_seconds == 60.0
        assert metric.resolution_time_seconds == 180.0

        # Verify saved in DB
        result_m = await db.execute(select(ConversationMetric).filter(ConversationMetric.conversation_id == conv.id))
        db_metric = result_m.scalars().first()
        assert db_metric is not None
        assert db_metric.first_response_time_seconds == 60.0

        # --- B. Test CSAT Survey Submission ---
        csat = await analytics_service.submit_csat_survey(
            db=db,
            conversation_id=conv.id,
            rating=5,
            feedback="Pelayanan AI sangat cepat!"
        )
        assert csat is not None
        assert csat.rating == 5
        assert csat.feedback == "Pelayanan AI sangat cepat!"

        # Verify rating constraint validation
        with pytest.raises(ValueError, match="CSAT rating must be between 1 and 5"):
            await analytics_service.submit_csat_survey(db=db, conversation_id=conv.id, rating=6)

        # --- C. Test Tenant Analytics Summary (Dashboard API) ---
        summary = await analytics_service.get_tenant_analytics_summary(db=db, tenant_id=tenant.id)
        assert summary["csat"]["average_rating"] == 5.0
        assert summary["csat"]["total_surveys"] == 1
        assert summary["csat"]["distribution"][5] == 1
        assert summary["performance"]["average_first_response_seconds"] == 60.0
        assert summary["performance"]["average_resolution_seconds"] == 180.0
        assert summary["performance"]["total_messages"] == 4
        assert summary["performance"]["ai_messages"] == 2
        assert summary["efficiency"]["ai_resolution_rate_percent"] == 100.0

        # --- D. Test Export & Reporting (CSV Export) ---
        csv_path = await analytics_service.generate_csv_report(db=db, tenant_id=tenant.id)
        expected_path = f"/home/momo/Dokumen/Insyaallah Sukses/storage/reports/analytics_report_{tenant.id}.csv"
        assert csv_path == expected_path
        assert os.path.exists(expected_path)

        with open(expected_path, "r") as f:
            lines = f.readlines()
            # Verify header is written
            assert "Conversation ID" in lines[0]
            assert "First Response Time" in lines[0]
            # Verify record values
            assert conv.id in lines[1]
            assert "60.00" in lines[1]
            assert "180.00" in lines[1]

        # Clean up generated CSV file
        if os.path.exists(expected_path):
            os.remove(expected_path)
