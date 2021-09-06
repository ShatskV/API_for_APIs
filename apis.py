from flask import current_app
import json
import fnmatch
from requests import request
import config
import dropbox
from dropbox.exceptions import AuthError
import requests

def weather_by_city(city_name):
    weather_url = current_app.config['WEATHER_URL']
    params = {
        "key": current_app.config['WEATHER_API_KEY'],
        "q": city_name,
        "format": "json",
        "num_of_days": 1,
        "lang": "ru"
    }

    try:
        result = requests.get(weather_url, params=params)
        weather = result.json()
        result.raise_for_status()
    except (requests.RequestException, ValueError) as err:
        print(f"сервер погоды недоступен! ошибка: {err}")
        return False

    if 'data' in weather:
        if 'current_condition' in weather['data']:
            try:
                return weather['data']['current_condition'][0]
            except(IndexError, TypeError):
                return False
    return False


def get_book(book_to_find="Ложная слепота"):
    params = {"q": book_to_find, "maxResults": 3}
    try: 
        response = requests.get(config.GOOGLE_BOOKS_API, params=params)
        response.raise_for_status()
        books = response.json()
    except (requests.RequestException, ValueError) as err:
        print(f"сервер поиска книг недоступен! Ошибка:{err}")
        return False
    if books['items']:
        for book in books["items"]:
            volume = book["volumeInfo"]
            title = volume["title"]
            published = volume.get("publishedDate", "год издания неизвестен")
            description = volume.get("description", "описание отсутствует")
            print(f"{title} ({published}) | {description}")
    else:
        return False


def dropbox_files(mask='*'):
    
    with open('tokens.json', 'r', encoding='utf-8') as f:
        tokens = json.load(f)
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
    with dropbox.Dropbox(access_token) as dbx:
        try:
            print(dbx.users_get_current_account())
        except AuthError:
            print("AUTH ERROR")
            data = {'grant_type': 'refresh_token',
                    'refresh_token': refresh_token
                    }
            response = requests.post('https://api.dropbox.com/oauth2/token', data=data, auth=(config.DROPBOX_APP_KEY, config.DROPBOX_APP_SECRET))
            tokens = response.json()
            access_token = tokens["access_token"]
            write_read_tokens(access_token, refresh_token)
            print(response.json())
        # print(dbx.files_list_folder(path=''))
        token_str = f'Bearer {access_token}'
        headers = {'Authorization': token_str,
                   'Content-Type': 'application/json',
                   }

        data = '{"query": "foo"}'

        # response = requests.post('https://api.dropboxapi.com/2/check/user', headers=headers, data=data)
        # print(response.json())
        # token_str = f'Bearer {access_token}'
        headers = {'Authorization': token_str}
        data = '{"path": ""}'
                

        # response = requests.post('https://api.dropboxapi.com/2/file_requests/count', headers=headers, data=data)
        # print(response)
        # print(response.json())

        # headers = {'Authorization': token_str,
        #            'Content-Type': 'application/json',
        #            }

        # data = {"limit": 10, "path": '/'}

        # response = requests.post('https://api.dropboxapi.com/2/file_requests/list_v2', headers=headers, data=data)
        # # print(type(response))
        # print(response.text)
        # print('='*30)
        # headers = {'Authorization': token_str,
        #            'Content-Type': 'application/json',
        #            }

        # data = '{"limit": 100,"actions": []}'

        # response = requests.post('https://api.dropboxapi.com/2/sharing/list_folders', headers=headers, data=data)
        # entries = response.json
        # for entry in entries:
        #     print(entry["name"])
        # print(response.text)


            # print(dbx.users_get_current_account())
            # dbx.check_and_refresh_access_token()
        # print(dbx.check_and_refresh_access_token())
        # shared_link = dropbox.files.SharedLink(url=url)
        # name_list = []
        # for entry in dbx.files_list_folder(path='', shared_link=shared_link).entries:
        #     name_list.append(entry.name)
        # print(name_list[:5])


        print("%"*100)
        headers = {'Authorization': token_str,
                   'Content-Type': 'application/json',
                   }
        data ='{"path": ""}'
        response = requests.post('https://api.dropboxapi.com/2/files/list_folder', headers=headers, data=data)
        files = response.json()
        files = files['entries']
        # print(entries)
        for file in files:
            mask = '*'
            if fnmatch.fnmatch(file['name'], mask):
                print(file['name'])
       

def write_read_tokens(access_token=None, refresh_token=None):  
    if (access_token is None ) and refresh_token is  None:
        method = 'r'
    else:
        method = 'w'
    with open(config.DB_TK_JSON, method, encoding='utf-8') as f:
        if method == 'r':    
            tokens = json.load(f)
            access_token = tokens["access_token"]
            refresh_token = tokens["refresh_token"]    
            return access_token, refresh_token
        else:
            tokens = {"access_token": access_token, 
                      "refresh_token": refresh_token
                      }
            json.dump(tokens, f, indent=4)
            return True
            
            

if __name__ == "__main__":
    print(weather_by_city("Moscow,Russia"))
    # dropbox_files()
