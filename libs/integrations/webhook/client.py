import logging
import json
import hmac
import hashlib
from typing import Dict, Any
import httpx

logger = logging.getLogger("hiqonis.webhook")

class HiqonisWebhookService:
    """Outbound Webhook system broadcasting signed events to external integrations."""

    async def dispatch_webhook_event(
        self,
        tenant_id: str,
        endpoint_url: str,
        signing_secret: str,
        event_type: str,
        payload: Dict[str, Any]
    ) -> bool:
        """Sends a cryptographically signed HMAC-SHA256 webhook event payload.

        Args:
            tenant_id: The ID of the tenant.
            endpoint_url: Third-party callback webhook URL.
            signing_secret: Webhook signature key.
            event_type: Trigger identifier (e.g. 'message.received', 'lead.qualified').
            payload: Body details dictionary to serialize and send.
        """
        try:
            full_body = {
                "tenant_id": tenant_id,
                "event": event_type,
                "data": payload
            }
            body_json = json.dumps(full_body)

            # Generate SHA256 signature using the secret key
            signature = hmac.new(
                signing_secret.encode("utf-8"),
                body_json.encode("utf-8"),
                hashlib.sha256
            ).hexdigest()

            headers = {
                "Content-Type": "application/json",
                "X-Hiqonis-Signature": signature,
                "X-Hiqonis-Event": event_type
            }

            # Outbound async POST request
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(endpoint_url, data=body_json, headers=headers)
                
                if response.is_success:
                    logger.info(f"Webhook event {event_type} dispatched successfully to {endpoint_url}")
                    return True
                else:
                    logger.error(f"Webhook delivery failed for {endpoint_url}. Status: {response.status_code}")
                    return False
        except Exception as e:
            logger.exception(f"Error during webhook dispatch to {endpoint_url}: {str(e)}")
            return False
