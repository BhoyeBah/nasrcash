import asyncio
import os
import tempfile

os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://nasrcash:nasrcash@localhost:5432/nasrcash_test"
)
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("KYC_STORAGE_PATH", tempfile.mkdtemp(prefix="nasrcash-kyc-test-"))

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.core.database import Base
from app.modules.registry import import_all_models

get_settings.cache_clear()
settings = get_settings()

import_all_models()

test_engine = create_async_engine(settings.database_url, future=True, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
def _prepare_database():
    from app.modules.countries.seed import seed_countries

    async def _create():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestSessionLocal() as session:
            await seed_countries(session)
            await session.commit()

    asyncio.run(_create())
    yield


# Reference/config tables seeded once for the whole test session — never wiped between tests.
REFERENCE_TABLES = {"countries"}


@pytest.fixture(autouse=True)
async def _clean_tables():
    yield
    async with test_engine.begin() as conn:
        table_names = ", ".join(
            f'"{t.name}"'
            for t in reversed(Base.metadata.sorted_tables)
            if t.name not in REFERENCE_TABLES
        )
        if table_names:
            await conn.exec_driver_sql(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE")


@pytest.fixture(autouse=True)
async def _seed_fx_rates():
    from app.modules.fx.seed import seed_fx_rates

    async with TestSessionLocal() as session:
        await seed_fx_rates(session)
        await session.commit()
    yield


@pytest.fixture
async def db_session() -> AsyncSession:
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session):
    from app.core.database import get_db
    from app.main import app

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
