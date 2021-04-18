from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
import requests
import time

project_name = "Bon APPétit"
net_id = "Elina Hvirtsman: eh582, Julia Ng: jen67, Shirley Chen: sc2552, Luke Forsman: ltf25, Vincent Ferraiuolo: vpf6"

@irsystem.route('/', methods=['GET'])
def search():
	url='http://localhost:5000/query'
	params = {}
	dietary = request.args.get('dietary')
	params['ingredients'] = dietary
	#url += 'ingredients=' + dietary
	typeOfFood = request.args.get('type')
	#url += '&food_type=' + typeOfFood
	params['food_type'] = typeOfFood
 	# price = request.args.get('price')
	if not dietary:
		data = []
		output_message = ''
		return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)

	else:
		output_message = "Your search: " + dietary + ' ' + typeOfFood
		# time.sleep(5)
		data = requests.get(url, params).json()


		return render_template('results.html', output_message=output_message, data=data)



