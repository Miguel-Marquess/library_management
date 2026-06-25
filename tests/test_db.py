from dataclasses import asdict

import pytest
from sqlalchemy import select

from library_management.models.db_models import UserDatabase
from tests.conftest import UserFactory


@pytest.mark.asyncio
async def test_create_user_db(session, mock_db_time):
    with mock_db_time(model=UserDatabase) as time:
        user = UserFactory()

        session.add(user)
        await session.commit()

        user_db = await session.scalar(
            select(UserDatabase).where(UserDatabase.id == user.id)
        )

    assert asdict(user_db) == {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'password': user.password,
        'created_at': time,
        'updated_at': time,
    }
