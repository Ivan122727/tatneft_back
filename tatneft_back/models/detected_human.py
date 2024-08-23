from pydantic import Field
from typing import Optional
from tatneft_back.db.collections.detected_human import DetectedHumanFields
from tatneft_back.models.base import BaseDBM

class DetectedHuman(BaseDBM):
    # db fields
    event_id: Optional[int] = Field(alias=DetectedHumanFields.event_id)
    avatar_filename: Optional[str] = Field(alias=DetectedHumanFields.avatar_filename)
    usefulness: Optional[int] = Field(alias=DetectedHumanFields.usefulness)