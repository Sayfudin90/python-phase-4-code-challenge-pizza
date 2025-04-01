#!/usr/bin/env python3

from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from flask_cors import CORS

# Import models
from models import db, Restaurant, Pizza, RestaurantPizza

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False  # Pretty print JSON

# Set up CORS and migrations
CORS(app)
migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def index():
    # TODO: Add more info about available endpoints
    return "Pizza Restaurant API - v1.0"

# Get all restaurants
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    # Convert to dict manually instead of using serializer
    result = []
    for r in restaurants:
        result.append({
            "id": r.id,
            "name": r.name,
            "address": r.address
        })
    
    # print(f"Returning {len(result)} restaurants")
    return make_response(jsonify(result), 200)

# Get one restaurant by ID
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    # Find the restaurant
    rest = Restaurant.query.filter_by(id=id).first()
    
    if not rest:
        error_response = {"error": "Restaurant not found"}
        return make_response(jsonify(error_response), 404)
    
    # Use the serializer for the detailed view
    return make_response(jsonify(rest.to_dict()), 200)

# Delete a restaurant
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    rest = Restaurant.query.filter_by(id=id).first()
    
    # Return error if restaurant doesn't exist
    if not rest:
        return make_response(
            jsonify({"error": "Restaurant not found"}),
            404
        )
    
    # Restaurant exists, so delete it
    try:
        db.session.delete(rest)
        db.session.commit()
        return make_response('', 204)
    except Exception as e:
        # Something went wrong
        db.session.rollback()
        return make_response(jsonify({"error": str(e)}), 500)

# Get all pizzas
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    all_pizzas = Pizza.query.all()
    pizza_list = []
    
    # Format each pizza
    for p in all_pizzas:
        pizza_dict = {
            "id": p.id,
            "name": p.name,
            "ingredients": p.ingredients
        }
        pizza_list.append(pizza_dict)
    
    return make_response(jsonify(pizza_list), 200)

# Create restaurant-pizza relationship
@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    # Get JSON data from request
    json_data = request.get_json()
    
    # Check if we got all the fields we need
    required_fields = ['price', 'pizza_id', 'restaurant_id']
    for field in required_fields:
        if field not in json_data:
            return make_response(
                jsonify({"errors": [f"Missing {field}"]}),
                400
            )
    
    # Get the price and IDs from the request
    price = json_data['price']
    pizza_id = json_data['pizza_id']
    restaurant_id = json_data['restaurant_id']
    
    # Make sure the restaurant exists
    restaurant = db.session.get(Restaurant, restaurant_id)
    if not restaurant:
        return make_response(
            jsonify({"errors": ["Restaurant not found"]}),
            404
        )
    
    # Make sure the pizza exists
    pizza = db.session.get(Restaurant, restaurant_id)
    if not pizza:
        return make_response(
            jsonify({"errors": ["Pizza not found"]}),
            404
        )
    
    # Create the relationship
    try:
        # Create new restaurant_pizza object
        rp = RestaurantPizza(
            price=price,
            pizza_id=pizza_id,
            restaurant_id=restaurant_id
        )
        
        # Add and commit to DB
        db.session.add(rp)
        db.session.commit()
        
        # Return the newly created object
        return make_response(jsonify(rp.to_dict()), 201)
    
    except ValueError:
        # Handle validation errors
        db.session.rollback()
        return make_response(
            jsonify({"errors": ["validation errors"]}),
            400
        )

# Run the app
if __name__ == '__main__':
    app.run(port=5555, debug=True)