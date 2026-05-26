import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from google.antigravity import Agent as AGYAgent, LocalAgentConfig
from sqlalchemy.future import select

from libs.infrastructure.database.session import AsyncSessionLocal
from libs.infrastructure.database.models import Appointment, AppointmentStatus

logger = logging.getLogger("hiqonis.appointment_agent")

# --- Define Appointment Tool Functions for Google Antigravity Agent ---

async def create_appointment_tool(
    tenant_id: str,
    contact_id: str,
    title: str,
    start_time: str,
    end_time: str,
    description: Optional[str] = None
) -> str:
    """Schedules a new appointment/meeting in the calendar database.

    Args:
        tenant_id: The ID of the tenant.
        contact_id: The ID of the contact/customer.
        title: The title/subject of the appointment.
        start_time: Start time of the meeting in ISO format (e.g. '2026-05-27T10:00:00').
        end_time: End time of the meeting in ISO format (e.g. '2026-05-27T11:00:00').
        description: Optional notes/details about the appointment.
    """
    try:
        # Standardize ISO formats
        st_clean = start_time.replace("Z", "+00:00")
        et_clean = end_time.replace("Z", "+00:00")
        start_dt = datetime.fromisoformat(st_clean)
        end_dt = datetime.fromisoformat(et_clean)
    except Exception as e:
        return f"Error: Invalid date format. Please use ISO 8601 format (e.g. YYYY-MM-DDTHH:MM:SS). Error: {str(e)}"

    if start_dt >= end_dt:
        return "Error: Start time must be before end time."

    async with AsyncSessionLocal() as db:
        try:
            # Create Appointment
            appt = Appointment(
                tenant_id=tenant_id,
                contact_id=contact_id,
                title=title,
                description=description,
                start_time=start_dt,
                end_time=end_dt,
                status=AppointmentStatus.SCHEDULED
            )
            db.add(appt)
            await db.commit()
            return f"Successfully scheduled appointment. Appointment ID: {appt.id}, Title: {title}, Start: {start_time}"
        except Exception as e:
            await db.rollback()
            logger.exception(f"Error in create_appointment_tool: {str(e)}")
            return f"Failed to schedule appointment: {str(e)}"

async def check_availability_tool(tenant_id: str, date_str: str) -> str:
    """Checks for existing appointments on a given day to find free slots.

    Args:
        tenant_id: The ID of the tenant.
        date_str: Date string in 'YYYY-MM-DD' format.
    """
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception as e:
        return "Error: Date must be in 'YYYY-MM-DD' format."

    async with AsyncSessionLocal() as db:
        try:
            # Get all appointments scheduled for that date
            result = await db.execute(select(Appointment).filter(Appointment.tenant_id == tenant_id))
            appts = result.scalars().all()
            
            # Filter in Python for simplicity and cross-DB (SQLite/Postgres) compatibility
            daily_appts = [a for a in appts if a.start_time.date() == target_date and a.status == AppointmentStatus.SCHEDULED]

            if not daily_appts:
                return f"No scheduled appointments on {date_str}. All slots are available!"

            response_lines = [f"Scheduled appointments on {date_str}:"]
            for a in sorted(daily_appts, key=lambda x: x.start_time):
                start = a.start_time.strftime("%H:%M")
                end = a.end_time.strftime("%H:%M")
                response_lines.append(f"- {start} - {end}: {a.title}")
            return "\n".join(response_lines)
        except Exception as e:
            logger.exception(f"Error checking availability: {str(e)}")
            return f"Failed to check availability: {str(e)}"

# --- Define the HiqonisAppointmentAgent Wrapper ---

class HiqonisAppointmentAgent:
    """AI Appointment Scheduling Agent driving calendar checks and smart booking."""
    
    def __init__(self, tenant_id: str, api_key: Optional[str] = None):
        self.tenant_id = tenant_id
        self.api_key = api_key
        self.system_instructions = (
            f"You are a calendar and scheduling assistant for tenant '{tenant_id}'. "
            "Your goal is to parse user conversations, check slot availability using 'check_availability_tool', "
            "and schedule appointments using 'create_appointment_tool'. "
            "Always verify availability first if a specific date is mentioned. "
            "Confirm the booking details (date, time, title) with the customer before concluding."
        )

    async def analyze_and_schedule(self, conversation_history: str, contact_id: str) -> str:
        """Analyze chat thread, check calendar slots, and book appointments."""
        config = LocalAgentConfig(
            system_instructions=self.system_instructions,
            tools=[create_appointment_tool, check_availability_tool],
            model="gemini-2.5-flash",
            api_key=self.api_key
        )
        async with AGYAgent(config=config) as agent:
            response = await agent.chat(
                f"Analyze this conversation thread for contact '{contact_id}' and schedule the appointment:\n\n{conversation_history}"
            )
            return await response.text()
