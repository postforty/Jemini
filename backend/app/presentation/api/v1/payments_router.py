from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.presentation.schemas import PaymentConfirmRequest, SubscriptionResponse
from app.presentation.dependencies import (
    get_confirm_payment_usecase,
    get_get_user_subscription_usecase,
    get_current_user_id
)
from app.usecases.payment_usecases import ConfirmPaymentUseCase, GetUserSubscriptionUseCase

router = APIRouter(prefix="/api/v1/payments", tags=["Payments"])

@router.post("/confirm", response_model=SubscriptionResponse)
async def confirm_payment(
    req: PaymentConfirmRequest,
    usecase: ConfirmPaymentUseCase = Depends(get_confirm_payment_usecase),
    user_id: Optional[str] = Depends(get_current_user_id)
):
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다."
        )

    try:
        sub = await usecase.execute(
            user_id=user_id,
            payment_key=req.payment_key,
            order_id=req.order_id,
            amount=req.amount
        )
        return SubscriptionResponse(
            user_id=sub.user_id,
            plan_type=sub.plan_type,
            status=sub.status,
            is_pro=sub.status == "active",
            current_period_end=sub.current_period_end
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"결제 승인 처리 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/status", response_model=SubscriptionResponse)
async def get_subscription_status(
    usecase: GetUserSubscriptionUseCase = Depends(get_get_user_subscription_usecase),
    user_id: Optional[str] = Depends(get_current_user_id)
):
    if not user_id:
        return SubscriptionResponse(
            user_id=None,
            plan_type="free",
            status="inactive",
            is_pro=False
        )

    sub = await usecase.execute(user_id=user_id)
    if not sub or sub.status != "active":
        return SubscriptionResponse(
            user_id=user_id,
            plan_type="free",
            status="inactive",
            is_pro=False
        )

    return SubscriptionResponse(
        user_id=sub.user_id,
        plan_type=sub.plan_type,
        status=sub.status,
        is_pro=True,
        current_period_end=sub.current_period_end
    )
