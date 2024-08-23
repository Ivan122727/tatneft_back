from tatneft_back.api.v1.schemas.base import BaseSchemaIn


class RegUserIn(BaseSchemaIn):
    mail: str
    username: str
    code: str