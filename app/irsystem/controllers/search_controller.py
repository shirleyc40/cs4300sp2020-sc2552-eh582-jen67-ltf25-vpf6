from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "Bon APPétit"
net_id = "Elina Hvirtsman: eh582, Julia Ng: jen67, Shirley Chen: sc2552, Luke Forsman: ltf25, Vincent Ferraiuolo: vpf6"

@irsystem.route('/', methods=['GET'])
def search():
	dietary = request.args.get('dietary')
	typeOfFood = request.args.get('type')
	price = request.args.get('price')
	if not dietary:
		data = []
		output_message = ''
		return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)

	else:
		output_message = "Your search: " + dietary + ' ' + typeOfFood
		data = range(5)
		return render_template('results.html', output_message=output_message, data=data)



