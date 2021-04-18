import flask

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
  return "<h1>Basic Flask Server</h1><p>This is a test</p>"

# Routes
@app.route('/query', methods=['GET'])
def process_query():
  food_type, ingredients, price_range = '', '', ''
  if 'food_type' in request.args:
    food_type = request.args['food_type']
  if 'ingredients' in request.args:
    ingredients = request.args['ingredients']
  else:
    raise HTTPException(msg='Invalid URL params', response_code=400)
  if 'price_range' in request.args:
    price_range = request.args['price_range']
    
  # run cosine similarity thing

if __name__ == "__main__":
  app.run()