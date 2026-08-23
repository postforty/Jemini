from typing import Optional
from app.domain.entities import Payment, Subscription
from app.domain.repositories import IPaymentRepository, ISubscriptionRepository
from app.domain.services import IPaymentGatewayService

class ConfirmPaymentUseCase:
    def __init__(
        self,
        payment_repo: IPaymentRepository,
        subscription_repo: ISubscriptionRepository,
        payment_service: IPaymentGatewayService
    ):
        self.payment_repo = payment_repo
        self.subscription_repo = subscription_repo
        self.payment_service = payment_service

    async def execute(
        self,
        user_id: str,
        payment_key: str,
        order_id: str,
        amount: float
    ) -> Subscription:
        if not user_id:
            raise ValueError("로그인이 필요한 서비스입니다.")

        # 1. Confirm payment with Toss Payments Gateway
        toss_res = await self.payment_service.confirm_payment(
            payment_key=payment_key,
            order_id=order_id,
            amount=amount
        )

        order_name = toss_res.get("orderName", "Jemini Pro Membership")
        method = toss_res.get("method", "카드")
        status = toss_res.get("status", "DONE")

        # 2. Save payment record
        payment = Payment(
            payment_key=payment_key,
            order_id=order_id,
            order_name=order_name,
            amount=amount,
            method=method,
            status=status,
            user_id=user_id
        )
        saved_payment = await self.payment_repo.add(payment)

        # 3. Create or update Pro Subscription
        subscription = Subscription(
            user_id=user_id,
            plan_type="pro",
            status="active",
            payment_id=saved_payment.id
        )
        saved_sub = await self.subscription_repo.upsert(subscription)
        return saved_sub

class GetUserSubscriptionUseCase:
    def __init__(self, subscription_repo: ISubscriptionRepository):
        self.subscription_repo = subscription_repo

    async def execute(self, user_id: Optional[str]) -> Optional[Subscription]:
        if not user_id:
            return None
        return await self.subscription_repo.get_by_user_id(user_id)
