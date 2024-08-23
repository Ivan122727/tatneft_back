from random import randint
from typing import Optional, Union

from bson import ObjectId
import pymongo

from tatneft_back.db.collections.base import Id
from tatneft_back.core.consts import db
from tatneft_back.db.collections.mailcode import MailCodeFields
from tatneft_back.models.mailcode import MailCode
from tatneft_back.models.user import User
from tatneft_back.utils.helpers import NotSet, is_set

async def remove_mail_code(
        *,
        id_: Optional[Id] = None,
        to_mail: Optional[str] = None,
        code: Optional[str] = None
):
    filter_ = {}
    if id_ is not None:
        filter_.update(db.mail_code_collection.create_id_filter(id_=id_))
    if to_mail is not None:
        filter_[MailCodeFields.to_mail] = to_mail
    if code is not None:
        filter_[MailCodeFields.code] = code

    if not filter_:
        raise ValueError("not filter_")

    await db.mail_code_collection.remove_document(
        filter_=filter_
    )


def _generate_mail_code() -> str:
    return str(randint(1, 9)) + str(randint(1, 9)) + str(randint(1, 9)) + str(randint(1, 9))


async def generate_unique_mail_code() -> str:
    mail_code = _generate_mail_code()
    while await db.mail_code_collection.document_exists(filter_={MailCodeFields.code: mail_code}):
        mail_code = _generate_mail_code()
    return mail_code


async def get_mail_codes(
        *,
        id_: Optional[Id] = None,
        to_mail: Optional[str] = None,
        code: Optional[str] = None,
        type_: Optional[str] = None,  # use MailCodeTypes
        to_user_oid: Union[NotSet, Optional[ObjectId]] = NotSet
) -> list[MailCode]:
    filter_ = {}
    if id_ is not None:
        filter_.update(db.mail_code_collection.create_id_filter(id_=id_))
    if to_mail is not None:
        filter_[MailCodeFields.to_mail] = to_mail
    if code is not None:
        filter_[MailCodeFields.code] = code
    if type_ is not None:
        filter_[MailCodeFields.type] = type_
    if is_set(to_user_oid):
        filter_[MailCodeFields.to_user_oid] = to_user_oid

    cursor = db.mail_code_collection.create_cursor(
        filter_=filter_,
        sort_=[(MailCodeFields.created, pymongo.DESCENDING)],
    )

    return [MailCode.parse_document(doc) async for doc in cursor]


async def create_mail_code(
        *,
        to_mail: str,
        code: str = None,
        type_: str,  # use MailCodeTypes
        to_user_oid: Optional[ObjectId] = None
) -> MailCode:
    to_user: Optional[User] = None
    if to_user_oid is not None:
        to_user = await db.user_collection.find_document_by_id(id_=to_user_oid)
        if to_user is None:
            raise Exception("to_user is None")

    if code is None:
        code = await generate_unique_mail_code()

    doc_to_insert = {
        MailCodeFields.to_mail: to_mail,
        MailCodeFields.code: code,
        MailCodeFields.type: type_,
        MailCodeFields.to_user_oid: to_user_oid
    }
    inserted_doc = await db.mail_code_collection.insert_document(doc_to_insert)
    created_mail_code = MailCode.parse_document(inserted_doc)

    created_mail_code.to_user = to_user

    return created_mail_code