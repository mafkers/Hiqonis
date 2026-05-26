import logging
import httpx
from typing import List, Dict, Any, Optional

from libs.integrations.channel_adapter import ChannelAdapter

logger = logging.getLogger("hiqonis.whatsapp")

class WhatsAppAdapter(ChannelAdapter):
    """Adapter for the official WhatsApp Business Cloud API (Meta)."""

    def __init__(self, token: str, phone_number_id: str):
        self.token = token
        self.phone_number_id = phone_number_id
        self.base_url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    async def send_text_message(self, recipient_id: str, text: str) -> bool:
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_id,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": text
            }
        }
        return await self._execute_request(payload)

    async def send_media_message(self, recipient_id: str, media_url: str, media_type: str) -> bool:
        # media_type can be: image, video, document, audio
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_id,
            "type": media_type,
            media_type: {
                "link": media_url
            }
        }
        return await self._execute_request(payload)

    async def send_template_message(
        self, 
        recipient_id: str, 
        template_name: str, 
        language_code: str, 
        components: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_id,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }
        if components:
            payload["template"]["components"] = components
            
        return await self._execute_request(payload)

    async def _execute_request(self, payload: Dict[str, Any]) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    self.base_url,
                    json=payload,
                    headers=self.headers,
                    timeout=10.0
                )
                if res.status_code in (200, 201):
                    logger.info(f"WhatsApp message successfully sent. Response: {res.json()}")
                    return True
                else:
                    logger.error(f"WhatsApp Cloud API error {res.status_code}: {res.text}")
                    return False
        except Exception as e:
            logger.exception(f"Exception during WhatsApp message transmission: {str(e)}")
            return False
