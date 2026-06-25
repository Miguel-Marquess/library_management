from fastapi import APIRouter

from library_management.database import get_session
from library_management.models.db_models import UserDatabase
from library_management.schemas.users_schemas import UserPublic, UserSchema
from fastapi import Depends
router = APIRouter(tags=['users'], prefix='/users')


@router.post('/', status_code=201, response_model=UserPublic)
async def create_user(user: UserSchema, session = Depends(get_session)):
    db_user = UserDatabase(**user.model_dump())
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user
