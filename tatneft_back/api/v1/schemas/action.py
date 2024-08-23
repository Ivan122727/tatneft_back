from typing import Optional
from tatneft_back.api.v1.schemas.base import BaseOutDBMSchema, BaseSchemaIn, BaseSchemaOut


class ActionOut(BaseOutDBMSchema):
    detected_human_id: Optional[int]
    price: Optional[int]
    title: Optional[str]
    timeline: Optional[str]
    event_id: Optional[int]

class SensitiveActionOut(ActionOut):
    ...