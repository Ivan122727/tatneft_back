from pydantic import Field
from typing import Optional
from tatneft_back.core.enumerations import UserRoles
from tatneft_back.db.collections.user import UserFields
from tatneft_back.models.base import BaseDBM
from tatneft_back.utils.role_utils import roles_to_list

class User(BaseDBM):
    # db fields
    username: Optional[str] = Field(alias=UserFields.username)
    roles: list[str] = Field(alias=UserFields.roles, default=[])
    tokens: list[str] = Field(alias=UserFields.tokens, default=[])
    mail: Optional[str] = Field(alias=UserFields.mail)
    count_attemps: int = Field(alias=UserFields.count_attemps, default=10)

    def compare_roles(self, needed_roles: UserRoles) -> bool:
        needed_roles = roles_to_list(needed_roles)
        return bool(set(needed_roles) & set(self.roles))