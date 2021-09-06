import json
from logging import error
from flask import Flask, current_app, request, jsonify
from apis import weather_by_city
from flask_restful import Api, Resource
app = Flask(__name__)
app.config.from_pyfile("config.py")
api = Api(app)
# @app.route("/", methods=["GET"])
# def get_data_api():
#     json 

class Data_Api(Resource):
    def post():
        pass
        

    def get(self):
        # json_data = request.get_json()
        args_data = request.args
        city = args_data.get('city', 0)
        if city == 0:
            city = app.config["WEATHER_DEFAULT_CITY"]
        # else:
        #     city = json_data['city']
        weather =  weather_by_city(city)
        if weather:
            return weather, 200
        return "error", 404

    def delete():
        pass
api.add_resource(Data_Api, "/api")


if __name__ == "__main__":
    app.run(debug=True)