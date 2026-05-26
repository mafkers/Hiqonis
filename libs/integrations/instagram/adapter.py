import logging
import httpx
from typing import List, Dict, Any, Optional

from libs.integrations.channel_adapter import ChannelAdapter

logger = logging.getLogger("hiqonis.instagram")

class InstagramAdapter(ChannelAdapter):
    """Adapter for the official Instagram Graph API (Meta Messenger Platform)."""

    def __init__(self, page_access_token: str):
        self.token = page_access_token
        self.base_url = "https://graph.facebook.com/v19.0/me/messages"
        self.params = {
            "access_token": page_access_token
        }
        self.headers = {
            "Content-Type": "application/json"
        }

    async def send_text_message(self, recipient_id: str, text: str) -> bool:
        payload = {
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "text": text
            }
        }
        return await self._execute_request(payload)

    async def send_media_message(self, recipient_id: str, media_url: str, media_type: str) -> bool:
        # media_type can be: image, video, file
        payload = {
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "attachment": {
                    "type": media_type,
                    "payload": {
                        "url": media_url,
                        "is_reusable": True
                    }
                }
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
        # Instagram DM does not support official Meta template parameters.
        # Fallback: Send a notification message about the template triggering.
        text = f"[Notification Triggered: {template_name}]"
        return await self.send_text_message(recipient_id, text)

    async def _execute_request(self, payload: Dict[str, Any]) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    self.base_url,
                    json=payload,
                    params=self.params,
                    headers=self.headers,
                    timeout=10.0
                )
                if res.status_code in (200, 201):
                    logger.info(f"Instagram DM successfully sent. Response: {res.json()}")
                    return True
                else:
                    logger.error(f"Instagram Graph API error {res.status_code}: {res.text}")
                    return False
        except Exception as e:
            logger.exception(f"Exception during Instagram DM transmission: {str(e)}")
            return False
