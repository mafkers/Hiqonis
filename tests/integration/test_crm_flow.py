import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.future import select

from libs.infrastructure.database.models import Base, Tenant, Contact, Lead, LeadStatus
from libs.agents.crm_agent.agent import HiqonisCRMAgent, create_or_update_contact_tool, score_and_qualify_lead_tool

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

# Monkeypatch the database session factory inside both the session module and the agent module
import libs.infrastructure.database.session as session_module
session_module.AsyncSessionLocal = TestSessionLocal

import libs.agents.crm_agent.agent as crm_agent_module
crm_agent_module.AsyncSessionLocal = TestSessionLocal

@pytest.mark.asyncio
async def test_crm_agent_database_tool_calling():
    # 1. Initialize tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with TestSessionLocal() as db:
        # 2. Setup mock Tenant
        tenant = Tenant(name="Hiqonis CRM Corp")
        db.add(tenant)
        await db.commit()
        
        # 3. Test create_or_update_contact_tool directly
        res_contact = await create_or_update_contact_tool(
            tenant_id=tenant.id,
            name="Alice Smith",
            email="alice@smith.com",
            phone="+62812345"
        )
        assert "Successfully created contact" in res_contact
        
        # Verify contact was saved in DB
        result_contact = await db.execute(select(Contact).filter(Contact.email == "alice@smith.com"))
        contact = result_contact.scalars().first()
        assert contact is not None
        assert contact.name == "Alice Smith"
        assert contact.phone == "+62812345"
        
        # 4. Test score_and_qualify_lead_tool directly
        res_lead = await score_and_qualify_lead_tool(
            tenant_id=tenant.id,
            contact_id=contact.id,
            score=90,
            status="qualified"
        )
        assert "Successfully created lead" in res_lead
        
        # Verify lead was saved in DB
        result_lead = await db.execute(select(Lead).filter(Lead.contact_id == contact.id))
        lead = result_lead.scalars().first()
        assert lead is not None
        assert lead.score == 90
        assert lead.status == LeadStatus.QUALIFIED
