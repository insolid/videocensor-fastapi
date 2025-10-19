from fastapi_users import schemas


class VisibleFieldsMixin:
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


from datetime import datetime


class UserRead(schemas.BaseUser[int]):
    created_at: datetime
    updated_at: datetime


class UserCreate(VisibleFieldsMixin, schemas.BaseUserCreate):
    pass


class UserUpdate(VisibleFieldsMixin, schemas.BaseUserUpdate):
    pass
