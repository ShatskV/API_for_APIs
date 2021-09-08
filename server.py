import json
from distutils.util import strtobool
from logging import error
from flask import Flask, current_app, request, jsonify
from apis import weather_by_city, get_book, dropbox_files
from flask_restful import Api, Resource

app = Flask(__name__)
app.config.from_pyfile("config.py")
api = Api(app)
# @app.route("/", methods=["GET"])
# def get_data_api():
#     json 
def check_args(args_data):
    args_data = dict(args_data)
    for key, value in args_data.items():
        if key not in ['weather', 'book_find', 'dropbox_files', 'city', 'book', 'mask']:
            return False, None
        if key in ['weather', 'book_find', 'dropbox_files']:
            try:
                print(type(value))
                args_data[key] = strtobool(value.lower()) 
            except ValueError:
                return False, None
    return True, args_data
    

class Data_Api(Resource):
    def post():
        pass
        

    def get(self):
        # json_data = request.get_json()
        ## получаем данные погоды
        # print(request)
        args_data = request.args
        check, args_data = check_args(args_data) 
        if not check:
            return {"error": "wrong arguments!"}, 400
        weather_on = args_data.get('weather', True)
        book_on = args_data.get('book_find', True) 
        dropbox_on = args_data.get('drobpox_files', True)
       
        
        if weather_on:
            city = args_data.get('city', app.config["WEATHER_DEFAULT_CITY"])
            weather, status_code_weather = weather_by_city(city)
            responce = {"weather": {"status_code": status_code_weather,
                                    "data": weather 
                                    }
                        }
            if status_code_weather == 200:
                responce["weather"]['city'] = city
        else: 
            responce = {}
        ##поиск по книгам
        if book_on:
            book = args_data.get('book', app.config['DEFAULT_BOOK'])
            books_list, status_code_book = get_book(book)
            responce['book_find'] = {"data": books_list, 
                                "status_code": status_code_book
                                }   
        ## поиск по файлам
        if dropbox_on:
            mask = args_data.get("mask", "*")   
            files_list, status_code_db = dropbox_files(mask)
            responce['dropbox_files'] = {"data": files_list,
                                         "status_code": status_code_db
                                         }
        if not responce:
            return {"error": "all services not available"}, 404
        return responce, 200

    def delete():
        pass
api.add_resource(Data_Api, "/api")


if __name__ == "__main__":
    app.run(debug=True)