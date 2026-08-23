import pytest
from fastapi.testclient import TestClient
from main import app
from app.presentation.dependencies import (
    get_confirm_payment_usecase,
    get_get_user_subscription_usecase,
    get_current_user_id
)
from app.domain.entities import Subscription

client = TestClient(app)

def test_get_subscription_status_unauthenticated():
    app.dependency_overrides[get_current_user_id] = lambda: None
    response = client.get("/api/v1/payments/status")
    assert response.status_code == 200
    data = response.json()
    assert data["is_pro"] is False
    assert data["status"] == "inactive"
    app.dependency_overrides.clear()

def test_get_subscription_status_pro_user():
    app.dependency_overrides[get_current_user_id] = lambda: "pro_test_user"
    
    class FakeGetSubUseCase:
        async def execute(self, user_id):
            return Subscription(user_id=user_id, plan_type="pro", status="active")

    app.dependency_overrides[get_get_user_subscription_usecase] = lambda: FakeGetSubUseCase()

    response = client.get("/api/v1/payments/status")
    assert response.status_code == 200
    data = response.json()
    assert data["is_pro"] is True
    assert data["plan_type"] == "pro"
    assert data["user_id"] == "pro_test_user"
    app.dependency_overrides.clear()

def test_confirm_payment_unauthenticated():
    app.dependency_overrides[get_current_user_id] = lambda: None
    payload = {
        "paymentKey": "pk_test_123",
        "orderId": "order_test_123",
        "amount": 9900
    }
    response = client.post("/api/v1/payments/confirm", json=payload)
    assert response.status_code == 401
    app.dependency_overrides.clear()

def test_confirm_payment_success():
    app.dependency_overrides[get_current_user_id] = lambda: "user_test_456"

    class FakeConfirmUseCase:
        async def execute(self, user_id, payment_key, order_id, amount):
            return Subscription(user_id=user_id, plan_type="pro", status="active")

    app.dependency_overrides[get_confirm_payment_usecase] = lambda: FakeConfirmUseCase()

    payload = {
        "paymentKey": "pk_test_123",
        "orderId": "order_test_123",
        "amount": 9900
    }
    response = client.post("/api/v1/payments/confirm", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_pro"] is True
    assert data["user_id"] == "user_test_456"
    app.dependency_overrides.clear()
