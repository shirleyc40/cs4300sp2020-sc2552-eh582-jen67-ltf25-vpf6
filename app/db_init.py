from app import db
from flask import Flask, render_template, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
import json
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

class Restaurants(db.Model):
  __tablename__ = "restaurants"
  id = db.Column(db.String, primary_key=True)
  stars = db.Column(db.Float, nullable=False)
  reviewcount = db.Column(db.Integer, nullable=False)
  hours = db.Column(db.String, nullable=False)
  categories = db.Column(db.String, nullable=False)
  print("HEY THERE")
  def create(self):
    db.session.add(self)
    db.session.commit()
    return self

  def __init__(self, stars, hours, reviewcount, categories):
    self.stars = stars 
    self.hours = hours
    self.reviewcount = reviewcount
    self.categories = categories

  def __repr__(self):
    return '' % self.id

class MenuItems(db.Model):
  __tablename__ = "items"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String, nullable=False)
  description = db.Column(db.String, nullable=False)
  restaurant = db.Column(db.String, nullable=False)
  price = db.Column(db.Integer, nullable=False)

  def create(self):
    db.session.add(self)
    db.session.commit()
    return self

  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return '' % self.id

db.create_all()

# Populating DBs
with open('app/result.json') as f:
  data = json.load(f)
for name in data:
  
  restaurant_schema = RestaurantSchema()
  data[name]['hours'] = 'hey'
  print(data[name])
  # data[name]['id'] = name
  # r = Restaurants(stars=4.5, reviewcount=90, categories='hi')
  restaurant = restaurant_schema.load(data[name])
  restaurant.id = name
  result = restaurant_schema.dump(restaurant.create())

  