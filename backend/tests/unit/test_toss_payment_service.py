import pytest
from app.infrastructure.external.toss_payment_service import TossPaymentGatewayService

def test_toss_payment_service_init():
    # 1. With key
    service_with_key = TossPaymentGatewayService("test_sk_sample123")
    assert service_with_key.secret_key == "test_sk_sample123"
    assert service_with_key.auth_header.startswith("Basic ")

    # 2. Without key
    service_no_key = TossPaymentGatewayService(None)
    assert service_no_key.secret_key == ""
    assert service_no_key.auth_header == ""

@pytest.mark.asyncio
async def test_toss_payment_service_missing_key_raises_error():
    service = TossPaymentGatewayService(None)
    with pytest.raises(ValueError, match="TOSS_SECRET_KEY is not configured"):
        await service.confirm_payment(
            payment_key="pk_test_123",
            order_id="order_123",
            amount=9900.0
        )
