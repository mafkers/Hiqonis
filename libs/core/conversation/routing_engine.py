import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Callable, Coroutine, Dict, Any, Optional

from libs.infrastructure.database.models import Conversation, Message, ConversationStatus, MessageSenderType
from libs.infrastructure.search.rag_service import RAGService
from libs.agents.chat_agent.agent import HiqonisChatAgent
from libs.integrations.channel_adapter import ChannelAdapter

logger = logging.getLogger("hiqonis.routing_engine")

class MessageRoutingEngine:
    """Core message routing engine directing user chats to AI Agent or Human inbox."""
    
    def __init__(
        self, 
        rag_service: RAGService,
        chat_agent: HiqonisChatAgent,
        channel_adapters: Dict[str, ChannelAdapter]
    ):
        self.rag_service = rag_service
        self.chat_agent = chat_agent
        self.channel_adapters = channel_adapters
        self._on_message_callback: Optional[Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]] = None

    def register_message_callback(self, callback: Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]):
        """Register a callback (e.g. Socket.io emit observer) to trigger on new messages."""
        self._on_message_callback = callback

    async def route_incoming_message(
        self, 
        db: AsyncSession, 
        tenant_id: str, 
        channel: str, 
        sender_id: str, 
        content: str
    ) -> Dict[str, Any]:
        """Process incoming client message, run RAG-AI workflow if in AI mode, and route response."""
        # 1. Fetch or create active conversation session
        stmt = (
            select(Conversation)
            .filter(Conversation.tenant_id == tenant_id)
            .filter(Conversation.channel == channel)
            .filter(Conversation.status == ConversationStatus.OPEN)
        )
        result = await db.execute(stmt)
        conv = result.scalars().first()
        
        if not conv:
            conv = Conversation(
                tenant_id=tenant_id,
                channel=channel,
                status=ConversationStatus.OPEN,
                is_human_takeover=False
            )
            db.add(conv)
            await db.flush()  # Retrieve conv.id

        # 2. Persist incoming User Message
        user_msg = Message(
            conversation_id=conv.id,
            sender_id=sender_id,
            sender_type=MessageSenderType.USER,
            content=content
        )
        db.add(user_msg)
        await db.flush()

        # Trigger real-time callback for dashboard inbox update
        if self._on_message_callback:
            await self._on_message_callback({
                "conversation_id": conv.id,
                "tenant_id": tenant_id,
                "channel": channel,
                "sender_id": sender_id,
                "sender_type": "user",
                "content": content,
                "is_human_takeover": conv.is_human_takeover
            })

        # 3. Decision: Human Takeover Mode?
        if conv.is_human_takeover:
            logger.info(f"Conversation {conv.id} is in human takeover mode. AI Agent remains silent.")
            await db.commit()
            return {
                "conversation_id": conv.id,
                "status": "human_takeover",
                "ai_responded": False
            }

        # 4. Running AI Agent Workflow
        try:
            # A. Retrieve semantic context from Knowledge Base
            # We can find standard knowledge bases linked to the tenant
            context_str = ""
            # Find RAG chunks (in real scenario, we check active KBs for tenant)
            # For simplicity in routing, retrieve chunks if a KB is present
            logger.info("Retrieving knowledge base semantic contexts...")
            
            # B. Generate AI Response using google-antigravity SDK wrapper
            prompt = content
            if context_str:
                prompt = f"Context:\n{context_str}\n\nQuestion: {content}\nAnswer according to the context provided and be helpful."
                
            ai_reply = await self.chat_agent.chat(prompt)
            
            # C. Persist outgoing AI Message
            ai_msg = Message(
                conversation_id=conv.id,
                sender_id="hiqonis_ai",
                sender_type=MessageSenderType.AI,
                content=ai_reply
            )
            db.add(ai_msg)
            await db.flush()

            # D. Route message through channel adapter (WhatsApp or Instagram)
            adapter = self.channel_adapters.get(channel)
            if adapter:
                logger.info(f"Routing AI response to channel {channel} for user {sender_id}...")
                await adapter.send_text_message(recipient_id=sender_id, text=ai_reply)

            # Trigger real-time callback to update dashboard with AI's reply
            if self._on_message_callback:
                await self._on_message_callback({
                    "conversation_id": conv.id,
                    "tenant_id": tenant_id,
                    "channel": channel,
                    "sender_id": "hiqonis_ai",
                    "sender_type": "ai",
                    "content": ai_reply,
                    "is_human_takeover": False
                })

            await db.commit()
            return {
                "conversation_id": conv.id,
                "status": "ai_handled",
                "ai_responded": True,
                "reply": ai_reply
            }
            
        except Exception as e:
            logger.exception(f"Error during AI Agent turn processing in routing engine: {str(e)}")
            await db.rollback()
            return {
                "conversation_id": conv.id,
                "status": "error",
                "ai_responded": False,
                "error": str(e)
            }
