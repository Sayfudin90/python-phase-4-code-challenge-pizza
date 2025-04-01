#!/usr/bin/env python3

from app import app
from models import db, Restaurant, Pizza, RestaurantPizza
import random

# Seed the database with initial data
with app.app_context():
    # First, clear out existing data
    print("Cleaning up old data...")
    RestaurantPizza.query.delete()
    Restaurant.query.delete()
    Pizza.query.delete()
    
    # Create some restaurants
    print("Adding restaurants...")
    karens = Restaurant(name="Karen's Pizza Shack", address="address1")
    sanjays = Restaurant(name="Sanjay's Pizza", address="address2")
    kikis = Restaurant(name="Kiki's Pizza", address="address3")
    
    restaurants = [karens, sanjays, kikis]
    db.session.add_all(restaurants)
    db.session.commit()
    
    # Create some pizzas
    print("Adding pizzas...")
    emma = Pizza(name="Emma", ingredients="Dough, Tomato Sauce, Cheese")
    geri = Pizza(name="Geri", ingredients="Dough, Tomato Sauce, Cheese, Pepperoni")
    mel = Pizza(name="Melanie", ingredients="Dough, Sauce, Ricotta, Red peppers, Mustard")
    
    pizzas = [emma, geri, mel]
    db.session.add_all(pizzas)
    db.session.commit()
    
    # Link restaurants and pizzas
    print("Creating restaurant-pizza connections...")
    restaurant_pizzas = []
    
    # Give Karen's both Emma and Geri pizzas
    rp1 = RestaurantPizza(price=15, restaurant=karens, pizza=emma)
    rp2 = RestaurantPizza(price=17, restaurant=karens, pizza=geri)
    restaurant_pizzas.extend([rp1, rp2])
    
    # Give Sanjay's the Melanie pizza
    rp3 = RestaurantPizza(price=20, restaurant=sanjays, pizza=mel)
    restaurant_pizzas.append(rp3)
    
    # Give Kiki's a random pizza
    random_pizza = random.choice(pizzas)
    rp4 = RestaurantPizza(price=random.randint(10, 25), restaurant=kikis, pizza=random_pizza)
    restaurant_pizzas.append(rp4)
    
    # Add all the restaurant_pizzas to the database
    db.session.add_all(restaurant_pizzas)
    db.session.commit()
    
    print("Done seeding!")
    print(f"Added {Restaurant.query.count()} restaurants")
    print(f"Added {Pizza.query.count()} pizzas")
    print(f"Added {RestaurantPizza.query.count()} restaurant-pizza relationships")