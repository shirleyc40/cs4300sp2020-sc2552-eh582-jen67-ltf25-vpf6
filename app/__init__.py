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
  link = db.Column(db.String, nullable=False)
  address = db.Column(db.String, nullable=False)
  city = db.Column(db.String, nullable=False)

  def create(self):
    db.session.add(self)
    db.session.commit()
    return self

  def __init__(self, stars, hours, reviewcount, categories, link, address, city):
    self.stars = stars 
    self.hours = hours
    self.reviewcount = reviewcount
    self.categories = categories
    self.link = link
    self.address = address
    self.city = city

  def __repr__(self):
    return '' % self.id

class MenuItems(db.Model):
  __tablename__ = "items"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String, nullable=False)
  description = db.Column(db.String, nullable=False)
  restaurant = db.Column(db.String, db.ForeignKey("restaurants.id"))
  price = db.Column(db.String, nullable=False)
  city = db.Column(db.String, nullable=False)

  def create(self):
    db.session.add(self)
    db.session.commit()
    return self

  def __init__(self, name, description, restaurant, price, city):
    self.name = name
    self.description = description
    self.restaurant = restaurant
    self.price = price
    self.city = city

  def __repr__(self):
    return '' % self.id

class Reviews(db.Model):
  __tablename__ = "reviews"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  stars = db.Column(db.Float, nullable=False)
  restrictions = db.Column(db.String, nullable=False)
  foodtype = db.Column(db.String, nullable=False)
  restaurant = db.Column(db.String, db.ForeignKey("restaurants.id"))

  def create(self):
    db.session.add(self)
    db.session.commit()
    return self

  def __init__(self, stars, restrictions, foodtype, restaurant):
    self.stars = stars
    self.restrictions = restrictions
    self.foodtype = foodtype
    self.restaurant = restaurant

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
    link = fields.String(required=True)
    address = fields.String(required=True)
    city = fields.String(required=True)


class MenuItemsSchema(ModelSchema):
    class Meta:
        model = MenuItems
        sqla_session = db.session

    id = fields.Number()
    name = fields.String(required=True)
    price = fields.String(required=True)
    description = fields.String(required=True)
    restaurant = fields.String()
    city = fields.String()

class ReviewSchema(ModelSchema):
    class Meta:
        model = Reviews
        sqla_session = db.session

    id = fields.Number()
    stars = fields.Number(required=True)
    restrictions = fields.String(required=True)
    foodtype = fields.String(required=True)
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
  # with open('app/result.json') as f:
  #   data = json.load(f)

  # for name in data:
  #   restaurant_schema = RestaurantSchema()
  #   print(data[name])
  #   restaurant = restaurant_schema.load(data[name])
  #   restaurant.id = name
  #   result = restaurant_schema.dump(restaurant.create())

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
    res = []
    for rest in restaurants:
      res.append(rest['id'])
    return make_response(jsonify({"restaurants": res})) # return all doctors with their reviews

@app.route('/items', methods=['GET'])
def test2():
    get_items = MenuItems.query.all()
    items_schema = MenuItemsSchema(many=True)
    items = items_schema.dump(get_items)
    return make_response(jsonify({"items": items})) # return all doctors with their reviews

@app.route('/review', methods=['POST'])
def make_review():
  data = request.get_json()
  review_schema = ReviewSchema()
  review = review_schema.load(data) # load data from request into doctor schema
  result = review_schema.dump(review.create())
  return make_response(jsonify({"review": result}), 200) # return new doctor and success code


@app.route('/query', methods=['GET'])
def process_query():
  food_type, ingredients, price_range = '', '', ''
  if 'food_type' in request.args:
    food_type = request.args['food_type']
  if 'ingredients' in request.args:
    ingredients = request.args['ingredients']
    print("ingredients: ", ingredients)
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
  if 'city' in request.args:
    loc = request.args['city']

  get_items = MenuItems.query.filter(MenuItems.city==loc)
  items_schema = MenuItemsSchema(many=True)
  # items = items_schema.dump(get_items)
  items = items_schema.dump(get_items)

  # items = []
  # for item in blob:
  #   rest = item['restaurant'].lower()
  #   get_rest = Restaurants.query.get(rest)
  #   rest_schema = RestaurantSchema()
  #   restaurant = rest_schema.dump(get_rest)
  #   if restaurant['city'].lower() == city:
  #     items.append(item)
      
  inverted_idx = dict()

  print(len(items))
  temp = dict()
  npitems = np.array([])
  for i,item in enumerate(items):
    temp[item['id']] = item
    npitems = np.append(npitems, item)

  # print(npitems)
  prices = [0]*(9046)
  
  for i in range(1,9046):
    if i in temp:
      item = temp[i]
      toks = tokenize(item['description'])
      counts = Counter(toks)
      for word, value in counts.items():
        if word in inverted_idx.keys():
          inverted_idx[word].append((item['id'],value))
        else:
          inverted_idx[word] = [(item['id'], value)]
        prices[i] = float(re.findall("[^\$]*$", item['price'])[0])

  result = {}
  query_toks = tokenize(ingredients)
  food_toks = tokenize(food_type)

  veg = ['beef', 'pork', 'lamb', 'veal', 'chicken', 'duck', 'turkey', 'goose', 'sausage', 'pepperoni', 'ham', 'bacon', 'meatballs', 'prosciutto', 'fish']
  fish = ['salmon', 'tuna', 'tilapia']
  shellfish = ['crab', 'clams', 'mussels', 'shrimp', 'anchovies', 'scallops', 'calamari', 'lobster', 'oysters', 'crayfish', 'octopus', 'squid']
  cheese = ['mozzarella', 'parmesan', 'ricotta']
  dairy = ['cheese', 'butter', 'milk', 'cream', 'ice cream', 'yogurt'] + cheese
  gluten = ['bread', 'pasta', 'wheat', 'rye', 'spelt', 'barley', 'cereal', 'cookies', 'cake', 'crackers']
  restrictions = {
    'vegan': ['eggs', 'honey'] + veg + fish + shellfish + dairy,
    'vegetarian': veg + fish + shellfish,
    'shellfish': shellfish,
    'tree nuts': ['almond', 'brazil nut', 'cashew', 'chestnut', 'filbert', 'hazelnut', 'hickory nut', 'macadamia nut', 'pecan', 'pistachio', 'walnut'],
    'fish': fish,
    'cheese': cheese
  }
  restrictions.update(dict.fromkeys(['dairy', 'dairy free', 'lactose intolerant'], dairy))
  restrictions.update(dict.fromkeys(['gluten', 'gluten free'], gluten))

  for restriction in query_toks:
    if restriction in restrictions:
      if restriction == 'shellfish' or restriction == 'tree nuts' or restriction == 'dairy' \
      or restriction == 'gluten' or restriction == 'fish' or restriction == 'cheese':
        query_toks += restrictions[restriction]
      else:
        query_toks.remove(restriction)
        query_toks += restrictions[restriction]
        food_toks.append(restriction)

  M = main(food_toks,query_toks,price_range,npitems, inverted_idx, prices)
  # for q_tok in query_toks:
  #   M = boolean_search(food_type, q_tok, inverted_idx, price_range, prices)

  # if len(M) == 0:
  #   M = [float(x) for x in range(1,len(blob)+1)]
  # print("M: ", len(M[0]))
  if (len(M[0]) == 2907 and city == 'austin' and not M[1] == "no_err") or (len(M[0]) == 6138 and city == 'atlanta' and not M[1] == "no_err"):
    return make_response({"error": "No restaurants found"})

  else:
    for item in M[0]:
      get_item = MenuItems.query.get(item)
      item_schema = MenuItemsSchema()
      # print(counter)
      items = item_schema.dump(get_item)
      restaurant = items['restaurant']
      if restaurant in result:
        if len(result[restaurant]['items'])<5:
          result[restaurant]['items'].append(items)
      else:
        result[restaurant] = {}
        result[restaurant]['items'] = [items]

    sorted_restaurants = [] 
    for rest in result:
      get_rest = Restaurants.query.get(rest)
      rest_schema = RestaurantSchema()
      restaurant = rest_schema.dump(get_rest)
      stars, review_count = restaurant['stars'], restaurant['reviewcount']
      addr, link = restaurant['address'], restaurant['link']
      sorted_restaurants.append((rest, stars, review_count, addr, link))

    p = sorted(sorted_restaurants, key=lambda x: (-x[1], -x[2]))

    counter = 0
    total = []
    for rest, star, count, addr, link in p:
      if counter < 5:
        result[rest]['address'] = addr
        result[rest]['link'] = link
        result[rest]['stars'] = star
        total.append({rest: result[rest]})
      counter += 1
    if M[1] == "no_restr":
      # print("HERE")
      return make_response({"res": total, "error": "None of the items contained your dietary restrictions but here's what we found for your craving"})
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
