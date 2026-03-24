import uuid
import pytest
from httpx import AsyncClient

BASE = "/api/v1"
PROTECTED_ROUTE = f"{BASE}/users/me"


# ── Helpers ────────────────────────────────────────────────────────────────────


def unique_email() -> str:
    return f"user_{uuid.uuid4().hex[:8]}@test.com"


def company_payload() -> dict:
    return {"name": f"Acme {uuid.uuid4().hex[:6]}", "description": "Test company"}


def user_payload(company_id: str, email: str) -> dict:
    return {
        "email": email,
        "full_name": "Alice Smith",
        "password": "StrongPass123!",
        "company_id": company_id,
    }


def login_payload(email: str, password: str) -> dict:
    # OAuth2PasswordRequestForm expects form data with field "username".
    # Your app uses email as the username — so email goes in the username field.
    return {"username": email, "password": password}


# ── Step 1: company creation ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_company(client: AsyncClient):
    res = await client.post(f"{BASE}/companies/", json=company_payload())

    assert res.status_code == 201, res.text
    body = res.json()
    assert "id" in body
    assert body["name"].startswith("Acme")


# ── Step 2: registration ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    company_res = await client.post(f"{BASE}/companies/", json=company_payload())
    assert company_res.status_code == 201, company_res.text
    company_id = company_res.json()["id"]

    email = unique_email()
    res = await client.post(
        f"{BASE}/auth/register", json=user_payload(company_id, email)
    )

    assert res.status_code == 201, res.text
    body = res.json()
    assert "access_token" in body
    assert body["access_token"] != ""


@pytest.mark.asyncio
async def test_register_duplicate_email_fails(client: AsyncClient):
    """Registering twice with the same email must be rejected."""
    company_res = await client.post(f"{BASE}/companies/", json=company_payload())
    assert company_res.status_code == 201, company_res.text
    company_id = company_res.json()["id"]

    email = unique_email()
    payload = user_payload(company_id, email)

    first = await client.post(f"{BASE}/auth/register", json=payload)
    assert first.status_code == 201, first.text

    second = await client.post(f"{BASE}/auth/register", json=payload)
    assert second.status_code in (
        400,
        409,
    ), f"Expected 400/409 for duplicate email, got {second.status_code}: {second.text}"


@pytest.mark.asyncio
async def test_register_invalid_company_fails(client: AsyncClient):
    """A non-existent company_id must be rejected."""
    res = await client.post(
        f"{BASE}/auth/register",
        json=user_payload(
            company_id=str(uuid.uuid4()),
            email=unique_email(),
        ),
    )
    assert res.status_code in (
        400,
        404,
        422,
    ), f"Expected error for missing company, got {res.status_code}: {res.text}"


# ── Step 3: login ──────────────────────────────────────────────────────────────
#
# FastAPI's OAuth2PasswordRequestForm expects:
#   - form data (not JSON)  →  use data= not json=
#   - field named "username"  →  your app uses email here


@pytest.mark.asyncio
async def test_login_returns_token(client: AsyncClient):
    company_res = await client.post(f"{BASE}/companies/", json=company_payload())
    company_id = company_res.json()["id"]
    email = unique_email()
    password = "StrongPass123!"

    await client.post(f"{BASE}/auth/register", json=user_payload(company_id, email))

    res = await client.post(f"{BASE}/auth/login", data=login_payload(email, password))

    assert res.status_code == 200, res.text
    body = res.json()
    assert "access_token" in body
    assert body["access_token"] != ""


@pytest.mark.asyncio
async def test_login_wrong_password_fails(client: AsyncClient):
    company_res = await client.post(f"{BASE}/companies/", json=company_payload())
    company_id = company_res.json()["id"]
    email = unique_email()

    await client.post(f"{BASE}/auth/register", json=user_payload(company_id, email))

    res = await client.post(
        f"{BASE}/auth/login",
        data=login_payload(email, "wrongpassword"),
    )
    assert res.status_code in (
        400,
        401,
    ), f"Expected 400/401 for bad password, got {res.status_code}: {res.text}"


@pytest.mark.asyncio
async def test_login_unknown_email_fails(client: AsyncClient):
    res = await client.post(
        f"{BASE}/auth/login",
        data=login_payload(unique_email(), "whatever"),
    )
    assert res.status_code in (400, 401, 404), res.text


# ── Step 4: protected route ────────────────────────────────────────────────────


async def _get_token(client: AsyncClient) -> str:
    """Create a company + user, log in, return a valid JWT."""
    company_res = await client.post(f"{BASE}/companies/", json=company_payload())
    company_id = company_res.json()["id"]
    email = unique_email()
    password = "StrongPass123!"

    await client.post(f"{BASE}/auth/register", json=user_payload(company_id, email))
    login_res = await client.post(
        f"{BASE}/auth/login",
        data=login_payload(email, password),
    )
    return login_res.json()["access_token"]


@pytest.mark.asyncio
async def test_protected_route_with_valid_token(client: AsyncClient):
    token = await _get_token(client)

    res = await client.get(
        PROTECTED_ROUTE,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text


@pytest.mark.asyncio
async def test_protected_route_without_token_fails(client: AsyncClient):
    res = await client.get(PROTECTED_ROUTE)
    assert res.status_code in (
        401,
        403,
    ), f"Expected 401/403 with no token, got {res.status_code}: {res.text}"


@pytest.mark.asyncio
async def test_protected_route_with_bad_token_fails(client: AsyncClient):
    res = await client.get(
        PROTECTED_ROUTE,
        headers={"Authorization": "Bearer this.is.not.a.valid.token"},
    )
    assert res.status_code in (401, 403), res.text


# ── Full system test ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_full_auth_flow(client: AsyncClient):
    """
    End-to-end: create company → register → login → access protected route.
    Each assertion includes res.text so failures print the actual server response.
    """

    # 1. Create company
    company_res = await client.post(f"{BASE}/companies/", json=company_payload())
    assert company_res.status_code == 201, company_res.text
    company_id = company_res.json()["id"]

    # 2. Register
    email = unique_email()
    password = "StrongPass123!"
    register_res = await client.post(
        f"{BASE}/auth/register",
        json=user_payload(company_id, email),
    )
    assert register_res.status_code == 201, register_res.text
    assert register_res.json()["access_token"]

    # 3. Login
    login_res = await client.post(
        f"{BASE}/auth/login",
        data=login_payload(email, password),
    )
    assert login_res.status_code == 200, login_res.text
    token = login_res.json()["access_token"]
    assert token

    # 4. Access protected route
    protected_res = await client.get(
        PROTECTED_ROUTE,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert protected_res.status_code == 200, protected_res.text
