from typing import Optional
from tatneft_back.api.v1.schemas.base import BaseOutDBMSchema, BaseSchemaIn, BaseSchemaOut


class UserOut(BaseOutDBMSchema):
    roles: list[str] = []
    mail: Optional[str]
    username: Optional[str]
    count_attemps: Optional[int]

class SensitiveUserOut(UserOut):
    current_token: str


class UserExistsStatusOut(BaseSchemaOut):
    is_exists: bool


class UpdateUserIn(BaseSchemaIn):
    username: str