import uuid
import pytest
from httpx import AsyncClient

BASE = "/api/v1/companies"


# ── Helpers ────────────────────────────────────────────────────────────────────


def company_payload() -> dict:
    return {
        "name": f"Acme {uuid.uuid4().hex[:6]}",
        "description": "Test company",
    }


async def get_auth_header(client: AsyncClient):
    """
    Create company + user + login → return auth header
    """
    company_res = await client.post(f"{BASE}/", json=company_payload())
    company_id = company_res.json()["id"]

    email = f"user_{uuid.uuid4().hex[:6]}@test.com"
    password = "StrongPass123!"

    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Test User",
            "password": password,
            "company_id": company_id,
        },
    )

    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )

    token = login_res.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


# ── Create ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_company_success(client: AsyncClient):
    res = await client.post(f"{BASE}/", json=company_payload())

    assert res.status_code == 201, res.text
    body = res.json()
    assert "id" in body
    assert body["name"].startswith("Acme")


@pytest.mark.asyncio
async def test_create_company_duplicate_name_fails(client: AsyncClient):
    payload = company_payload()

    first = await client.post(f"{BASE}/", json=payload)
    assert first.status_code == 201, first.text

    second = await client.post(f"{BASE}/", json=payload)
    assert second.status_code in (
        400,
        409,
    ), f"Expected 400/409 for duplicate name, got {second.status_code}: {second.text}"


# ── Get ────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_my_company_success(client: AsyncClient):
    headers = await get_auth_header(client)

    res = await client.get(f"{BASE}/my_company", headers=headers)

    assert res.status_code == 200, res.text
    body = res.json()
    assert "id" in body
    assert "name" in body


@pytest.mark.asyncio
async def test_get_my_company_unauthorized(client: AsyncClient):
    res = await client.get(f"{BASE}/my_company")

    assert res.status_code in (401, 403), res.text


# ── Update ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_my_company_success(client: AsyncClient):
    headers = await get_auth_header(client)

    new_name = f"Updated {uuid.uuid4().hex[:6]}"

    res = await client.put(
        f"{BASE}/update_my_company",
        json={"name": new_name, "description": "Updated"},
        headers=headers,
    )

    assert res.status_code == 200, res.text
    assert res.json()["name"] == new_name


@pytest.mark.asyncio
async def test_update_my_company_unauthorized(client: AsyncClient):
    res = await client.put(
        f"{BASE}/update_my_company",
        json={"name": "Should Fail"},
    )

    assert res.status_code in (401, 403), res.text


# ── Delete ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_company_no_users_fails(client: AsyncClient):
    # No user → no auth → should fail
    res = await client.delete(f"{BASE}/delete_my_company")

    assert res.status_code in (401, 403), res.text


@pytest.mark.asyncio
async def test_delete_company_success_last_user(client: AsyncClient):
    headers = await get_auth_header(client)

    res = await client.delete(
        f"{BASE}/delete_my_company",
        headers=headers,
    )

    assert res.status_code in (200, 204), res.text
