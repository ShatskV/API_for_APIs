from queries import get_token_from_base
from auth_db import  check_access_token, renew_access_token
from flask import current_app
from utils import requests_data
import fnmatch


def weather_by_city(city_name, timeout):
    weather_url = current_app.config['WEATHER_URL']
    params = {"key": current_app.config['WEATHER_API_KEY'],
              "q": city_name,
              "format": "json",
              "num_of_days": 1,
              "lang": "ru"
              }
  
    weather, status_code = requests_data(weather_url, params=params, timeout=timeout, method='get')
    if status_code != 200:
        return weather, status_code  

    if 'data' in weather:
        if 'current_condition' in weather['data']:
            try:
                return weather['data']['current_condition'][0], 200
            except(IndexError, TypeError) as err:
                return {"error": "Data error", "error_message":  str(err)}, 404
    return {"error": "Data is empty!"}, 404


def get_book(book_to_find, timeout):
    params = {"q": book_to_find, "maxResults": 3}
    books, status_code = requests_data(current_app.config["GOOGLE_BOOKS_API"], 
                                       params=params, timeout=timeout, method='get'
                                       )
    if status_code != 200:
        return books, status_code

    
    if books.get("items", False):
        return books['items'], 200
    else:
        return {"error": "data is empty"}, 404 


def dropbox_files(mask, path, timeout):
    access_token = check_access_token()

    if not access_token:
        refresh_token = get_token_from_base('refresh_token')
        if not refresh_token:
            return {"error": "No refresh token! please authenticate with code or new token!",
            "url":  current_app.config["DROPBOX_AUTH_URL"]
            }, 401
        else:
            refresh_token = refresh_token.token_value
            access_token, status = renew_access_token(refresh_token)
            if status != 200:
                return access_token, status

    headers = {'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
               }
    data = '{"path": "' + path +'"}'
    
    files, status_code = requests_data(current_app.config["DROPBOX_FILES_URL"], headers=headers, data=data, timeout=timeout)
    if status_code != 200:
        return files, status_code
    
    files = files.get('entries', False)
    list_files = []
    if files:
        for file in files:
            if fnmatch.fnmatch(file['name'], mask):
                list_files.append(file['name'])
        return list_files, 200
    else:
        return {'error': "server not available"}, 404
