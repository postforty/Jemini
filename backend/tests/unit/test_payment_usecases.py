import pytest
import json
from typing import Optional, List, Dict
from app.domain.entities import Payment, Subscription
from app.domain.repositories import IPaymentRepository, ISubscriptionRepository
from app.domain.services import IPaymentGatewayService
from app.usecases.payment_usecases import ConfirmPaymentUseCase, GetUserSubscriptionUseCase
from app.usecases.generate_usecase import GenerateResponseUseCase
from tests.unit.test_usecases import MockChatRepository, MockMessageRepository, MockLLMService

class MockPaymentRepository(IPaymentRepository):
    def __init__(self):
        self.payments: Dict[str, Payment] = {}

    async def add(self, payment: Payment) -> Payment:
        self.payments[payment.id] = payment
        return payment

    async def get_by_order_id(self, order_id: str) -> Optional[Payment]:
        for p in self.payments.values():
            if p.order_id == order_id:
                return p
        return None

    async def get_by_user_id(self, user_id: str) -> List[Payment]:
        return [p for p in self.payments.values() if p.user_id == user_id]

class MockSubscriptionRepository(ISubscriptionRepository):
    def __init__(self):
        self.subs: Dict[str, Subscription] = {}

    async def get_by_user_id(self, user_id: str) -> Optional[Subscription]:
        return self.subs.get(user_id)

    async def upsert(self, subscription: Subscription) -> Subscription:
        self.subs[subscription.user_id] = subscription
        return subscription

class MockPaymentGatewayService(IPaymentGatewayService):
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail

    async def confirm_payment(self, payment_key: str, order_id: str, amount: float) -> dict:
        if self.should_fail:
            raise ValueError("[REJECT_CARD_COMPANY] 잔액이 부족합니다.")
        return {
            "paymentKey": payment_key,
            "orderId": order_id,
            "orderName": "Jemini Pro Membership",
            "method": "간편결제",
            "status": "DONE",
            "totalAmount": amount,
        }

@pytest.mark.asyncio
async def test_confirm_payment_success():
    pay_repo = MockPaymentRepository()
    sub_repo = MockSubscriptionRepository()
    gw_service = MockPaymentGatewayService()

    usecase = ConfirmPaymentUseCase(pay_repo, sub_repo, gw_service)
    sub = await usecase.execute(
        user_id="user_123",
        payment_key="pk_test_12345",
        order_id="order_12345",
        amount=9900.0
    )

    assert sub.user_id == "user_123"
    assert sub.plan_type == "pro"
    assert sub.status == "active"
    assert len(pay_repo.payments) == 1

@pytest.mark.asyncio
async def test_confirm_payment_failure():
    pay_repo = MockPaymentRepository()
    sub_repo = MockSubscriptionRepository()
    gw_service = MockPaymentGatewayService(should_fail=True)

    usecase = ConfirmPaymentUseCase(pay_repo, sub_repo, gw_service)
    with pytest.raises(ValueError) as excinfo:
        await usecase.execute(
            user_id="user_123",
            payment_key="pk_test_fail",
            order_id="order_fail",
            amount=9900.0
        )
    assert "잔액이 부족합니다" in str(excinfo.value)
    assert len(pay_repo.payments) == 0

@pytest.mark.asyncio
async def test_get_user_subscription_usecase():
    sub_repo = MockSubscriptionRepository()
    usecase = GetUserSubscriptionUseCase(sub_repo)

    # 1. No user_id
    res_none = await usecase.execute(None)
    assert res_none is None

    # 2. Free user (no subscription record)
    res_free = await usecase.execute("free_user")
    assert res_free is None

    # 3. Pro user
    await sub_repo.upsert(Subscription(user_id="pro_user", plan_type="pro", status="active"))
    res_pro = await usecase.execute("pro_user")
    assert res_pro is not None
    assert res_pro.plan_type == "pro"
    assert res_pro.status == "active"

@pytest.mark.asyncio
async def test_generate_response_pro_model_permission_check():
    chat_repo = MockChatRepository()
    msg_repo = MockMessageRepository()
    llm_service = MockLLMService()
    sub_repo = MockSubscriptionRepository()

    gen_uc = GenerateResponseUseCase(chat_repo, msg_repo, llm_service, sub_repo)

    # Case 1: Free model (gemini-3.1-flash-lite) should work without user_id / subscription
    events_free = []
    async for e in gen_uc.execute(prompt="Hello Free", model="gemini-3.1-flash-lite"):
        events_free.append(e)
    assert any("Hello " in e for e in events_free)

    # Case 2: Free model (ollama) should work without user_id / subscription
    events_ollama = []
    async for e in gen_uc.execute(prompt="Hello Ollama", model="ollama:gemma3:270m"):
        events_ollama.append(e)
    assert any("Hello " in e for e in events_ollama)

    # Case 3: Pro model (gpt-4o) without user_id -> error event
    events_pro_no_user = []
    async for e in gen_uc.execute(prompt="Hello Pro", model="gpt-4o", user_id=None):
        events_pro_no_user.append(e)
    error_event = json.loads(events_pro_no_user[0].replace("data: ", "").strip())
    assert error_event["type"] == "error"
    assert "Pro 멤버십" in error_event["message"]

    # Case 4: Pro model (gpt-4o) with free user -> error event
    events_pro_free_user = []
    async for e in gen_uc.execute(prompt="Hello Pro", model="gpt-4o", user_id="free_user_id"):
        events_pro_free_user.append(e)
    error_event2 = json.loads(events_pro_free_user[0].replace("data: ", "").strip())
    assert error_event2["type"] == "error"
    assert "Pro 멤버십" in error_event2["message"]

    # Case 5: Pro model (gpt-4o) with active Pro user -> success
    await sub_repo.upsert(Subscription(user_id="pro_user_id", plan_type="pro", status="active"))
    events_pro_paid = []
    async for e in gen_uc.execute(prompt="Hello Pro", model="gpt-4o", user_id="pro_user_id"):
        events_pro_paid.append(e)
    assert any("Hello " in e for e in events_pro_paid)
