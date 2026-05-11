"""API tests for the Budget Manager application."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///./test_budget_manager.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def override_get_db():
    """Create a test database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def setup_function():
    """Recreate database tables before each test."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)


def register_user() -> dict:
    """Register a test user."""
    response = client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "password": "qwerty123",
        },
    )

    assert response.status_code == 201
    return response.json()


def login_user() -> str:
    """Login test user and return access token."""
    response = client.post(
        "/auth/login",
        data={
            "username": "user@example.com",
            "password": "qwerty123",
        },
    )

    assert response.status_code == 200

    token_data = response.json()

    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    return token_data["access_token"]


def get_auth_headers(token: str) -> dict[str, str]:
    """Return authorization headers."""
    return {
        "Authorization": f"Bearer {token}",
    }


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Budget Manager API is running",
    }


def test_register_and_login_user():
    """Test user registration and login."""
    user = register_user()

    assert user["email"] == "user@example.com"
    assert "id" in user
    assert "created_at" in user
    assert "password" not in user

    token = login_user()

    assert isinstance(token, str)
    assert len(token) > 0


def test_categories_crud():
    """Test category CRUD operations."""
    register_user()
    token = login_user()
    headers = get_auth_headers(token)

    create_response = client.post(
        "/categories/",
        json={
            "name": "Продукты",
            "type": "expense",
        },
        headers=headers,
    )

    assert create_response.status_code == 201

    category = create_response.json()

    assert category["name"] == "Продукты"
    assert category["type"] == "expense"

    category_id = category["id"]

    list_response = client.get(
        "/categories/",
        headers=headers,
    )

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    get_response = client.get(
        f"/categories/{category_id}",
        headers=headers,
    )

    assert get_response.status_code == 200
    assert get_response.json()["id"] == category_id

    update_response = client.put(
        f"/categories/{category_id}",
        json={
            "name": "Супермаркеты",
        },
        headers=headers,
    )

    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Супермаркеты"

    delete_response = client.delete(
        f"/categories/{category_id}",
        headers=headers,
    )

    assert delete_response.status_code == 204


def test_transactions_crud():
    """Test transaction CRUD operations."""
    register_user()
    token = login_user()
    headers = get_auth_headers(token)

    category_response = client.post(
        "/categories/",
        json={
            "name": "Транспорт",
            "type": "expense",
        },
        headers=headers,
    )

    category_id = category_response.json()["id"]

    create_response = client.post(
        "/transactions/",
        json={
            "amount": 1500,
            "description": "Такси",
            "date": "2026-05-09",
            "category_id": category_id,
        },
        headers=headers,
    )

    assert create_response.status_code == 201

    transaction = create_response.json()

    assert transaction["amount"] == 1500
    assert transaction["description"] == "Такси"

    transaction_id = transaction["id"]

    list_response = client.get(
        "/transactions/",
        headers=headers,
    )

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    get_response = client.get(
        f"/transactions/{transaction_id}",
        headers=headers,
    )

    assert get_response.status_code == 200
    assert get_response.json()["id"] == transaction_id

    update_response = client.put(
        f"/transactions/{transaction_id}",
        json={
            "amount": 2000,
            "description": "Такси вечером",
        },
        headers=headers,
    )

    assert update_response.status_code == 200
    assert update_response.json()["amount"] == 2000
    assert update_response.json()["description"] == "Такси вечером"

    delete_response = client.delete(
        f"/transactions/{transaction_id}",
        headers=headers,
    )

    assert delete_response.status_code == 204


def test_goals_crud():
    """Test saving goal CRUD operations."""
    register_user()
    token = login_user()
    headers = get_auth_headers(token)

    create_response = client.post(
        "/goals/",
        json={
            "title": "Накопить на ноутбук",
            "target_amount": 120000,
            "current_amount": 15000,
            "deadline": "2026-12-31",
        },
        headers=headers,
    )

    assert create_response.status_code == 201

    goal = create_response.json()

    assert goal["title"] == "Накопить на ноутбук"
    assert goal["target_amount"] == 120000

    goal_id = goal["id"]

    list_response = client.get(
        "/goals/",
        headers=headers,
    )

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    get_response = client.get(
        f"/goals/{goal_id}",
        headers=headers,
    )

    assert get_response.status_code == 200
    assert get_response.json()["id"] == goal_id

    update_response = client.put(
        f"/goals/{goal_id}",
        json={
            "current_amount": 25000,
        },
        headers=headers,
    )

    assert update_response.status_code == 200
    assert update_response.json()["current_amount"] == 25000

    delete_response = client.delete(
        f"/goals/{goal_id}",
        headers=headers,
    )

    assert delete_response.status_code == 204


def test_savings_plan_analytics():
    """Test savings plan business endpoint."""
    register_user()
    token = login_user()
    headers = get_auth_headers(token)

    category_response = client.post(
        "/categories/",
        json={
            "name": "Продукты",
            "type": "expense",
        },
        headers=headers,
    )

    category_id = category_response.json()["id"]

    client.post(
        "/transactions/",
        json={
            "amount": 15000,
            "description": "Продукты за месяц",
            "date": "2026-05-09",
            "category_id": category_id,
        },
        headers=headers,
    )

    response = client.post(
        "/analytics/savings-plan",
        json={
            "monthly_income": 120000,
            "target_amount": 60000,
            "months": 6,
        },
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["monthly_saving_required"] == 10000
    assert "average_monthly_expenses" in data
    assert "free_money" in data
    assert "is_goal_realistic" in data
    assert isinstance(data["recommendations"], list)


def test_protected_endpoint_without_token():
    """Test that protected endpoints require authorization."""
    response = client.get("/categories/")

    assert response.status_code == 401