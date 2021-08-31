import config
import json
import requests


def dropbox_get_token():
    app_key = config.DROPBOX_APP_KEY
    app_secret = config.DROPBOX_APP_SECRET

    authorization_url = config.DROPBOX_AUTH_URL
    print ('Go to the following URL and allow access:')
    print(authorization_url)

    authorization_code = input('Enter the code:\n')

    token_url = config.DROPBOX_TOKEN_URL
    params = {
        "code": authorization_code,
        "grant_type": "authorization_code",
        "client_id": app_key,
        "client_secret": app_secret
    }
    try:
        responce = requests.post(token_url, data=params)
        responce.raise_for_status()
    except (requests.RequestException, ValueError) as err:
        print(f"сервер авторизации dropbox недоступен! ошибка: {err}")
        return False
    tokens = responce.json()
    tokens = {"access_token": tokens["access_token"], 
              "refresh_token": tokens["refresh_token"]
              }
    with open('tokens.json', 'w', encoding='utf-8') as f:
        json.dump(tokens, f, indent=4)
    return True

if __name__ == "__main__": 
    dropbox_get_token()
