#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify
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
        restaurants = Restaurant.query.all()
        return [restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants], 200

class RestaurantDetail(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            return restaurant.to_dict(only=('id', 'name', 'address', 'restaurant_pizzas.pizza')), 200
        return {'error': 'Restaurant not found'}, 404
    
    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return {}, 204
        return {'error': 'Restaurant not found'}, 404

class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [pizza.to_dict(only=('id', 'name', 'ingredients')) for pizza in pizzas], 200

class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        price = data.get('price')
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')

        # Validate price range
        if not isinstance(price, int) or not (1 <= price <= 30):
            return {'errors': ['validation errors']}, 400

        # Ensure pizza and restaurant exist
        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)
        if not pizza or not restaurant:
            return {'errors': ['validation errors']}, 400

        new_restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)

        try:
            db.session.add(new_restaurant_pizza)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'errors': ['validation errors']}, 400

        return new_restaurant_pizza.to_dict(rules=('id', 'price', 'pizza', 'restaurant')), 201

api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantDetail, '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)


