from contextlib import contextmanager
from datetime import datetime

import factory
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from library_management.app import app
from library_management.database import get_session
from library_management.models.db_models import UserDatabase, registry_table
from library_management.security import get_password_hash


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:17', driver='psycopg') as postgres:
        yield create_async_engine(postgres.get_connection_url())


@pytest_asyncio.fixture
async def session(engine):
    async with engine.begin() as conn:
        await conn.run_sync(registry_table.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as ss:
        yield ss

    async with engine.begin() as conn:
        await conn.run_sync(registry_table.metadata.drop_all)


@pytest_asyncio.fixture
async def user(session):
    password = 'testpassword'

    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password
    # cria um atributo temporario no ORM
    return user


@pytest_asyncio.fixture
async def other_user(session):
    password = 'testpassword'

    user = UserFactory(password=get_password_hash(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password

    return user


class UserFactory(factory.Factory):
    class Meta:
        model = UserDatabase

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}password')


@contextmanager
def _mock_db_time(model, time=datetime(2026, 6, 11)):
    def fake_hook_time(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time

        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_hook_time)
    yield time
    event.remove(model, 'before_insert', fake_hook_time)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture
def token(client, user):
    response = client.post(
        'auth/login', data={'username': user.email, 'password': user.clean_password}
    )

    return response.json()['access_token']
