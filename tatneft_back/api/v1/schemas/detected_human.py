from typing import Optional
from tatneft_back.api.v1.schemas.base import BaseOutDBMSchema, BaseSchemaIn, BaseSchemaOut


class DetectedHumanOut(BaseOutDBMSchema):
    event_id: Optional[int]
    avatar_filename: Optional[str]
    usefulness: Optional[int]

class SensitiveDetectedHumanOut(DetectedHumanOut):
    ...