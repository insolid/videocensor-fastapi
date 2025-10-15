from fastapi_users import schemas


class UserMixin:
    model_config = {
        "json_schema_extra": {
            # Remove other fields from api docs
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "Password1!",
                }
            ]
        }
    }


class UserRead(schemas.BaseUser[int]):
    pass


class UserCreate(UserMixin, schemas.BaseUserCreate):
    pass


class UserUpdate(UserMixin, schemas.BaseUserUpdate):
    pass
