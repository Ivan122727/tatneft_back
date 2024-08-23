from pydantic import Field
from typing import Optional

from bson import ObjectId
from tatneft_back.db.collections.mailcode import MailCodeFields
from tatneft_back.models.base import BaseDBM
from tatneft_back.models.user import User


class MailCode(BaseDBM):
    # db fields
    to_mail: str = Field(alias=MailCodeFields.to_mail)
    code: str = Field(alias=MailCodeFields.code)
    type: str = Field(alias=MailCodeFields.type)
    to_user_oid: Optional[ObjectId] = Field(alias=MailCodeFields.to_user_oid)
    to_user: Optional[User] = Field(default=None)
