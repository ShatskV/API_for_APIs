from server import create_app
from db_model import db, Token

db.create_all(app=create_app())
