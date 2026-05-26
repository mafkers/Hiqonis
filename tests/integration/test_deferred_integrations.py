import pytest
from libs.integrations.payment.midtrans_adapter import HiqonisMidtransAdapter
from libs.integrations.voice.vapi_adapter import HiqonisVapiAdapter
from libs.integrations.voice.advanced_features import HiqonisAdvancedVoiceService
from libs.integrations.shopee.client import HiqonisShopeeClient
from libs.integrations.tokopedia.client import HiqonisTokopediaClient
from libs.integrations.erp.client import HiqonisSAPAdapter, HiqonisOracleAdapter

@pytest.mark.asyncio
async def test_midtrans_payment_integration():
    adapter = HiqonisMidtransAdapter()
    redirect_url = await adapter.create_payment_invoice(
        tenant_id="test-tenant-uuid",
        invoice_number="INV-123456",
        amount=250000.0,
        customer_name="Momo",
        customer_email="momo@example.com"
    )
    assert redirect_url is not None
    assert "sandbox.midtrans.com" in redirect_url
    assert "INV-123456" in redirect_url

@pytest.mark.asyncio
async def test_vapi_voice_integration():
    adapter = HiqonisVapiAdapter()
    call_id = await adapter.trigger_outbound_call(
        customer_phone="+6281111",
        assistant_id="asst-999-default",
        tenant_id="test-tenant-uuid",
        customer_name="Momo"
    )
    assert call_id is not None
    assert "call_vapi_mock_id_" in call_id or len(call_id) > 5

@pytest.mark.asyncio
async def test_shopee_marketplace_integration():
    client = HiqonisShopeeClient()
    order_details = await client.get_shopee_order_status(
        shop_id=777,
        order_sn="260526MOCKSHP"
    )
    assert order_details is not None
    assert order_details["order_sn"] == "260526MOCKSHP"
    assert order_details["status"] in ("COMPLETED", "SHIPPED")
    assert "tracking_number" in order_details

@pytest.mark.asyncio
async def test_tokopedia_marketplace_integration():
    client = HiqonisTokopediaClient()
    order_details = await client.get_tokopedia_order_status(
        shop_id=888,
        order_id="260526MOCKTKP"
    )
    assert order_details is not None
    assert order_details["order_id"] == "260526MOCKTKP"
    assert order_details["status"] in ("DELIVERED", "PROCESSED")
    assert "logistics" in order_details

@pytest.mark.asyncio
async def test_erp_systems_integrations():
    sap = HiqonisSAPAdapter()
    oracle = HiqonisOracleAdapter()

    # Test SAP Master Data Customer Sync
    success_sap = await sap.sync_customer_master(
        tenant_id="test-tenant-uuid",
        contact_details={"name": "Alice Cooper", "email": "alice@cooper.com", "phone": "+62877"}
    )
    assert success_sap is True

    # Test Oracle Financials Invoice Sync
    success_oracle = await oracle.sync_invoice_records(
        tenant_id="test-tenant-uuid",
        invoice_details={"invoice_number": "INV-ORCL-100", "amount": 1200.0, "customer_email": "alice@cooper.com"}
    )
    assert success_oracle is True

@pytest.mark.asyncio
async def test_advanced_voice_capabilities():
    service = HiqonisAdvancedVoiceService()

    # Test custom IVR plan configurations
    ivr_result = await service.create_ivr_flow(
        tenant_id="test-tenant-uuid",
        menu_nodes=[
            {"dial_key": "1", "action": "Speak to Sales AI Agent"},
            {"dial_key": "2", "action": "Query billing status and invoices"}
        ]
    )
    assert ivr_result["status"] == "active"
    assert "ivr_flow_node_config" in ivr_result["ivr_id"]

    # Test completed recordings lookup
    recording_url = await service.fetch_call_recording("call_12345")
    assert recording_url is not None
    assert "audio_file_download_mock_call_12345" in recording_url
