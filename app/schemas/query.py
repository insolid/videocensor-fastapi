from typing import Annotated, Literal

from pydantic import BaseModel, Field, computed_field


class CommonQuery(BaseModel):
    page: Annotated[int, Field(ge=1, exclude=True)] = 1
    limit: Annotated[int, Field(ge=1)] = 50
    order: Annotated[
        Literal["asc", "desc"], Field(serialization_alias="sort_orders")
    ] = "asc"

    @computed_field
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit

    def model_dump(self, **kwargs):
        kwargs.setdefault("by_alias", True)
        return super().model_dump(**kwargs)
