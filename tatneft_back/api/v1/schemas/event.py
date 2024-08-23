from typing import Optional
from tatneft_back.api.v1.schemas.base import BaseOutDBMSchema, BaseSchemaIn, BaseSchemaOut


class EventOut(BaseOutDBMSchema):
    filename: Optional[str]
    user_id: Optional[int]
    privacy: Optional[str]

class SensitiveEventOut(EventOut):
    ...