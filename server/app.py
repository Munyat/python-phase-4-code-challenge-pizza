#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class Restaurants(Resource):
    def get(self):
        restaurants = [restaurant.to_dict() for restaurant in Restaurant.query.all()]
        return make_response(jsonify(restaurants), 200)

class RestaurantById(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant:
            restaurant_data = {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "restaurant_pizzas": [
                    {
                        "id": rp.id,
                        "pizza": {
                            "id": rp.pizza.id,
                            "name": rp.pizza.name,
                            "ingredients": rp.pizza.ingredients
                        },
                        "pizza_id": rp.pizza_id,
                        "price": rp.price,
                        "restaurant_id": rp.restaurant_id
                    } for rp in restaurant.restaurant_pizzas
                ]
            }
            return make_response(jsonify(restaurant_data.to_dict()), 200)
        else:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)

    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response({"message": "successfully deleted"}, 204)
        else:
            return make_response({"error": "Restaurant not found"}, 404)

class Pizzas(Resource):
    def get(self):
        pizzas = [pizza.to_dict() for pizza in Pizza.query.all()]
        return make_response(jsonify(pizzas), 200)

class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        price = data.get('price')
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')

        errors = []

        if not price or not isinstance(price, (int, float)) or price < 1 or price > 30:
            errors.append("Price must be a number between 1 and 30")

        if not pizza_id:
            errors.append("Must provide a valid pizza_id")

        if not restaurant_id:
            errors.append("Must provide a valid restaurant_id")

        if errors:
            return make_response(jsonify({"errors": ['validation errors']}), 400)

        new_restaurant_pizza = RestaurantPizza(
            price=price,
            pizza_id=pizza_id,
            restaurant_id=restaurant_id
        )

        db.session.add(new_restaurant_pizza)
        db.session.commit()

        return make_response(jsonify(new_restaurant_pizza.to_dict()), 201)

api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantById, '/restaurants/<int:id>')  # Fixed endpoint path
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(debug=True)