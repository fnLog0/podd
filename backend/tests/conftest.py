import pytest
import pytest_asyncio
import os
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from src.main import app
from src.database import async_session
from src.models import RefreshToken, User


@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    os.environ["JWT_SECRET"] = "test-secret-key-32-bytes-long-!"
    os.environ["JWT_ALGORITHM"] = "HS256"
    yield
    del os.environ["JWT_SECRET"]


@pytest_asyncio.fixture(scope="function")
async def clean_db():
    async with async_session() as session:
        await session.execute(delete(RefreshToken))
        await session.execute(delete(User))
        await session.commit()
    yield
    async with async_session() as session:
        await session.execute(delete(RefreshToken))
        await session.execute(delete(User))
        await session.commit()


@pytest_asyncio.fixture(scope="function")
async def client(clean_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
