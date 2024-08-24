from tatneft_back.core.create_app import create_app
from tatneft_back.core.consts import db

db.drop_collections()
app = create_app()
