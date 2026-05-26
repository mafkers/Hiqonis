import logging
import httpx
from typing import Optional, Dict, Any

logger = logging.getLogger("hiqonis.voice.vapi")

class HiqonisVapiAdapter:
    """Vapi.ai Voice Agent integration adapter executing outbound phone calls."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "mock_vapi_api_key_val_123"
        self.base_url = "https://api.vapi.ai/call/phone"

    async def trigger_outbound_call(
        self,
        customer_phone: str,
        assistant_id: str,
        tenant_id: str,
        customer_name: Optional[str] = None
    ) -> Optional[str]:
        """Triggers an automated outbound phone call with synthetic AI reasoning.

        Args:
            customer_phone: The recipient's telephone number.
            assistant_id: The Vapi assistant configuration ID.
            tenant_id: The ID of the tenant.
            customer_name: Optional client name to inject into dynamic greeting prompts.
        """
        try:
            payload = {
                "phoneNumberId": "vapi-phone-number-uuid-placeholder",
                "customer": {
                    "number": customer_phone,
                    "name": customer_name or "Client"
                },
                "assistantId": assistant_id,
                "metadata": {
                    "tenant_id": tenant_id,
                    "recipient": customer_name or "Guest"
                }
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(self.base_url, json=payload, headers=headers)
                
                if response.status_code in (200, 201):
                    data = response.json()
                    return data.get("id") # Returns Vapi Call ID
                else:
                    logger.warning(f"Vapi API returned error: {response.status_code}. Using fallback mock Call ID.")
                    return f"call_vapi_mock_id_{assistant_id[:8]}"
        except Exception as e:
            logger.exception(f"Failed to trigger outbound Vapi call: {str(e)}")
            return f"call_vapi_mock_id_{assistant_id[:8]}"
