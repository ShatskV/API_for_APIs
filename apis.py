from queries import get_token_from_base
from auth_db import  check_access_token, get_new_access_token, renew_access_token
from flask import current_app
import json
import fnmatch
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, time, timedelta
from db_model import Token
from requests import request, status_codes
from sqlalchemy.exc import SQLAlchemyError
import config
import requests


def weather_by_city(city_name, timeout):
    weather_url = current_app.config['WEATHER_URL']
    params = {"key": current_app.config['WEATHER_API_KEY'],
              "q": city_name,
              "format": "json",
              "num_of_days": 1,
              "lang": "ru"
              }
  
    # responce = requests.get(weather_url, params=params, timeout=1)
    weather, status_code = requests_data(weather_url, params=params, timeout=timeout, method='get')
    if status_code != 200:
        return weather, status_code  

    if 'data' in weather:
        if 'current_condition' in weather['data']:
            try:
                return weather['data']['current_condition'][0], 200
            except(IndexError, TypeError) as err:
                return {"error": "Data error:" + err}, 404
    return {"error": "Data is empty!"}, 404


def get_book(book_to_find, timeout):
    params = {"q": book_to_find, "maxResults": 3}
    try: 
        response = requests.get(current_app.config["GOOGLE_BOOKS_API"], params=params)
        response.raise_for_status()
        books = response.json()
    except (requests.RequestException, ValueError) as err:
        print(f"сервер поиска книг недоступен! Ошибка:{err}")
        return {"error": err}, 404
    
    if books.get("items", False):
        return books['items'], 200
    else:
        return {"error": "data is empty"}, 404 


def dropbox_files(mask, path, timeout):
    access_token = check_access_token()
    print(f'access_token:{access_token}')

    if not access_token:
        refresh_token = get_token_from_base('refresh_token')
        print(f"rf_tk: {refresh_token}")
        if not refresh_token:
            return {"error": "No refresh token! please authenticate with code or new token!",
            "url":  current_app.config["DROPBOX_AUTH_URL"]
            }, 401
        else:
            refresh_token = refresh_token.token_value
            access_token, status = get_new_access_token(refresh_token)
            if status != 200:
                return access_token, status

    print("--8"*30)
    headers = {'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                }
    # data = str({"path": str(path)})
    data = '{"path": "' + path +'"}'
    print(data)
    # data = '{"path": ""}'
    # data = '{"query": "foo"}'
    try:
        response = requests.post('https://api.dropboxapi.com/2/files/list_folder', headers=headers, data=data)
        files = response.json()
        response.raise_for_status()
    except (requests.RequestException, ValueError) as err:
        print(f"сервер авторизации dropbox недоступен! ошибка: {err} {response.status_code}")
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



def requests_data(url, params=None, headers=None, data=None,  auth=None, method='post', 
                  timeout=5):
    if method == 'post': 
        req_func = requests.post
    else:
        req_func = requests.get
    try: 
        responce = req_func(url, params=params, headers=headers, data=data,  auth=auth, 
                  timeout=timeout)
        result = responce.json()
        responce.raise_for_status()
    except ValueError as errv:
        current_app.logger.exception("Exc ValueError!")
        return {"error": "value error!", "error_message": errv}, 500
    except requests.exceptions.HTTPError as errh:
        current_app.logger.exception("Exc HTTPError!")
        return {"error": "Http Error!", "error_message": errh}, responce.status_code
    except requests.exceptions.Timeout as errt:
        current_app.logger.exception("Exc Timeout!")
        return {"error": "Timeout Error!", "error_message": errt}, 408
    except requests.exceptions.ConnectionError as errc:
        current_app.logger.exception("Exc ConnectionError!")
        return {"error": "Error Connecting:!", "error_message": errc}, 404
    except requests.exceptions.RequestException as err:
        current_app.logger.exception("Other requests.exception!")
        return {"error": "OOps: Something Else!", "error_message": err}, responce.status_code
    return result, 200


if __name__ == "__main__":
    print(weather_by_city("Moscow,Russia"))
    # dropbox_files()
