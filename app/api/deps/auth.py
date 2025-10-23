from typing import Annotated

from fastapi import Depends

from app.models.users import User
from app.utils.fastapi_users import fastapi_users as fu

current_user = fu.current_user(active=True)
CurrentUserDep = Annotated[User, Depends(current_user)]
