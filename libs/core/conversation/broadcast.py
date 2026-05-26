import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable, Coroutine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from libs.infrastructure.database.models import (
    Contact, Conversation, Message, ConversationStatus, MessageSenderType
)
from libs.integrations.channel_adapter import ChannelAdapter

logger = logging.getLogger("hiqonis.broadcast")

class HiqonisBroadcastService:
    """Enterprise broadcast campaign manager routing templates to multiple clients."""
    
    def __init__(
        self,
        on_message_callback: Optional[Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]] = None
    ):
        self.on_message_callback = on_message_callback

    async def send_broadcast_campaign(
        self,
        db: AsyncSession,
        tenant_id: str,
        contact_ids: List[str],
        template_name: str,
        language_code: str = "id",
        channel_adapters: Dict[str, ChannelAdapter] = None
    ) -> Dict[str, Any]:
        """Triggers a Meta-approved WhatsApp template campaign to multiple contacts.

        Args:
            db: SQLAlchemy AsyncSession.
            tenant_id: The ID of the tenant running the campaign.
            contact_ids: List of contact database IDs to receive the broadcast.
            template_name: Name of the WhatsApp Cloud API template.
            language_code: Language localization code (default: 'id' for Indonesian).
            channel_adapters: Active channel adapters.
        """
        if not channel_adapters or "whatsapp" not in channel_adapters:
            return {"status": "failed", "error": "WhatsApp channel adapter not configured."}
            
        wa_adapter = channel_adapters["whatsapp"]
        success_count = 0
        failed_contacts = []

        for cid in contact_ids:
            try:
                # 1. Fetch Contact
                result_c = await db.execute(select(Contact).filter(Contact.id == cid).filter(Contact.tenant_id == tenant_id))
                contact = result_c.scalars().first()
                
                if not contact or not contact.phone:
                    failed_contacts.append({"contact_id": cid, "reason": "Contact not found or lacks phone number."})
                    continue

                # 2. Find or create open conversation for this user on WhatsApp
                stmt_conv = (
                    select(Conversation)
                    .filter(Conversation.tenant_id == tenant_id)
                    .filter(Conversation.channel == "whatsapp")
                    .filter(Conversation.status == ConversationStatus.OPEN)
                )
                result_conv = await db.execute(stmt_conv)
                conv = result_conv.scalars().first()

                if not conv:
                    conv = Conversation(
                        tenant_id=tenant_id,
                        channel="whatsapp",
                        status=ConversationStatus.OPEN,
                        is_human_takeover=False
                    )
                    db.add(conv)
                    await db.flush()

                # 3. Deliver template message via adapter
                sent = await wa_adapter.send_template_message(
                    recipient_id=contact.phone,
                    template_name=template_name,
                    language_code=language_code
                )

                if sent:
                    # 4. Log broadcast message in DB
                    broadcast_msg = Message(
                        conversation_id=conv.id,
                        sender_id="hiqonis_broadcast_campaign",
                        sender_type=MessageSenderType.SYSTEM,
                        content=f"[Broadcast Campaign] Sent WhatsApp template: {template_name} ({language_code})"
                    )
                    db.add(broadcast_msg)
                    
                    # Trigger dashboard update
                    if self.on_message_callback:
                        await self.on_message_callback({
                            "conversation_id": conv.id,
                            "tenant_id": tenant_id,
                            "channel": "whatsapp",
                            "sender_id": "hiqonis_broadcast_campaign",
                            "sender_type": "system",
                            "content": f"[Broadcast Campaign] Sent template: {template_name}",
                            "is_human_takeover": conv.is_human_takeover
                        })
                        
                    success_count += 1
                else:
                    failed_contacts.append({"contact_id": cid, "reason": "Adapter failed to send template message."})
            except Exception as e:
                logger.exception(f"Error sending broadcast to contact {cid}: {str(e)}")
                failed_contacts.append({"contact_id": cid, "reason": str(e)})

        if success_count > 0:
            await db.commit()

        return {
            "status": "completed",
            "campaign_template": template_name,
            "success_count": success_count,
            "failed_count": len(failed_contacts),
            "failures": failed_contacts
        }
