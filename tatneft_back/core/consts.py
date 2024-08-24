import asyncio

# from tatneft_ai.utils_hack_tatneft.entity import MFiLkO
from tatneft_back.db.db import DB
from tatneft_back.core.settings import Settings

settings = Settings()
db = DB(mongo_uri=settings.mongo_uri, mongo_db_name=settings.mongo_db_name)