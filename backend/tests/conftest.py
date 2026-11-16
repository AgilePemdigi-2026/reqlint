import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Task 09: the developer's backend/.env now points SLM_PROVIDER at a real
# provider (Groq). Every mocked test in this suite was written against the
# mock provider (ai_suggestion_source == "mock", honest mock generator, ...)
# and must stay deterministic and offline, so the suite pins the provider
# before app.core.config is imported. Tests that exercise a real provider
# patch settings explicitly; the live-Groq smoke check is a standalone
# script, not part of this suite.
os.environ["SLM_PROVIDER"] = "mock"

import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.main import app as fastapi_app
from app.core.database import Base, get_db
import app.core.database as core_db
import app.services.audit_service as audit_svc
from app.services.nlp_stage1 import load_stage1_resources

# In-memory test sqlite database
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

# Override engine and session maker for background tasks as well
core_db.AsyncSessionLocal = TestSessionLocal
audit_svc.AsyncSessionLocal = TestSessionLocal

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    load_stage1_resources()
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

fastapi_app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
