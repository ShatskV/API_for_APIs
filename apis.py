from os import access
from queries import get_token_from_base
from auth_db import  check_access_token, get_new_access_token, renew_access_token
from flask import current_app
import json
import fnmatch
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from db_model import Token
# from server import db
from requests import request
from sqlalchemy.exc import SQLAlchemyError
import config
# import dropbox
# from dropbox.exceptions import AuthError
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
        result = requests.get(weather_url, params=params, timeout=1)
        weather = result.json()
        result.raise_for_status()
    except ValueError as errv:
        return {"error": "value error: " + str(errv)}, 500
    except requests.exceptions.HTTPError as errh:
        return {"error": "Http Error: " + str(errh)}, result.status_code
    except requests.exceptions.ConnectionError as errc:
        return {"error": "Error Connecting:" + str(errc)}, 404
    except requests.exceptions.Timeout as errt:
        return {"error": "Timeout Error:" + str(errt)}, 408
    except requests.exceptions.RequestException as err:
        return {"error": "OOps: Something Else" + str(err)}, result.status_code
    

    if 'data' in weather:
        if 'current_condition' in weather['data']:
            try:
                return weather['data']['current_condition'][0], 200
            except(IndexError, TypeError) as err:
                return {"error": "Data error:" + err}, 404
    return {"error": "Data is empty!"}, 404


def get_book(book_to_find):
    params = {"q": book_to_find, "maxResults": 3}
    try: 
        response = requests.get(config.GOOGLE_BOOKS_API, params=params)
        response.raise_for_status()
        books = response.json()
    except (requests.RequestException, ValueError) as err:
        print(f"сервер поиска книг недоступен! Ошибка:{err}")
        return {"error": err}, 404
    # if books['items']:
    #     for book in books["items"]:
    #         volume = book["volumeInfo"]
    #         title = volume["title"]
    #         published = volume.get("publishedDate", "год издания неизвестен")
    #         description = volume.get("description", "описание отсутствует")
    #         print(f"{title} ({published}) | {description}")

    # else:
    #     return {"error": "data is empty"}, 404 
    # print(books)
    if books.get("items", False):
        return books['items'], 200
    else:
        return {"error": "data is empty"}, 404 



def dropbox_files(mask):
    
    # with open('tokens.json', 'r', encoding='utf-8') as f:
    #     tokens = json.load(f)
    #     access_token = tokens["access_token"]
    #     refresh_token = tokens["refresh_token"]
    #     exp_time = tokens['exp_time']
    # with dropbox.Dropbox(access_token) as dbx:
    # access_token = get_token_from_base('access_token')
    access_token = check_access_token()
    if not access_token:
        refresh_token = get_token_from_base('refresh_token')
        if not refresh_token:
            return {"error": "No refresh token! please authenticate with code or new token!",
            "url":  current_app.config["DROPBOX_AUTH_URL"]
            }, 401
        else:
            access_token, status = get_new_access_token(refresh_token)
            if status != 200:
                return access_token, status
    
    
    ##########################################
        # print(dbx.files_list_folder(path=''))
    # token_str = f'Bearer {access_token}'
    # headers = {'Authorization': token_str,
    #             'Content-Type': 'application/json',
    #             }

    # data = '{"query": "foo"}'

    # response = requests.post('https://api.dropboxapi.com/2/check/user', headers=headers, data=data)
    # print(response.json())

    # # token_str = f'Bearer {access_token}'
    # headers = {'Authorization': token_str}
    # data = '{"path": ""}'
                

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


    print("--8"*30)
    headers = {'Authorization': access_token,
                'Content-Type': 'application/json',
                }
    data ='{"path": ""}'
    try:
        response = requests.post('https://api.dropboxapi.com/2/files/list_folder', headers=headers, data=data)
        files = response.json()
        response.raise_for_status()
    except (requests.RequestException, ValueError) as err:
        print(f"сервер авторизации dropbox недоступен! ошибка: {err}")
        return {"error": "server is anavaible!"}, 404
    files = files.get('entries', False)
    # print(entries)
    list_files = []
    if files:
        for file in files:
            if fnmatch.fnmatch(file['name'], mask):
                list_files.append(file['name'])
        return list_files, 200
    else:
        return {'error': "server not available"}, 404




if __name__ == "__main__":
    print(weather_by_city("Moscow,Russia"))
    # dropbox_files()
