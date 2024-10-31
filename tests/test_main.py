import time
import pytest
import asyncio
import warnings

from unittest.mock import patch, AsyncMock
from httpx import AsyncClient
from app.main import app
from app.utils import (
    generate_random_email,
    generate_random_password,
    generate_random_username,
    generate_random_candidate_name,
    generate_random_experience,
    generate_random_skills,
)

# Suppress specific deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="passlib.utils")


@pytest.mark.asyncio
async def get_access_token(async_client):
    email = generate_random_email()
    password = generate_random_password()
    response = await async_client.post(
        "/user",
        json={
            "username": generate_random_username(),
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 200

    response = await async_client.post(
        "/token", data={"username": email, "password": password}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "API is healthy"}

@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        email = generate_random_email()
        password = generate_random_password()
        response = await async_client.post(
            "/user",
            json={
                "username": generate_random_username(),
                "email": email,
                "password": password
            }
        )
    assert response.status_code == 200
    assert response.json() == {"message": "User created successfully"}

@pytest.mark.asyncio
async def test_create_candidate():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        token = await get_access_token(async_client)
        time.sleep(0.5)
        response = await async_client.post(
            "/candidates",
            json={
                "name": generate_random_candidate_name(),
                "experience": generate_random_experience(),
                "skills": generate_random_skills(),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200
    assert "name" in response.json()

@pytest.mark.asyncio
async def test_get_candidate():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        token = await get_access_token(async_client)
        candidate_response = await async_client.post(
            "/candidates",
            json={
                "name": generate_random_candidate_name(),
                "experience": generate_random_experience(),
                "skills": generate_random_skills(),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        candidate_id = str(candidate_response.json()["_id"])  # Ensure ID is a string

        response = await async_client.get(
            f"/candidates/{candidate_id}", headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_candidate():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        token = await get_access_token(async_client)
        candidate_response = await async_client.post(
            "/candidates",
            json={
                "name": generate_random_candidate_name(),
                "experience": generate_random_experience(),
                "skills": generate_random_skills(),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        candidate_id = candidate_response.json()["_id"]

        response = await async_client.put(
            f"/candidates/{candidate_id}",
            json={
                "name": generate_random_candidate_name(),
                "experience": generate_random_experience(),
                "skills": generate_random_skills(),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_delete_candidate():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        token = await get_access_token(async_client)
        candidate_response = await async_client.post(
            "/candidates",
            json={
                "name": generate_random_candidate_name(),
                "experience": generate_random_experience(),
                "skills": generate_random_skills(),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        candidate_id = candidate_response.json()["_id"]

        response = await async_client.delete(
            f"/candidates/{candidate_id}", headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 200
    assert response.json() == {"message": "Candidate deleted successfully"}

@pytest.mark.asyncio
async def test_generate_report():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        token = await get_access_token(async_client)
        response = await async_client.get(
            "/generate-report", headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
