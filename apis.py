from requests.api import request
import config
import json
import requests

def weather_by_city(city_name):
    weather_url = config.WEATHER_URL
    params = {
        "key": config.WEATHER_API_KEY,
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
        print(f"сервер недоступен! Ошибка:{err}")
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


def dropbox_files():
    app_key = config.DROPBOX_APP_KEY  # <-- CHANGE HERE
    app_secret = config.DROPBOX_APP_SECRET  # <-- CHANGE HERE
    data = {'grant_type': 'refresh_token',
            'refresh_token': '<REFRESH_TOKEN>'
            }

    response = requests.post('https://api.dropbox.com/oauth2/token', data=data, 
                              auth=(app_key, app_secret))
    print(response)
    
    # print('1. Go to: ' + authorize_url)
    # print('2. Click "Allow" (you might have to log in first)')
    # print('3. Copy the authorization code.')
    # code = input("Enter the authorization code here: ").strip()
    # access_token, user_id = flow.finish(code)
    # client = dropbox.client.DropboxClient(access_token)
    
    # metadata = client.metadata('/foldername')  # <-- CHANGE HERE
    # files = [content['path'].split('/')[-1] for content in metadata['contents']]
    # print(files)



        




if __name__ == "__main__":
    # print(weather_by_city("Moscow,Russia"))
