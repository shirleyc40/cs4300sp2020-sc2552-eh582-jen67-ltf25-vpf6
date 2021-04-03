from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "Bon APPétit"
net_id = "Elina Hvirstman: eh582, Julia Ng: jen67, Shirley Chen: sc2552, Luke Forsman: ltf25, Vincent Ferraiuolo: vpf6"

@irsystem.route('/', methods=['GET'])
def search():
	query = request.args.get('search')
	if not query:
		data = []
		output_message = ''
	else:
		output_message = "Your search: " + query
		data = range(5)
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)



