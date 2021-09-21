from apis import weather_by_city, get_book, dropbox_files
from auth_db import delete_db_token, dropbox_get_new_tokens
from distutils.util import strtobool
from db_model import db
from flask import Flask
from flask_restful import Api, Resource, reqparse

from log_set import logger_config
import logging.config 


def create_app():
    logging.config.dictConfig(logger_config)
    logger = logging.getLogger("app_logger")

    app = Flask(__name__)
    app.config.from_pyfile("config.py")
    app.logger.addHandler(logger)
    api = Api(app)
    db.init_app(app)

    post_args = reqparse.RequestParser()
    post_args.add_argument("auth_type", default="authorization_code", choices=["refresh_token", "authorization_code"], 
                            case_sensitive=False, location="json", help="auth_type is required!")
    post_args.add_argument ("token_code", required=True, location="json", case_sensitive=True,
                            help="token or auth_code is required!")
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
    get_args.add_argument("path", default="")
    get_args.add_argument("timeout_w", default=app.config['TIMEOUT_API'])
    get_args.add_argument("timeout_b", default=app.config['TIMEOUT_API'])
    get_args.add_argument("timeout_d", default=app.config['TIMEOUT_API'])


    class Data_api(Resource):

        def get(self):
            args = get_args.parse_args()
            weather_on = strtobool(args['weather'])
            book_on = strtobool(args['book_find'])
            dropbox_on = strtobool(args['dropbox_files'])
            
            if weather_on:
                city = args['city']
                weather, status_code_weather = weather_by_city(city, args['timeout_w'])
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
                books_list, status_code_book = get_book(book, args['timeout_b'])
                responce['book_find'] = {"data": books_list, 
                                    "status_code": status_code_book
                                    }   
            ## поиск по файлам
            if dropbox_on:
                mask = args["mask"]
                path = args["path"] 
                files_list, status_code_db = dropbox_files(mask, path, args['timeout_d'])
                responce['dropbox_files'] = {"data": files_list,
                                            "status_code": status_code_db
                                            }
            if not responce:
                return {"error": "all services not available"}, 404
            return responce, 200
    

    class Auth_db(Resource):
        def post(self):
            args = post_args.parse_args()
            if args['auth_type'] == "authorization_code":
                message, status_code = dropbox_get_new_tokens(authorization_code=args['token_code'])
            else: 
                message, status_code = dropbox_get_new_tokens(refresh_token=args['token_code'])
            if status_code != 200:
                logger.warning(f"{status_code}: {message}")
                return message, status_code
            return {"message": "refresh_token was changed!"}, 200

        def get(self):
            return {"message": "url for autorization with code",
                    "auth_url": app.config['DROPBOX_AUTH_URL']}, 200

        def delete(self):
            message, status_code = delete_db_token()
            if status_code != 200: 
                logger.warning(f"{status_code}: {message}")
            return message, status_code

    api.add_resource(Data_api, "/api")
    api.add_resource(Auth_db, "/api/auth")
    

    return app
    