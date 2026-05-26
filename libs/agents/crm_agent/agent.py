import logging
from typing import Optional, List, Dict, Any
from google.antigravity import Agent as AGYAgent, LocalAgentConfig
from sqlalchemy.future import select

from libs.infrastructure.database.session import AsyncSessionLocal
from libs.infrastructure.database.models import Contact, Lead, LeadStatus, Deal, DealStage

logger = logging.getLogger("hiqonis.crm_agent")

# --- Define CRM Tool Functions for Google Antigravity Agent ---

async def create_or_update_contact_tool(
    tenant_id: str, 
    name: str, 
    email: Optional[str] = None, 
    phone: Optional[str] = None
) -> str:
    """Creates a new contact or updates an existing contact's details in the CRM.

    Args:
        tenant_id: The ID of the tenant/business owner.
        name: Full name of the contact.
        email: Email address (optional).
        phone: Phone number (optional).
    """
    async with AsyncSessionLocal() as db:
        try:
            # Check if contact already exists by email (if provided)
            contact = None
            if email:
                result = await db.execute(select(Contact).filter(Contact.email == email).filter(Contact.tenant_id == tenant_id))
                contact = result.scalars().first()
                
            if not contact:
                contact = Contact(tenant_id=tenant_id, name=name, email=email, phone=phone)
                db.add(contact)
                await db.flush()
                action = "created"
            else:
                contact.name = name
                if phone:
                    contact.phone = phone
                action = "updated"

            await db.commit()
            return f"Successfully {action} contact. Contact ID: {contact.id}"
        except Exception as e:
            await db.rollback()
            logger.exception(f"Error in create_or_update_contact_tool: {str(e)}")
            return f"Failed to modify contact: {str(e)}"

async def score_and_qualify_lead_tool(
    tenant_id: str,
    contact_id: str,
    score: int,
    status: str
) -> str:
    """Scores a lead (0-100) and marks its qualification status (new, qualified, lost).

    Args:
        tenant_id: The ID of the tenant.
        contact_id: The ID of the contact.
        score: Score integer from 0 to 100.
        status: The qualification status. Must be one of: 'new', 'qualified', 'lost'.
    """
    if status not in ("new", "qualified", "lost"):
        return "Error: Invalid status value. Must be 'new', 'qualified', or 'lost'."
        
    async with AsyncSessionLocal() as db:
        try:
            # Check if lead already exists for this contact
            result = await db.execute(select(Lead).filter(Lead.contact_id == contact_id))
            lead = result.scalars().first()
            
            lead_status = LeadStatus(status)
            if not lead:
                lead = Lead(
                    tenant_id=tenant_id,
                    contact_id=contact_id,
                    status=lead_status,
                    score=score
                )
                db.add(lead)
                await db.flush()
                action = "created"
            else:
                lead.status = lead_status
                lead.score = score
                action = "updated"
                
            await db.commit()
            return f"Successfully {action} lead. Lead ID: {lead.id}, Score: {score}, Status: {status}"
        except Exception as e:
            await db.rollback()
            logger.exception(f"Error in score_and_qualify_lead_tool: {str(e)}")
            return f"Failed to score lead: {str(e)}"

# --- Define the CRMAgent Wrapper ---

class HiqonisCRMAgent:
    """AI CRM Agent driving lead capturing, scoring, and workflow updates."""
    
    def __init__(self, tenant_id: str, api_key: Optional[str] = None):
        self.tenant_id = tenant_id
        self.api_key = api_key
        self.system_instructions = (
            f"You are a sales and CRM assistant for tenant '{tenant_id}'. "
            "Your goal is to parse user conversations, extract contact profiles (name, email, phone), "
            "and automatically register or update them in the CRM database using the 'create_or_update_contact_tool'. "
            "If the customer expresses strong purchasing intent or asks for a proposal, score the lead (0-100) "
            "and qualify them using the 'score_and_qualify_lead_tool' with status='qualified'. "
            "Always be helpful, professional, and execute tools when sufficient data is collected."
        )

    async def analyze_and_qualify(self, conversation_history: str) -> str:
        """Run the CRM agent turn on a compiled conversation thread to auto-update the pipeline."""
        config = LocalAgentConfig(
            system_instructions=self.system_instructions,
            tools=[create_or_update_contact_tool, score_and_qualify_lead_tool],
            model="gemini-2.5-flash",
            api_key=self.api_key
        )
        async with AGYAgent(config=config) as agent:
            response = await agent.chat(
                f"Analyze this conversation thread and update the CRM records accordingly:\n\n{conversation_history}"
            )
            return await response.text()
