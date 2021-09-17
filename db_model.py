from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
# from server import db

db = SQLAlchemy()

class Token(db.Model):
    __tablename__ = "tokens"

    id = db.Column(db.Integer, primary_key=True)
    type_token = db.Column(db.String(25), index=True, unique=True, nullable=False)
    token_value = db.Column(db.String(200), nullable=False, unique=True)
    exp_datetime = db.Column(db.DateTime())

    @property
    def expired(self):
        if self.exp_datetime is None:
            return False
        return self.exp_datetime < datetime.now()
        
    def __repr__(self):
        return '<token name={} id={}>'.format(self.type_token, self.id)

    