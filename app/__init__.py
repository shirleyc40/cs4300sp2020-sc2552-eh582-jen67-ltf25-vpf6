# Gevent needed for sockets
from gevent import monkey
monkey.patch_all()
from Data_BoolSearch import *

# Imports
import os
from flask import Flask, render_template, make_response, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
import json
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

from collections import Counter
import re

# Configure app
socketio = SocketIO()
app = Flask(__name__)
app.config.from_object(os.environ["APP_SETTINGS"])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]

# DB
db = SQLAlchemy(app)

# Tables
class Restaurants(db.Model):
  __tablename__ = "restaurants"
  id = db.Column(db.String, primary_key=True)
  stars = db.Column(db.Float, nullable=False)
  reviewcount = db.Column(db.Integer, nullable=False)
  hours = db.Column(db.String, nullable=False)
  categories = db.Column(db.String, nullable=False)

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
  restaurant = db.Column(db.String, db.ForeignKey("restaurants.id"))
  price = db.Column(db.String, nullable=False)

  def create(self):
    db.session.add(self)
    db.session.commit()
    return self

  def __init__(self, name, description, restaurant, price):
    self.name = name
    self.description = description
    self.restaurant = restaurant
    self.price = price

  def __repr__(self):
    return '' % self.id

db.create_all()

# Schemas
class RestaurantSchema(ModelSchema):
    class Meta:
        model = Restaurants
        sqla_session = db.session

    id = fields.String()
    stars = fields.Number(required=True)
    reviewcount = fields.Number(required=True)
    hours = fields.String(required=True)
    categories = fields.String(required=True)


class MenuItemsSchema(ModelSchema):
    class Meta:
        model = MenuItems
        sqla_session = db.session

    id = fields.Number()
    name = fields.String(required=True)
    price = fields.String(required=True)
    description = fields.String(required=True)
    restaurant = fields.String()

# Populating Database
# with open('app/result.json') as f:
#   data = json.load(f)
# for name in data:
  
#   restaurant_schema = RestaurantSchema()
#   data[name]['hours'] = 'hey'
#   print(data[name])
#   # data[name]['id'] = name
#   # r = Restaurants(stars=4.5, reviewcount=90, categories='hi')
#   restaurant = restaurant_schema.load(data[name])
#   restaurant.id = name
#   result = restaurant_schema.dump(restaurant.create())

# Populating
@app.route('/populate', methods=['GET'])
def pop():
  with open('app/items.json') as f:
    data = json.load(f)
  for item in data:
    items_schema = MenuItemsSchema()
    item = items_schema.load(item)
    result = items_schema.dump(item.create())
  return make_response({})


# Routes
@app.route('/restaurants', methods=['GET'])
def test():
    get_restaurants = Restaurants.query.all()
    restuarant_schema = RestaurantSchema(many=True)
    restaurants = restuarant_schema.dump(get_restaurants)
    return make_response(jsonify({"restaurants": restaurants})) # return all doctors with their reviews

@app.route('/items', methods=['GET'])
def test2():
    get_items = MenuItems.query.all()
    items_schema = MenuItemsSchema(many=True)
    items = items_schema.dump(get_items)
    return make_response(jsonify({"items": items})) # return all doctors with their reviews

@app.route('/query', methods=['GET'])
def process_query():
  food_type, ingredients, price_range = '', '', ''
  if 'food_type' in request.args:
    food_type = request.args['food_type']
  if 'ingredients' in request.args:
    ingredients = request.args['ingredients']
  else:
    # raise HTTPException(msg='Invalid URL params', response_code=400)
    print("hey")
  if 'price_range' in request.args:
    price_range = request.args['price_range']
    if price_range == 'any':
      price_range = float('inf')
    else:
      price_range = int(request.args['price_range'])
  else:
    price_range = float('inf')

  # print(ingredients)
  query_toks = tokenize(ingredients)

  get_items = MenuItems.query.all()
  items_schema = MenuItemsSchema(many=True)
  items = items_schema.dump(get_items)

  inverted_idx = dict()

  prices = [0]*(len(items)+1)
  
  for item in items:
    id = int(item['id'])
    toks = tokenize(item['description'])
    counts = Counter(toks)
    for word, value in counts.items():
      if word in inverted_idx.keys():
        # inverted_idx[word].append((item['id'],float(re.findall("[^\$]*$", item['price'])[0]),value))
        inverted_idx[word].append((item['id'],value))
      else:
        # inverted_idx[word] = [(item['id'],float(re.findall("[^\$]*$", item['price'])[0]), value)]
        inverted_idx[word] = [(item['id'], value)]
      prices[id] = float(re.findall("[^\$]*$", item['price'])[0])

  result = {}
  for q_tok in query_toks:
    M = boolean_search(food_type, q_tok, inverted_idx, price_range, prices)

  if len(M) == 0:
    M = [float(x) for x in range(1, 2908)]

  for item_id in M:
    get_item = MenuItems.query.get(item_id)
    item_schema = MenuItemsSchema()
    # print(counter)
    items = item_schema.dump(get_item)
    restaurant = items['restaurant']
    if restaurant in result:
      if len(result[restaurant])<5:
        result[restaurant].append(items)
    else:
      result[restaurant] = [items]

  sorted_restaurants = [] 
  for rest in result:
    get_rest = Restaurants.query.get(rest)
    rest_schema = RestaurantSchema()
    restaurant = rest_schema.dump(get_rest)
    stars, review_count = restaurant['stars'], restaurant['reviewcount']
    sorted_restaurants.append((rest, stars, review_count))

  p = sorted(sorted_restaurants, key=lambda x: (-x[1], -x[2]))

  counter = 0
  total = []
  for rest, star, count in p:
    if counter < 5:
      total.append({rest+str(star): result[rest]})
    counter += 1
  return make_response({"res": total})



# Import + Register Blueprints
from app.accounts import accounts as accounts
app.register_blueprint(accounts)
from app.irsystem import irsystem as irsystem
app.register_blueprint(irsystem)

# Initialize app w/SocketIO
socketio.init_app(app)

# HTTP error handling
@app.errorhandler(404)
def not_found(error):
  return render_template("404.html"), 404
