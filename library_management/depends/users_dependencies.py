from typing import Annotated

from fastapi import Depends

from library_management.models.db_models import UserDatabase
from library_management.security import get_current_user

Current_user = Annotated[UserDatabase, Depends(get_current_user)]
