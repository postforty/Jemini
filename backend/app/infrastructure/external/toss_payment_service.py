import base64
import httpx
from typing import Optional
from app.domain.services import IPaymentGatewayService

DEFAULT_TEST_SECRET_KEY = "test_sk_your_secret_key_here"


class TossPaymentGatewayService(IPaymentGatewayService):
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or DEFAULT_TEST_SECRET_KEY
        encoded_key = base64.b64encode(f"{self.secret_key}:".encode("utf-8")).decode("utf-8")
        self.auth_header = f"Basic {encoded_key}"
        self.confirm_url = "https://api.tosspayments.com/v1/payments/confirm"

    async def confirm_payment(
        self,
        payment_key: str,
        order_id: str,
        amount: float
    ) -> dict:
        headers = {
            "Authorization": self.auth_header,
            "Content-Type": "application/json",
        }
        payload = {
            "paymentKey": payment_key,
            "orderId": order_id,
            "amount": int(amount),
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                self.confirm_url,
                json=payload,
                headers=headers,
            )
            try:
                data = response.json()
            except Exception:
                data = {"message": response.text}

            if response.status_code != 200:
                error_msg = data.get("message", "Payment confirmation failed")
                error_code = data.get("code", "UNKNOWN_ERROR")
                raise ValueError(f"[{error_code}] {error_msg}")

            return data
