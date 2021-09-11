import config
import json
import requests
from flask import current_app
from datetime import datetime, timedelta
from apis import write_read_write_tokens
from queries import add_tokens_to_base

def dropbox_get_token(authorization_code):

    app_key = current_app.config['DROPBOX_APP_KEY']
    app_secret = current_app.config['DROPBOX_APP_SECRET']

    token_url = current_app.config['DROPBOX_TOKEN_URL']
    print(authorization_code)
    params = {
        "code": authorization_code,
        "grant_type": "authorization_code",
        "client_id": app_key,
        "client_secret": app_secret
    }
    print(current_app.config['DROPBOX_AUTH_URL'])
    try:
        responce = requests.post(token_url, data=params)
        tokens = responce.json()
        responce.raise_for_status()
    except requests.exceptions.HTTPError:
        return {"error": "auth error", "message": tokens}, 401
    except (requests.RequestException, ValueError) as err:
        print(f"сервер авторизации dropbox недоступен! ошибка: {err}")
        return {"error": "server is anavaible!"}, 404
    result = add_tokens_to_base(tokens)
    if result:
        return {"message": "tokens changed!"}, 200
    return {"error": "Ошибка сервера!"}, 500

def get_access_token(refresh_token):
    data = {'grant_type': 'refresh_token',
                    'refresh_token': refresh_token
                    }
    response = requests.post('https://api.dropbox.com/oauth2/token', data=data, auth=(config.DROPBOX_APP_KEY, config.DROPBOX_APP_SECRET))
    tokens = response.json()
    print(f"tokens: {response.status_code}\n{tokens}")
    refresh_token_wrong = tokens.get('error_description', False)
    if refresh_token_wrong:
        return {"error": tokens['error_description'], "url_auth": current_app.config["DROPBOX_AUTH_URL"]}, 401
    access_token = tokens["access_token"]
    expiration_time = datetime.now() + timedelta(seconds=int(tokens['expires_in'])-5)
    write_read_write_tokens(access_token, refresh_token, expiration_time)
    return True, 200

if __name__ == "__main__": 
    dropbox_get_token("N_TB1DC5eJEAAAAAAAAGX9GgOM0OE3KaBLV6jAuqWus")
