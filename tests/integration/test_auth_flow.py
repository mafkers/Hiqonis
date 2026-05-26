import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from apps.api.main import app
from libs.infrastructure.database.session import get_db
from libs.infrastructure.database.models import Base

# Setup in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Apply dependency override to app
app.dependency_overrides[get_db] = override_get_db

@pytest.mark.asyncio
async def test_complete_onboard_and_auth_flow():
    # Create all tables in in-memory test database
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Onboard a new tenant and its primary admin user atomically
        onboard_payload = {
            "company_name": "Hiqonis Solo Inc",
            "full_name": "Momo Solo",
            "email": "momo@hiqonis.com",
            "password": "strongpassword123"
        }
        res_onboard = await ac.post("/api/v1/auth/onboard", json=onboard_payload)
        assert res_onboard.status_code == 201, res_onboard.text
        onboard_data = res_onboard.json()
        assert "access_token" in onboard_data
        assert "tenant_id" in onboard_data
        assert "user_id" in onboard_data
        assert onboard_data["email"] == "momo@hiqonis.com"
        
        # 2. Onboard duplicate email must fail
        res_dup = await ac.post("/api/v1/auth/onboard", json=onboard_payload)
        assert res_dup.status_code == 400
        assert "Email is already registered" in res_dup.json()["detail"]

        # 3. Login with correct credentials
        login_payload = {
            "email": "momo@hiqonis.com",
            "password": "strongpassword123"
        }
        res_login = await ac.post("/api/v1/auth/login", json=login_payload)
        assert res_login.status_code == 200, res_login.text
        login_data = res_login.json()
        assert "access_token" in login_data
        assert login_data["role"] == "tenant_admin"
        assert login_data["tenant_id"] == onboard_data["tenant_id"]

        # 4. Login with incorrect password must fail with 401
        bad_login_payload = {
            "email": "momo@hiqonis.com",
            "password": "wrongpassword"
        }
        res_bad_login = await ac.post("/api/v1/auth/login", json=bad_login_payload)
        assert res_bad_login.status_code == 401
        assert "Incorrect email or password" in res_bad_login.json()["detail"]
        
        # 5. Access routes and check tenant details match
        token = login_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        conv_payload = {
            "tenant_id": login_data["tenant_id"],
            "channel": "web"
        }
        res_conv = await ac.post("/api/v1/conversations/", json=conv_payload, headers=headers)
        assert res_conv.status_code == 201
        conv_data = res_conv.json()
        assert conv_data["tenant_id"] == login_data["tenant_id"]
        assert conv_data["channel"] == "web"
        assert conv_data["status"] == "open"
