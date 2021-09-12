from os import access
from db_model import Token, db
# from server import db
# from server import db
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError


def add_tokens_to_base(tokens):
    if tokens.get('access_token', False):
        token = Token.query.filter_by(type_token="access_token").first()
        if token is None:
            access_token = Token(type_token="access_token", 
                                 token_value=tokens["access_token"],
                                 exp_datetime = datetime.now() + timedelta(seconds=tokens["expires_in"]-10) 
                                 )
            db.session.add(access_token)
        else:
            token.token_value = tokens["access_token"]

    if tokens.get('refresh_token', False):       
        token = Token.query.filter_by(type_token="refresh_token").first()   
        if token is None:
            refresh_token = Token(type_token="refresh_token", 
                                  token_value=tokens["refresh_token"])
            db.session.add(refresh_token)
        else:
            token.token_value = tokens["refresh_token"]
    
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        return False
    return True


def get_token_from_base(type_token):
    token= Token.query.filter_by(type_token=type_token).first()
    if token is None:
        return False
    return token


def delete_tokens_from_base(type_token=False):
    if type_token:
        token = get_token_from_base(type_token)
        if not token:
            db.session.delete(token)
    else:
        db.session.query(Token).delete()
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        return False
    return True