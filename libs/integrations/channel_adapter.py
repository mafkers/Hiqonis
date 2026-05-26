from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class ChannelAdapter(ABC):
    """Abstract base class representing an external communication channel adapter."""

    @abstractmethod
    async def send_text_message(
        self, 
        recipient_id: str, 
        text: str
    ) -> bool:
        """Send a plain text message to the recipient on the channel."""
        pass

    @abstractmethod
    async def send_media_message(
        self, 
        recipient_id: str, 
        media_url: str, 
        media_type: str
    ) -> bool:
        """Send a media message (image, video, document) to the recipient."""
        pass

    @abstractmethod
    async def send_template_message(
        self, 
        recipient_id: str, 
        template_name: str, 
        language_code: str, 
        components: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Send a pre-approved template message (Meta official restriction)."""
        pass
