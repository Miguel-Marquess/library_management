from fastapi import APIRouter

from library_management.depends.database_dependencies import Session
from library_management.depends.users_dependencies import Current_user
from library_management.models.db_models import UserDatabase
from library_management.schemas.users_schemas import (
    Message,
    UserPublic,
    UserSchema,
    UserUpdate,
)
from library_management.security import get_password_hash

router = APIRouter(tags=['users'], prefix='/users')


@router.get('/', status_code=200, response_model=UserPublic)
def me(current_user: Current_user):

    return current_user


@router.post('/', status_code=201, response_model=UserPublic)
async def create_user(user: UserSchema, session: Session):
    db_user = UserDatabase(
        **user.model_dump(exclude={'password'}),
        password=get_password_hash(user.password),
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@router.delete('/me', status_code=200, response_model=Message)
async def delete_user(current_user: Current_user, session: Session):
    await session.delete(current_user)
    await session.commit()
    return {'message': 'User was deleted.'}


@router.patch('/me', status_code=200, response_model=UserPublic)
async def update_user(current_user: Current_user, user: UserUpdate, session: Session):
    for key, value in user.model_dump(exclude_unset=True, exclude={'password'}).items():
        setattr(current_user, key, value)

    if user.password:
        current_user.password = get_password_hash(user.password)

    await session.commit()
    await session.refresh(current_user)
    return current_user
