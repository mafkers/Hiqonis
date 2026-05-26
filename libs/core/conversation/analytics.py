import logging
import csv
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from libs.infrastructure.database.models import (
    Conversation, Message, ConversationStatus, MessageSenderType,
    ConversationMetric, CSATSurvey
)

logger = logging.getLogger("hiqonis.analytics")

class HiqonisAnalyticsService:
    """Enterprise Analytics & CSAT Reporting engine compiling CX metrics."""

    async def calculate_and_save_metrics(self, db: AsyncSession, conversation_id: str) -> Optional[ConversationMetric]:
        """Calculates performance metrics for a conversation and persists them.

        Metrics calculated:
        - Total message count
        - AI-generated reply count
        - Human-agent reply count
        - First response time (seconds since initial user message)
        - Resolution time (seconds since initial user message to resolution)
        """
        try:
            # 1. Fetch conversation
            result_conv = await db.execute(select(Conversation).filter(Conversation.id == conversation_id))
            conv = result_conv.scalars().first()
            if not conv:
                logger.error(f"Conversation {conversation_id} not found for metrics calculation.")
                return None

            # 2. Fetch all messages ordered by timestamp asc
            stmt_msgs = (
                select(Message)
                .filter(Message.conversation_id == conversation_id)
                .order_by(Message.timestamp.asc())
            )
            result_msgs = await db.execute(stmt_msgs)
            messages = list(result_msgs.scalars().all())

            if not messages:
                return None

            # 3. Compute counters
            total_msg = len(messages)
            ai_msg_count = sum(1 for m in messages if m.sender_type == MessageSenderType.AI)
            human_msg_count = sum(1 for m in messages if m.sender_type == MessageSenderType.AGENT)

            # 4. Compute First Response Time (FRT)
            first_user_msg = next((m for m in messages if m.sender_type == MessageSenderType.USER), None)
            first_reply = next((m for m in messages if m.sender_type in (MessageSenderType.AI, MessageSenderType.AGENT)), None)

            first_response_time = None
            if first_user_msg and first_reply and first_reply.timestamp > first_user_msg.timestamp:
                first_response_time = (first_reply.timestamp - first_user_msg.timestamp).total_seconds()

            # 5. Compute Resolution Time (RT)
            resolution_time = None
            if conv.status == ConversationStatus.RESOLVED and first_user_msg:
                # If resolved, calculate time delta from first user message to conversation updated_at
                if conv.updated_at > first_user_msg.timestamp:
                    resolution_time = (conv.updated_at - first_user_msg.timestamp).total_seconds()

            # 6. Save or Update in DB
            stmt_metric = select(ConversationMetric).filter(ConversationMetric.conversation_id == conversation_id)
            result_metric = await db.execute(stmt_metric)
            metric = result_metric.scalars().first()

            if not metric:
                metric = ConversationMetric(
                    tenant_id=conv.tenant_id,
                    conversation_id=conversation_id,
                    first_response_time_seconds=first_response_time,
                    resolution_time_seconds=resolution_time,
                    message_count=total_msg,
                    ai_message_count=ai_msg_count,
                    human_message_count=human_msg_count
                )
                db.add(metric)
            else:
                metric.first_response_time_seconds = first_response_time
                metric.resolution_time_seconds = resolution_time
                metric.message_count = total_msg
                metric.ai_message_count = ai_msg_count
                metric.human_message_count = human_msg_count
                metric.updated_at = datetime.utcnow()

            await db.flush()
            return metric
        except Exception as e:
            logger.exception(f"Error compiling conversation metrics: {str(e)}")
            return None

    async def submit_csat_survey(
        self,
        db: AsyncSession,
        conversation_id: str,
        rating: int,
        feedback: Optional[str] = None
    ) -> Optional[CSATSurvey]:
        """Submits customer feedback rating (1 to 5 stars) for a conversation.

        Args:
            db: SQLAlchemy AsyncSession.
            conversation_id: The ID of the conversation.
            rating: Satisfaction score from 1 to 5.
            feedback: Optional text comments.
        """
        if rating < 1 or rating > 5:
            raise ValueError("CSAT rating must be between 1 and 5.")

        try:
            # Query conversation to get tenant_id
            result_conv = await db.execute(select(Conversation).filter(Conversation.id == conversation_id))
            conv = result_conv.scalars().first()
            if not conv:
                logger.error(f"Conversation {conversation_id} not found for CSAT survey.")
                return None

            csat = CSATSurvey(
                tenant_id=conv.tenant_id,
                conversation_id=conversation_id,
                rating=rating,
                feedback=feedback
            )
            db.add(csat)
            await db.flush()
            return csat
        except Exception as e:
            logger.exception(f"Error submitting CSAT survey: {str(e)}")
            return None

    async def get_tenant_analytics_summary(self, db: AsyncSession, tenant_id: str) -> Dict[str, Any]:
        """Aggregates all performance and CSAT metrics for a tenant's analytics dashboard."""
        try:
            # 1. CSAT Averages
            stmt_csat = select(func.avg(CSATSurvey.rating), func.count(CSATSurvey.id)).filter(CSATSurvey.tenant_id == tenant_id)
            res_csat = await db.execute(stmt_csat)
            avg_rating, total_ratings = res_csat.first() or (0.0, 0)
            avg_rating = float(avg_rating or 0.0)

            # Rating distribution
            rating_dist = {i: 0 for i in range(1, 6)}
            stmt_dist = select(CSATSurvey.rating, func.count(CSATSurvey.id)).filter(CSATSurvey.tenant_id == tenant_id).group_by(CSATSurvey.rating)
            res_dist = await db.execute(stmt_dist)
            for rating_val, cnt in res_dist.all():
                rating_dist[rating_val] = cnt

            # 2. Performance Metrics
            stmt_metrics = (
                select(
                    func.avg(ConversationMetric.first_response_time_seconds),
                    func.avg(ConversationMetric.resolution_time_seconds),
                    func.sum(ConversationMetric.message_count),
                    func.sum(ConversationMetric.ai_message_count),
                    func.sum(ConversationMetric.human_message_count),
                    func.count(ConversationMetric.id)
                )
                .filter(ConversationMetric.tenant_id == tenant_id)
            )
            res_metrics = await db.execute(stmt_metrics)
            avg_frt, avg_rt, total_msgs, total_ai, total_human, total_convs = res_metrics.first() or (0.0, 0.0, 0, 0, 0, 0)

            # AI resolution rate vs Human handoff resolution rate
            stmt_resolutions = (
                select(Conversation.is_human_takeover, func.count(Conversation.id))
                .filter(Conversation.tenant_id == tenant_id)
                .filter(Conversation.status == ConversationStatus.RESOLVED)
                .group_by(Conversation.is_human_takeover)
            )
            res_res = await db.execute(stmt_resolutions)
            ai_resolutions = 0
            human_resolutions = 0
            for takeover, count in res_res.all():
                if takeover:
                    human_resolutions = count
                else:
                    ai_resolutions = count

            total_resolutions = ai_resolutions + human_resolutions
            ai_resolution_rate = (ai_resolutions / total_resolutions * 100.0) if total_resolutions > 0 else 0.0

            return {
                "tenant_id": tenant_id,
                "csat": {
                    "average_rating": round(avg_rating, 2),
                    "total_surveys": total_ratings,
                    "distribution": rating_dist
                },
                "performance": {
                    "average_first_response_seconds": round(float(avg_frt or 0.0), 2),
                    "average_resolution_seconds": round(float(avg_rt or 0.0), 2),
                    "total_conversations_tracked": total_convs,
                    "total_messages": int(total_msgs or 0),
                    "ai_messages": int(total_ai or 0),
                    "human_messages": int(total_human or 0)
                },
                "efficiency": {
                    "ai_resolutions": ai_resolutions,
                    "human_resolutions": human_resolutions,
                    "ai_resolution_rate_percent": round(ai_resolution_rate, 2)
                }
            }
        except Exception as e:
            logger.exception(f"Error fetching tenant analytics summary: {str(e)}")
            return {}

    async def generate_csv_report(self, db: AsyncSession, tenant_id: str) -> str:
        """Exports detailed conversation metrics as a CSV file and stores it locally.

        Returns:
            The absolute path of the generated CSV file.
        """
        try:
            # Query all conversation metrics with conversation channel/status details
            stmt = (
                select(
                    Conversation.id,
                    Conversation.channel,
                    Conversation.status,
                    Conversation.is_human_takeover,
                    ConversationMetric.first_response_time_seconds,
                    ConversationMetric.resolution_time_seconds,
                    ConversationMetric.message_count,
                    ConversationMetric.ai_message_count,
                    ConversationMetric.human_message_count,
                    Conversation.created_at
                )
                .join(ConversationMetric, Conversation.id == ConversationMetric.conversation_id)
                .filter(Conversation.tenant_id == tenant_id)
                .order_by(Conversation.created_at.desc())
            )
            result = await db.execute(stmt)
            records = result.all()

            storage_dir = "/home/momo/Dokumen/Insyaallah Sukses/storage/reports"
            os.makedirs(storage_dir, exist_ok=True)
            file_path = os.path.join(storage_dir, f"analytics_report_{tenant_id}.csv")

            with open(file_path, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                # Header
                writer.writerow([
                    "Conversation ID",
                    "Channel",
                    "Status",
                    "Human Handoff Active",
                    "First Response Time (sec)",
                    "Resolution Time (sec)",
                    "Total Messages",
                    "AI Message Count",
                    "Human Agent Message Count",
                    "Date Created"
                ])

                for rec in records:
                    writer.writerow([
                        rec[0],
                        rec[1],
                        rec[2].value if isinstance(rec[2], ConversationStatus) else rec[2],
                        "Yes" if rec[3] else "No",
                        f"{rec[4]:.2f}" if rec[4] is not None else "N/A",
                        f"{rec[5]:.2f}" if rec[5] is not None else "N/A",
                        rec[6],
                        rec[7],
                        rec[8],
                        rec[9].strftime("%Y-%m-%d %H:%M:%S")
                    ])

            return file_path
        except Exception as e:
            logger.exception(f"Error generating CSV analytics report: {str(e)}")
            raise e
