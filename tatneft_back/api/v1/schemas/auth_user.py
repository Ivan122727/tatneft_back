from tatneft_back.api.v1.schemas.base import BaseSchemaIn


class AuthUserIn(BaseSchemaIn):
    mail: str
    code: str