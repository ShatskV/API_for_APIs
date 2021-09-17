from datetime import datetime, timedelta
from flask import current_app
from queries import add_tokens_to_base, delete_tokens_from_base, get_token_from_base
import requests


def dropbox_get_new_tokens(authorization_code=False, refresh_token=False):
    if authorization_code:
        app_key = current_app.config['DROPBOX_APP_KEY']
        app_secret = current_app.config['DROPBOX_APP_SECRET']

        token_url = current_app.config['DROPBOX_TOKEN_URL']
        print(authorization_code)
        data = {"code": authorization_code,
                "grant_type": "authorization_code",
                "client_id": app_key,
                "client_secret": app_secret
                }
        try:
            responce = requests.post(token_url, data=data)
            tokens = responce.json()
            responce.raise_for_status()
        except requests.exceptions.HTTPError:
            return {"error": "auth error", "message": tokens}, 401
        except (requests.RequestException, ValueError) as err:
            print(f"сервер авторизации dropbox недоступен! ошибка: {err}")
            return {"error": "server is anavaible!"}, 404
    else: 
        tokens = {'refresh_token': refresh_token}   
    result = add_tokens_to_base(tokens)
    if result:
        return {"message": "tokens changed!"}, 200
    return {"error": "Ошибка сервера!"}, 500

def renew_access_token(refresh_token):
    data = {'grant_type': 'refresh_token',
            'refresh_token': refresh_token
            }
    print(f'refresh_token:\n{refresh_token}')
    try:
        response = requests.post('https://api.dropbox.com/oauth2/token', data=data, 
                                 auth=(current_app.config['DROPBOX_APP_KEY'],
                                 current_app.config['DROPBOX_APP_SECRET']))
        tokens = response.json()
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        return {"error": "auth error", "message": tokens}, 401
    except (requests.RequestException, ValueError) as err:
        print(f"сервер авторизации dropbox недоступен! ошибка: {err}")
        return {"error": "server is anavaible!"}, 404
    print(f"tokens: {response.status_code}\n{tokens}")
    refresh_token_wrong = tokens.get('error_description', False)
    if refresh_token_wrong:
        return {"error": tokens['error_description'], "url_auth": current_app.config["DROPBOX_AUTH_URL"]}, 401
    access_token = tokens["access_token"]
    expiration_time = datetime.now() + timedelta(seconds=int(tokens['expires_in'])-5)
    if not add_tokens_to_base(tokens):
        return {"error": "ошибка записи в БД"}, 500
    return True, 200

def check_access_token():
    access_token = get_token_from_base('access_token')
    # print(access_token)
    if not access_token:
        # print('check_access_no_tk')
        return False
    if access_token.expired:
        delete_tokens_from_base("access_token")
        # print('check_access_exp')

        return False
    if not check_connection(access_token.token_value):
        print('check_access_con_error')

        return False
    return access_token.token_value


def check_connection(access_token):
    # token_str = f"Bearer {access_token}"
    
    headers = {'Authorization': f"Bearer {access_token}",
                'Content-Type': 'application/json',
                }
    # print(f"headers:\n {headers}")
    data = '{"query": "foo"}'
    try:
        response = requests.post('https://api.dropboxapi.com/2/check/user', headers=headers, data=data)
        result = response.json()
        response.raise_for_status()
    except (requests.RequestException, ValueError) as err:
        print(f"сервер авторизации dropbox недоступен! ошибка: {err}")
        return False
    print(f"status_check_code: {response.status_code}")
    if result.get('error', False):
        return False
    else: 
        return True

def get_new_access_token(refresh_token):
    data = {'grant_type': 'refresh_token',
            'refresh_token': refresh_token
            }
    try:
        response = requests.post('https://api.dropbox.com/oauth2/token', data=data, 
                                 auth=(current_app.config['DROPBOX_APP_KEY'], current_app.config['DROPBOX_APP_SECRET']),
                                 timeout=6)
        tokens = response.json()
        response.raise_for_status()
    except requests.exceptions.HTTPError:
            return {"error": "auth error", "message": tokens}, 401
    except (requests.RequestException, ValueError) as err:
        # print(f"сервер авторизации dropbox недоступен! ошибка: {err}")
        return {"error": "server is anavaible!"}, 404
    # print(f"tokens: {response.status_code}\n{tokens}")
    refresh_token_wrong = tokens.get('error_description', False)
    if refresh_token_wrong:
        return {"error": tokens['error_description'], "url_auth": current_app.config["DROPBOX_AUTH_URL"]}, 401
    access_token = tokens["access_token"]
    if not add_tokens_to_base(tokens):
        return {"error": "error with Database"}, 500
    print(response.json())
    return access_token, 200


def delete_db_token():
    access_token = get_token_from_base('access_token')

    if access_token is None:
        return {"error": "no access token! can't revoke"}, 400
    if access_token.expired:
        return {"error": "access token expired!"}, 400
    
    headers = {'Authorization': f'Bearer {access_token.token_value}',}

    try:
        response = requests.post('https://api.dropboxapi.com/2/auth/token/revoke', headers=headers)
        print(f"revoke token {response.status_code}")
        tokens = response.json()
        print(tokens)
        response.raise_for_status
    except requests.exceptions.HTTPError:
            return {"error": "auth error", "message": response.json()}, 401
    except (requests.RequestException, ValueError) as err:
        print(f"сервер авторизации dropbox недоступен! ошибка: {err}")
        return {"error": "server is anavaible!"}, 404
    if delete_tokens_from_base():
        return {'message': tokens, "warning": "token in base! can't delete"}, 200
    return {'message': tokens}, 200


# if __name__ == "__main__": 
#     get_new_access_token("-4a1uyReE5EAAAAAAAAAAWtIAiMv6RWpyeFQP2xr-63hQ7JbIq59Nu8UtQy6XeuP")



        
