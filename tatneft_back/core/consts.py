import asyncio

from tatneft_back.db.db import DB
from tatneft_back.core.settings import Settings

settings = Settings()
db = DB(mongo_uri=settings.mongo_uri, mongo_db_name=settings.mongo_db_name)
db.drop_collections(only_using=False)