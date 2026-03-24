import uuid
import pytest
from httpx import AsyncClient

BASE = "/api/v1/users"


# ── Helpers ────────────────────────────────────────────────────────────────────


def company_payload():
    return {
        "name": f"Acme {uuid.uuid4().hex[:6]}",
        "description": "Test company",
    }


def user_payload(email: str):
    return {
        "email": email,
        "full_name": "Test User",
        "password": "StrongPass123!",
    }


async def get_auth_context(client: AsyncClient):
    """
    Create company + register user + login
    Returns: (headers, user_id)
    """
    # create company
    company_res = await client.post("/api/v1/companies/", json=company_payload())
    company_id = company_res.json()["id"]

    email = f"user_{uuid.uuid4().hex[:6]}@test.com"
    password = "StrongPass123!"

    # register
    register_res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Owner User",
            "password": password,
            "company_id": company_id,
        },
    )
    user_id = (
        register_res.json()["user"]["id"] if "user" in register_res.json() else None
    )

    # login
    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )

    token = login_res.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}, user_id


# ── /me ────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_me_success(client: AsyncClient):
    headers, _ = await get_auth_context(client)

    res = await client.get(f"{BASE}/me", headers=headers)

    assert res.status_code == 200, res.text
    body = res.json()
    assert "email" in body


@pytest.mark.asyncio
async def test_get_me_unauthorized(client: AsyncClient):
    res = await client.get(f"{BASE}/me")

    assert res.status_code in (401, 403), res.text


# ── List users ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_users_success(client: AsyncClient):
    headers, _ = await get_auth_context(client)

    # create another user in same company
    email = f"user_{uuid.uuid4().hex[:6]}@test.com"
    await client.post(
        f"{BASE}/",
        json=user_payload(email),
        headers=headers,
    )

    res = await client.get(f"{BASE}/", headers=headers)

    assert res.status_code == 200, res.text
    body = res.json()
    assert "users" in body
    assert len(body["users"]) >= 1


# ── Get user ───────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_user_success(client: AsyncClient):
    headers, _ = await get_auth_context(client)

    # create another user
    email = f"user_{uuid.uuid4().hex[:6]}@test.com"
    create_res = await client.post(
        f"{BASE}/",
        json=user_payload(email),
        headers=headers,
    )
    user_id = create_res.json()["id"]

    res = await client.get(f"{BASE}/{user_id}", headers=headers)

    assert res.status_code == 200, res.text
    assert res.json()["id"] == user_id


@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient):
    headers, _ = await get_auth_context(client)

    res = await client.get(f"{BASE}/{uuid.uuid4()}", headers=headers)

    assert res.status_code in (404,), res.text


# ── Create user ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_user_success(client: AsyncClient):
    headers, _ = await get_auth_context(client)

    email = f"user_{uuid.uuid4().hex[:6]}@test.com"

    res = await client.post(
        f"{BASE}/",
        json=user_payload(email),
        headers=headers,
    )

    assert res.status_code == 201, res.text
    assert res.json()["email"] == email


@pytest.mark.asyncio
async def test_create_user_duplicate_email_fails(client: AsyncClient):
    headers, _ = await get_auth_context(client)

    email = f"user_{uuid.uuid4().hex[:6]}@test.com"

    first = await client.post(f"{BASE}/", json=user_payload(email), headers=headers)
    assert first.status_code == 201, first.text

    second = await client.post(f"{BASE}/", json=user_payload(email), headers=headers)
    assert second.status_code in (400, 409), second.text


# ── Update user ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_user_success(client: AsyncClient):
    headers, _ = await get_auth_context(client)

    email = f"user_{uuid.uuid4().hex[:6]}@test.com"
    create_res = await client.post(
        f"{BASE}/",
        json=user_payload(email),
        headers=headers,
    )
    user_id = create_res.json()["id"]

    new_name = "Updated Name"

    res = await client.patch(
        f"{BASE}/{user_id}",
        json={"full_name": new_name},
        headers=headers,
    )

    assert res.status_code == 200, res.text
    assert res.json()["full_name"] == new_name


@pytest.mark.asyncio
async def test_update_user_not_found(client: AsyncClient):
    headers, _ = await get_auth_context(client)

    res = await client.patch(
        f"{BASE}/{uuid.uuid4()}",
        json={"full_name": "Does not matter"},
        headers=headers,
    )

    assert res.status_code in (404,), res.text


# ── Delete user ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_user_success(client: AsyncClient):
    headers, _ = await get_auth_context(client)

    email = f"user_{uuid.uuid4().hex[:6]}@test.com"
    create_res = await client.post(
        f"{BASE}/",
        json=user_payload(email),
        headers=headers,
    )
    user_id = create_res.json()["id"]

    res = await client.delete(f"{BASE}/{user_id}", headers=headers)

    assert res.status_code in (200, 204), res.text


@pytest.mark.asyncio
async def test_delete_user_not_found(client: AsyncClient):
    headers, _ = await get_auth_context(client)

    res = await client.delete(f"{BASE}/{uuid.uuid4()}", headers=headers)

    assert res.status_code in (404,), res.text
