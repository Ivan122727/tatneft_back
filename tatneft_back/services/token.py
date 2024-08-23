import binascii
import os
from random import randint

from tatneft_back.db.collections.base import Id
from tatneft_back.core.consts import db
from tatneft_back.db.collections.user import UserFields


def generate_token() -> str:
    res = binascii.hexlify(os.urandom(20)).decode() + str(randint(10000, 1000000))
    return res[:128]

async def remove_token(*, client_id: Id, token: str):
    await db.user_collection.motor_collection.update_one(
        db.user_collection.create_id_filter(id_=client_id),
        {'$pull': {UserFields.tokens: token}}
    )

