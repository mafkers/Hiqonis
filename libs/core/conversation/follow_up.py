import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, Coroutine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from libs.infrastructure.database.models import Conversation, Message, ConversationStatus, MessageSenderType
from libs.agents.chat_agent.agent import HiqonisChatAgent
from libs.integrations.channel_adapter import ChannelAdapter

logger = logging.getLogger("hiqonis.follow_up")

class HiqonisFollowUpService:
    """Enterprise follow-up and re-engagement automation service."""
    
    def __init__(
        self,
        chat_agent: HiqonisChatAgent,
        on_message_callback: Optional[Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]] = None
    ):
        self.chat_agent = chat_agent
        self.on_message_callback = on_message_callback

    async def trigger_automated_follow_ups(
        self,
        db: AsyncSession,
        tenant_id: str,
        channel_adapters: Dict[str, ChannelAdapter],
        idle_hours: float = 24.0
    ) -> int:
        """Find open idle conversations and automatically send AI follow-up reminders.

        Args:
            db: SQLAlchemy AsyncSession.
            tenant_id: The ID of the tenant.
            channel_adapters: Dictionary of active channel adapters.
            idle_hours: Number of hours a conversation has been idle before follow-up.
        """
        # Find open, non-takeover conversations
        stmt = (
            select(Conversation)
            .filter(Conversation.tenant_id == tenant_id)
            .filter(Conversation.status == ConversationStatus.OPEN)
            .filter(Conversation.is_human_takeover == False)
        )
        result = await db.execute(stmt)
        conversations = result.scalars().all()
        
        triggered_count = 0
        cutoff_time = datetime.utcnow() - timedelta(hours=idle_hours)

        for conv in conversations:
            # Query last message
            stmt_msg = (
                select(Message)
                .filter(Message.conversation_id == conv.id)
                .order_by(Message.timestamp.desc())
                .limit(1)
            )
            res_msg = await db.execute(stmt_msg)
            last_msg = res_msg.scalars().first()
            
            if not last_msg:
                continue

            # Check if conversation is idle based on last message timestamp
            if last_msg.timestamp <= cutoff_time:
                # Retrieve the full conversation thread to give context to the follow-up prompt
                stmt_all = (
                    select(Message)
                    .filter(Message.conversation_id == conv.id)
                    .order_by(Message.timestamp.asc())
                )
                res_all = await db.execute(stmt_all)
                all_msgs = res_all.scalars().all()
                
                thread_str = "\n".join([f"{m.sender_type.value}: {m.content}" for m in all_msgs])

                # Generate a personalized re-engagement message using ChatAgent
                follow_up_prompt = (
                    f"Here is the history of an idle conversation:\n\n{thread_str}\n\n"
                    "Generate a highly professional, friendly follow-up message in Bahasa Indonesia "
                    "to re-engage the customer. Remind them gently about our services or ask if they have any other questions. "
                    "Keep it short and polite (maximum 2-3 sentences)."
                )
                follow_up_text = await self.chat_agent.chat(follow_up_prompt)

                # Persist outgoing AI follow-up Message
                ai_msg = Message(
                    conversation_id=conv.id,
                    sender_id="hiqonis_followup_bot",
                    sender_type=MessageSenderType.AI,
                    content=follow_up_text
                )
                db.add(ai_msg)
                
                # Update conversation updated_at
                conv.updated_at = datetime.utcnow()
                await db.flush()

                # Send via adapter
                adapter = channel_adapters.get(conv.channel)
                if adapter:
                    # Resolve customer sender_id (we check first message from USER)
                    customer_msg = next((m for m in all_msgs if m.sender_type == MessageSenderType.USER), None)
                    if customer_msg:
                        logger.info(f"Sending automated follow-up to {customer_msg.sender_id} via {conv.channel}")
                        await adapter.send_text_message(recipient_id=customer_msg.sender_id, text=follow_up_text)

                # Trigger socket event
                if self.on_message_callback:
                    await self.on_message_callback({
                        "conversation_id": conv.id,
                        "tenant_id": tenant_id,
                        "channel": conv.channel,
                        "sender_id": "hiqonis_followup_bot",
                        "sender_type": "ai",
                        "content": follow_up_text,
                        "is_human_takeover": False
                    })
                
                triggered_count += 1

        if triggered_count > 0:
            await db.commit()

        return triggered_count
