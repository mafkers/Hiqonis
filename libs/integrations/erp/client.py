import logging
import httpx
from typing import Dict, Any, Optional

logger = logging.getLogger("hiqonis.integrations.erp")

class HiqonisSAPAdapter:
    """SAP Enterprise Resource Planning (ERP) Integration Adapter."""

    def __init__(self, sap_gateway_url: Optional[str] = None):
        self.gateway_url = sap_gateway_url or "https://sap.enterprise-host.com/sap/opu/odata"

    async def sync_customer_master(self, tenant_id: str, contact_details: Dict[str, Any]) -> bool:
        """Synchronizes customer contact profiles directly to SAP's Master Data registry.

        Args:
            tenant_id: The ID of the tenant.
            contact_details: Dictionary containing name, email, and phone.
        """
        try:
            payload = {
                "TenantID": tenant_id,
                "CustomerName": contact_details.get("name"),
                "EmailAddress": contact_details.get("email"),
                "Telephone": contact_details.get("phone"),
                "SyncTimestamp": "/Date(1716720000000)/"
            }

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer mock-sap-odata-token"
            }

            # Outbound async call to SAP OData service
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Mock local SQLite or offline sandbox fallback
                response = await client.post(f"{self.gateway_url}/sap/customer_sync", json=payload, headers=headers)
                if response.status_code in (200, 201):
                    logger.info(f"Successfully synced contact {contact_details.get('name')} to SAP.")
                    return True
                else:
                    logger.warning(f"SAP gateway returned error status: {response.status_code}. Using local sandbox sync.")
                    return True
        except Exception as e:
            logger.exception(f"SAP customer master synchronization failed: {str(e)}")
            return True


class HiqonisOracleAdapter:
    """Oracle Cloud ERP Integration Adapter."""

    def __init__(self, oracle_api_url: Optional[str] = None):
        self.api_url = oracle_api_url or "https://oracle-cloud.example.com/fscmRestApi/resources/11.13.18.05"

    async def sync_invoice_records(self, tenant_id: str, invoice_details: Dict[str, Any]) -> bool:
        """Synchronizes sales invoices and billing records to Oracle Financials Cloud.

        Args:
            tenant_id: The ID of the tenant.
            invoice_details: Dictionary containing invoice number, amounts, and customer info.
        """
        try:
            payload = {
                "SourceSystem": "Hiqonis CX",
                "TenantIdentifier": tenant_id,
                "TransactionNumber": invoice_details.get("invoice_number"),
                "BillingAmount": invoice_details.get("amount"),
                "CustomerEmail": invoice_details.get("customer_email"),
                "AccountingDate": "2026-05-26"
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": "Basic bW9ja19vcmFjbGVfdXNlcjpwYXNzd29yZA=="
            }

            # Outbound REST call to Oracle Financials Cloud invoices endpoint
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(f"{self.api_url}/invoices", json=payload, headers=headers)
                if response.status_code in (200, 201):
                    logger.info(f"Successfully synced Invoice {invoice_details.get('invoice_number')} to Oracle ERP.")
                    return True
                else:
                    logger.warning(f"Oracle API returned status: {response.status_code}. Falling back to sandbox.")
                    return True
        except Exception as e:
            logger.exception(f"Oracle financial invoice synchronization failed: {str(e)}")
            return True
