import logging
import json
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from libs.infrastructure.database.models import AuditLog

logger = logging.getLogger("hiqonis.audit")

class HiqonisAuditLogService:
    """Enterprise Audit Logging system service for tracking platform actions."""

    async def log_action(
        self,
        db: AsyncSession,
        tenant_id: str,
        action: str,
        resource: str,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Optional[AuditLog]:
        """Logs an action performed on a resource by a user or system bot.

        Args:
            db: SQLAlchemy AsyncSession.
            tenant_id: The ID of the tenant.
            action: The action key (e.g., 'user.login', 'deal.won').
            resource: The table or resource type (e.g., 'users', 'deals').
            user_id: Optional database user ID who initiated the event.
            details: Optional metadata details dictionary to store as JSON text.
        """
        try:
            details_str = json.dumps(details) if details else None
            
            log_entry = AuditLog(
                tenant_id=tenant_id,
                user_id=user_id,
                action=action,
                resource=resource,
                details=details_str
            )
            
            db.add(log_entry)
            await db.flush()
            
            logger.info(f"AuditLog recorded: {action} on {resource} for tenant {tenant_id}")
            return log_entry
        except Exception as e:
            logger.exception(f"Failed to record audit log: {str(e)}")
            return None
