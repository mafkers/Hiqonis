import pytest
import json
import hmac
import hashlib
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.future import select

from libs.infrastructure.database.models import Base, Tenant, User, AuditLog
from libs.core.shared.audit import HiqonisAuditLogService
from libs.integrations.webhook.client import HiqonisWebhookService

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

import libs.core.shared.audit as audit_module
audit_module.AsyncSessionLocal = TestSessionLocal

@pytest.mark.asyncio
async def test_enterprise_audit_logging():
    # 1. Initialize tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as db:
        # 2. Setup mock Tenant & User
        tenant = Tenant(name="Hiqonis Enterprise LLC")
        db.add(tenant)
        await db.flush()

        user = User(
            tenant_id=tenant.id,
            email="admin@enterprise.com",
            hashed_password="scrypt:mocked_pass",
            full_name="Enterprise Admin",
            role="tenant_admin"
        )
        db.add(user)
        await db.commit()

        # 3. Test HiqonisAuditLogService
        audit_service = HiqonisAuditLogService()
        log_entry = await audit_service.log_action(
            db=db,
            tenant_id=tenant.id,
            action="user.login",
            resource="users",
            user_id=user.id,
            details={"ip_address": "127.0.0.1", "device": "Chrome Web"}
        )

        assert log_entry is not None
        assert log_entry.action == "user.login"
        assert log_entry.resource == "users"

        # Verify saved in DB
        result_log = await db.execute(select(AuditLog).filter(AuditLog.id == log_entry.id))
        db_log = result_log.scalars().first()
        assert db_log is not None
        assert db_log.user_id == user.id
        
        # Verify JSON decoding
        details = json.loads(db_log.details)
        assert details["ip_address"] == "127.0.0.1"


@pytest.mark.asyncio
async def test_enterprise_signed_webhooks(monkeypatch):
    webhook_service = HiqonisWebhookService()
    
    tenant_id = "test-tenant-uuid"
    endpoint_url = "https://external-api.com/callback"
    signing_secret = "hiqonis_webhook_secret_key_123"
    event_type = "lead.qualified"
    payload = {"lead_id": "lead-999", "score": 95}

    # Intercept httpx.AsyncClient.post to verify parameters and hmac headers
    captured_requests = []
    
    class MockResponse:
        def __init__(self, status_code):
            self.status_code = status_code
            self.is_success = status_code == 200

    async def mock_post(self, url, data, headers):
        captured_requests.append({
            "url": url,
            "data": data,
            "headers": headers
        })
        return MockResponse(200)

    import httpx
    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    # Dispatch event
    success = await webhook_service.dispatch_webhook_event(
        tenant_id=tenant_id,
        endpoint_url=endpoint_url,
        signing_secret=signing_secret,
        event_type=event_type,
        payload=payload
    )

    assert success is True
    assert len(captured_requests) == 1
    
    req = captured_requests[0]
    assert req["url"] == endpoint_url
    assert req["headers"]["X-Hiqonis-Event"] == event_type
    
    # Verify HMAC-SHA256 signature
    sent_sig = req["headers"]["X-Hiqonis-Signature"]
    body_data = req["data"]
    
    expected_sig = hmac.new(
        signing_secret.encode("utf-8"),
        body_data.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    assert sent_sig == expected_sig
