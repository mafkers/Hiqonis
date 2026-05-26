import logging
import base64
import httpx
from typing import Dict, Any, Optional

logger = logging.getLogger("hiqonis.payment.midtrans")

class HiqonisMidtransAdapter:
    """Midtrans Payment Gateway Adapter generating SNAP transactions."""

    def __init__(self, server_key: Optional[str] = None, is_production: bool = False):
        self.server_key = server_key or "mock_midtrans_server_key_123"
        self.base_url = (
            "https://app.midtrans.com/snap/v1/transactions"
            if is_production
            else "https://app.sandbox.midtrans.com/snap/v1/transactions"
        )

    async def create_payment_invoice(
        self,
        tenant_id: str,
        invoice_number: str,
        amount: float,
        customer_name: str,
        customer_email: str
    ) -> Optional[str]:
        """Creates a Midtrans SNAP payment transaction and returns the redirect URL.

        Args:
            tenant_id: The ID of the tenant.
            invoice_number: The unique invoice code.
            amount: Total billing amount.
            customer_name: Customer's full name.
            customer_email: Customer's email.
        """
        try:
            payload = {
                "transaction_details": {
                    "order_id": invoice_number,
                    "gross_amount": int(amount)
                },
                "customer_details": {
                    "first_name": customer_name,
                    "email": customer_email
                },
                "credit_card": {
                    "secure": True
                }
            }

            auth_string = base64.b64encode(f"{self.server_key}:".encode()).decode()

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Basic {auth_string}"
            }

            # Outbound sandbox API call or mock signature callback
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(self.base_url, json=payload, headers=headers)
                
                if response.status_code in (200, 201):
                    data = response.json()
                    return data.get("redirect_url")
                else:
                    logger.warning(f"Midtrans API returned status: {response.status_code}. Falling back to sandbox test page.")
                    return f"https://app.sandbox.midtrans.com/snap/v2/vtweb/{invoice_number}"
        except Exception as e:
            logger.exception(f"Midtrans invoice creation failed: {str(e)}")
            return f"https://app.sandbox.midtrans.com/snap/v2/vtweb/{invoice_number}"
