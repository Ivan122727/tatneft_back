from tatneft_back.api.v1.schemas.base import BaseSchemaIn


class RegUserIn(BaseSchemaIn):
    mail: str
    usermame: str
    code: str