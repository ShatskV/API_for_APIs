from datetime import datetime, timedelta
from flask import current_app
from utils import requests_data
from queries import add_tokens_to_base, delete_tokens_from_base, get_token_from_base
import requests


def dropbox_get_new_tokens(authorization_code=False, refresh_token=False):
    if authorization_code:
        app_key = current_app.config['DROPBOX_APP_KEY']
        app_secret = current_app.config['DROPBOX_APP_SECRET']

        token_url = current_app.config['DROPBOX_TOKEN_URL']
        data = {"code": authorization_code,
                "grant_type": "authorization_code",
                "client_id": app_key,
                "client_secret": app_secret
                }
        tokens, status_code = requests_data(token_url, data=data)
        if status_code == 401:
            {"error": "auth error", "message": tokens["error_message"]}, 401
        if status_code != 200:
            return tokens, status_code

        # try:
        #     responce = requests.post(token_url, data=data)
        #     tokens = responce.json()
        #     responce.raise_for_status()
        # except requests.exceptions.HTTPError:
        #     return {"error": "auth error", "message": tokens}, 401
        # except (requests.RequestException, ValueError) as err:
        #     print(f"сервер авторизации dropbox недоступен! ошибка: {err}")
        #     return {"error": "server is anavaible!"}, 404
    else: 
        tokens = {'refresh_token': refresh_token}   
    result = add_tokens_to_base(tokens)
    if result:
        return {"message": "tokens changed!"}, 200
    return {"error": "Ошибка сервера!"}, 500


def renew_access_token(refresh_token):
    app_key = current_app.config['DROPBOX_APP_KEY'],
    app_secret = current_app.config['DROPBOX_APP_SECRET']
    token_url = current_app.config['DROPBOX_TOKEN_URL']
    data = {'grant_type': 'refresh_token',
            'refresh_token': refresh_token
            }
    print(app_key)
    print(app_secret)
    print(data)
    tokens, status_code = requests_data(token_url, data=data, auth=(app_key, app_secret))

    # try:
    #     response = requests.post('https://api.dropbox.com/oauth2/token', data=data, 
    #                              auth=(current_app.config['DROPBOX_APP_KEY'],
    #                              current_app.config['DROPBOX_APP_SECRET']))
    #     tokens = response.json()
    #     response.raise_for_status()
    # except requests.exceptions.HTTPError:
    #     return {"error": "auth error", "message": tokens}, 401
    # except (requests.RequestException, ValueError) as err:
    #     print(f"сервер авторизации dropbox недоступен! ошибка: {err}")
    #     return {"error": "server is anavaible!"}, 404
    # print(f"tokens: {response.status_code}\n{tokens}")
    if status_code == 401:
            {"error": "auth error", "message": tokens["error_message"],
             "url_auth": current_app.config["DROPBOX_AUTH_URL"]}, 401
    if status_code != 200:
        return tokens, status_code
    ########
    refresh_token_wrong = tokens.get('error', False)
    if refresh_token_wrong:
        return {"error": tokens['error_description'], "url_auth": current_app.config["DROPBOX_AUTH_URL"]}, 401
    access_token = tokens["access_token"]
    # expiration_time = datetime.now() + timedelta(seconds=int(tokens['expires_in'])-5)
    if not add_tokens_to_base(tokens):
        return {"error": "error writing token to database!"}, 500
    return access_token, 200

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
    check_url = current_app.config['DROPBOX_CHECK_URL']
    headers = {'Authorization': f"Bearer {access_token}",
                'Content-Type': 'application/json',
                }
    # print(f"headers:\n {headers}")
    data = '{"query": "foo"}'
    result, status_code = requests_data(check_url, headers=headers, data=data)
    
    if status_code != 200:
        return False
    # try:
    #     response = requests.post(check_url, headers=headers, data=data)
    #     result = response.json()
    #     response.raise_for_status()
    # except (requests.RequestException, ValueError) as err:
    #     print(f"сервер авторизации dropbox недоступен! ошибка: {err}")
    #     return False
    # print(f"status_check_code: {response.status_code}")
    if result.get('error', False):
        return False
    else: 
        return True
### лишнее
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
    return access_token, 200


def delete_db_token():
    access_token = get_token_from_base('access_token')

    if access_token is None:
        return {"error": "no access token! can't revoke"}, 400
    if access_token.expired:
        return {"error": "access token expired!"}, 400
    token_url = current_app.config['DROPBOX_TOKEN_URL']
    # print(token_url+'/revoke')
    headers = {'Authorization': f'Bearer {access_token.token_value}',}
    print(headers)
    tokens, status_code = requests_data(token_url+'/revoke', headers=headers)
    
    # try:
    #     response = requests.post('https://api.dropboxapi.com/2/auth/token/revoke', headers=headers)
    #     print(f"revoke token {response.status_code}")
    #     tokens = response.json()
    #     print(tokens)
    #     response.raise_for_status
    # except requests.exceptions.HTTPError:
    #         return {"error": "auth error", "message": response.json()}, 401
    # except (requests.RequestException, ValueError) as err:
    #     print(f"сервер авторизации dropbox недоступен! ошибка: {err}")
    #     return {"error": "server is anavaible!"}, 404
    if status_code != 200:
        return {"error", "service is anavaible!"}, status_code
    if delete_tokens_from_base():
        return {'message': tokens, "warning": "token in base! can't delete"}, 200
    return {'message': tokens}, 200


# if __name__ == "__main__": 
#     get_new_access_token("-4a1uyReE5EAAAAAAAAAAWtIAiMv6RWpyeFQP2xr-63hQ7JbIq59Nu8UtQy6XeuP")



        
