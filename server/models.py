from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

# Set up naming conventions for foreign keys
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

# Initialize SQLAlchemy
db = SQLAlchemy(metadata=metadata)

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = 'restaurants'

    # Basic columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    # Define relationships
    restaurant_pizzas = db.relationship(
        'RestaurantPizza', 
        back_populates='restaurant',
        cascade='all, delete-orphan'  # Delete related restaurant_pizzas when restaurant is deleted
    )
    
    # Use association proxy to access pizzas directly
    pizzas = association_proxy('restaurant_pizzas', 'pizza')
    
    # Prevent infinite recursion in serialization
    serialize_rules = ('-restaurant_pizzas.restaurant', '-restaurant_pizzas.pizza.restaurant_pizzas')

    def __repr__(self):
        return f"<Restaurant {self.id}: {self.name}>"

class Pizza(db.Model, SerializerMixin):
    __tablename__ = 'pizzas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)  # comma-separated list of ingredients

    # Define relationships
    restaurant_pizzas = db.relationship(
        'RestaurantPizza', 
        back_populates='pizza',
        cascade='all, delete-orphan'
    )
    
    # Use association proxy to access restaurants directly
    restaurants = association_proxy('restaurant_pizzas', 'restaurant')
    
    # Prevent infinite recursion in serialization
    serialize_rules = ('-restaurant_pizzas.pizza', '-restaurant_pizzas.restaurant.restaurant_pizzas')

    def __repr__(self):
        return f"<Pizza {self.id}: {self.name}>"

class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = 'restaurant_pizzas'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    
    # Foreign keys
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'), nullable=False)

    # Relationships
    restaurant = db.relationship('Restaurant', back_populates='restaurant_pizzas')
    pizza = db.relationship('Pizza', back_populates='restaurant_pizzas')
    
    # Prevent infinite recursion in serialization
    serialize_rules = ('-restaurant.restaurant_pizzas', '-pizza.restaurant_pizzas')

    # Add validation for price
    @validates('price')
    def validate_price(self, key, price):
        # Make sure price is between 1 and 30
        if price < 1 or price > 30:
            raise ValueError("Price must be between 1 and 30")
        return price

    def __repr__(self):
        return f"<RestaurantPizza {self.id}: R{self.restaurant_id}-P{self.pizza_id} ${self.price}>"