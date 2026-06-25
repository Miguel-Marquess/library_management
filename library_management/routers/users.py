from fastapi import APIRouter, Depends
from sqlalchemy import select

from library_management.database import get_session
from library_management.models.db_models import UserDatabase
from library_management.schemas.users_schemas import (
    Message,
    UserPublic,
    UserSchema,
    UserUpdate,
)
from library_management.security import get_password_hash

router = APIRouter(tags=['users'], prefix='/users')


@router.post('/', status_code=201, response_model=UserPublic)
async def create_user(user: UserSchema, session=Depends(get_session)):
    db_user = UserDatabase(
        **user.model_dump(exclude={'password'}),
        password=get_password_hash(user.password),
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@router.delete('/{user_id}', status_code=200, response_model=Message)
async def delete_user(user_id: int, session=Depends(get_session)):
    user_db = await session.scalar(
        select(UserDatabase).where(UserDatabase.id == user_id)
    )
    await session.delete(user_db)
    await session.commit()
    return {'message': 'User was deleted.'}


@router.patch('/{user_id}', status_code=200, response_model=UserPublic)
async def update_user(user_id: int, user: UserUpdate, session=Depends(get_session)):
    user_db = await session.scalar(
        select(UserDatabase).where(UserDatabase.id == user_id)
    )

    for key, value in user.model_dump(exclude_unset=True, exclude={'password'}).items():
        setattr(user_db, key, value)

    if user.password:
        user_db.password = get_password_hash(user.password)

    await session.commit()
    await session.refresh(user_db)
    return user_db
