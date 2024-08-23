from typing import Optional

from tatneft_back.core.enumerations import UserRoles
from tatneft_back.db.collections.base import Id
from tatneft_back.db.collections.user import UserFields
from tatneft_back.models.user import User
from tatneft_back.services.token import generate_token
from tatneft_back.utils.role_utils import roles_to_list
from tatneft_back.core.consts import db

async def create_user(
        *,
        mail: Optional[str] = None,
        username: Optional[str] = None,
        tokens: Optional[list[str]] = None,
        auto_create_at_least_one_token: bool = True,
        roles: UserRoles = None
):
    if roles is None:
        roles = [UserRoles.user]
    else:
        roles = roles_to_list(roles)

    created_token: Optional[str] = None
    if tokens is None:
        tokens = []
        if auto_create_at_least_one_token is True:
            created_token = generate_token()
            tokens.append(created_token)

    doc_to_insert = {
        UserFields.mail: mail,
        UserFields.username: username,
        UserFields.tokens: tokens,
        UserFields.roles: roles,
        UserFields.count_attemps: 10,
    }
    inserted_doc = await db.user_collection.insert_document(doc_to_insert)
    created_user = User.parse_document(inserted_doc)
    created_user.misc_data["created_token"] = created_token
    return created_user

async def get_user(
        *,
        id_: Optional[Id] = None,
        mail: Optional[str] = None,
        int_id: Optional[int] = None,
        token: Optional[str] = None,
) -> Optional[User]:
    filter_ = {}
    if id_ is not None:
        filter_.update(db.user_collection.create_id_filter(id_=id_))
    if int_id is not None:
        filter_[UserFields.int_id] = int_id
    if mail is not None:
        filter_[UserFields.mail] = mail
    if token is not None:
        filter_[UserFields.tokens] = {"$in": [token]}

    if not filter_:
        raise ValueError("not filter_")

    doc = await db.user_collection.find_document(filter_=filter_)
    if doc is None:
        return None
    return User.parse_document(doc)

async def update_user(
        *,
        id_: Optional[Id] = None,
        mail: Optional[str] = None,
        int_id: Optional[int] = None,
        token: Optional[str] = None,
        count: Optional[int] = None,

) -> Optional[User]:
    filter_ = {}
    if id_ is not None:
        filter_.update(db.user_collection.create_id_filter(id_=id_))
    if int_id is not None:
        filter_[UserFields.int_id] = int_id
    if mail is not None:
        filter_[UserFields.mail] = mail
    if token is not None:
        filter_[UserFields.tokens] = {"$in": [token]}

    if not filter_:
        raise ValueError("not filter_")

    doc = await db.user_collection.find_document(filter_=filter_)
    if doc is None:
        return None
    if count is not None: 
        doc[UserFields.count_attemps] -= count
        await db.user_collection.update_document(filter_=filter_, set_={UserFields.count_attemps: doc[UserFields.count_attemps]})
    return User.parse_document(doc)

async def get_users(*, roles: Optional[list[str]] = None) -> list[User]:
    users = [User.parse_document(doc) async for doc in db.user_collection.create_cursor()]
    if roles is not None:
        users = [user for user in users if user.compare_roles(roles)]
    return users
