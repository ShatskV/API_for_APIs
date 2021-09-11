from os import access
from db_model import db, Token
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError

def add_tokens_to_base(tokens):
    access_token = Token(type_token="access_token", 
                         token_value=tokens["access_token"],
                         exp_datetime = datetime.now() + timedelta(seconds=tokens["expires_in"]-10) 
                         )
    refresh_token = Token(type_token="refresh_token", 
                          token_value=tokens["refresh_token"])
    if Token.query.filter_by(type_token="access_token").count() > 0:
        db.session.add(access_token)
    else:
        db.session.update(access_token)
    if Token.query.filter_by(type_token="refresh_token").count() > 0:
        db.session.add(refresh_token)
    else:
        db.session.update(refresh_token)
    
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        return False
    return True