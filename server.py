# from flask_sqlalchemy import SQLAlchemy
from config import NASA_URL
# from db_model import Token, db
import json
from distutils.util import strtobool
from db_model import db
from logging import error
from flask import Flask, current_app, request, jsonify
from apis import weather_by_city, get_book, dropbox_files
from auth_db import delete_db_token
from auth_db import dropbox_get_new_tokens
# from queries import delete_tokens_from_base
# from flask_restful i
from flask_restful import Api, Resource, reqparse


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("config.py")
    api = Api(app)
    db.init_app(app)

    post_args = reqparse.RequestParser()
    post_args.add_argument("auth_type", default="authorization_code", choices=["refresh_token", "authorization_code"], 
                            case_sensitive=False, location="json", help="auth_type is required!")
    post_args.add_argument ("token_code", required=True, location="json", case_sensitive=True,
                            help="token or auth_code is required!")
    # print(app.config['SQLALCHEMY_DATABASE_URI'])
    help_arg= "wrong argument value!"
    arg_choice_bool = ["y", "yes", "t", "true", "on", "1", "n", "no", "f", "false", "off", "0"]

    get_args = reqparse.RequestParser()
    get_args.add_argument("weather", default="true", case_sensitive=False, help=help_arg,
                          choices=arg_choice_bool)
    get_args.add_argument("dropbox_files", default="true", case_sensitive=False, help=help_arg,
                          choices=arg_choice_bool)
    get_args.add_argument("book_find", default="true", case_sensitive=False, help=help_arg,
                          choices=arg_choice_bool)
    get_args.add_argument("book", default=app.config['DEFAULT_BOOK'])
    get_args.add_argument("city", default=app.config['WEATHER_DEFAULT_CITY'])
    get_args.add_argument("mask", default='*')
    get_args.add_argument("path", default='')



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
        def post(self):
            args = post_args.parse_args()
            if args['auth_type'] == "authorization_code":
                print(f"OPOP, {args['auth_type']}")
                message, status = dropbox_get_new_tokens(authorization_code=args['token_code'])
            else: 
                print("OPOPOP2")
                message, status = dropbox_get_new_tokens(refresh_token=args['token_code'])
            # current_app.config['NASA_URL']='fergop'
            if status != 200:
                return message, status
            return {"message": "refresh_token was changed!"}, 200

        def get(self):
            args = get_args.parse_args()

            # json_data = request.get_json()
            ## получаем данные погоды
            # print(request)
            # args_data = request.args
            # check, args_data = check_args(args_data) 
            # if not check:
            #     return {"error": "wrong arguments!"}, 400
            # weather_on = args_data.get('weather', True)
            # book_on = args_data.get('book_find', True) 
            # dropbox_on = args_data.get('drobpox_files', True)
            weather_on = strtobool(args['weather'])
            book_on = strtobool(args['book_find'])
            dropbox_on = strtobool(args['dropbox_files'])
            
            if weather_on:
                city = args['city']
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
                book = args['book']
                books_list, status_code_book = get_book(book)
                responce['book_find'] = {"data": books_list, 
                                    "status_code": status_code_book
                                    }   
            ## поиск по файлам
            if dropbox_on:
                mask = args["mask"]
                path = args["path"] 
                files_list, status_code_db = dropbox_files(mask, path)
                responce['dropbox_files'] = {"data": files_list,
                                            "status_code": status_code_db
                                            }
            if not responce:
                return {"error": "all services not available"}, 404
            return responce, 200

        def delete(self):
            result, status_code = delete_db_token()
            # result = "ok"
            # status_code = 200
            return result, status_code

    api.add_resource(Data_Api, "/api")

    return app
    