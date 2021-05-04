from apiclient import discovery, errors
from httplib2 import Http
from oauth2client import client, file, tools
from googleapiclient import errors
import csv

def get_api_services():
    # define credentials and client secret file paths
    credentials_file_path = './credentials/credentials.json'
    clientsecret_file_path = './credentials/client_secret_347999455336-aulmc59fl0h5r5nm8a1dfao58c55ukns.apps.googleusercontent.com.json'

    # define scope
    SCOPE = 'https://www.googleapis.com/auth/drive'

    # define store
    store = file.Storage(credentials_file_path)
    credentials = store.get()

    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(clientsecret_file_path, SCOPE)
        credentials = tools.run_flow(flow, store)

    # define API service
    http = credentials.authorize(Http())
    drive = discovery.build('drive', 'v3', http=http)
    sheets = discovery.build('sheets', 'v4', credentials=credentials)

    return drive, sheets

def get_spreadsheet_id(api_service, spreadsheet_name):
    results = []
    page_token = None

    while True:
        try:
            param = {'q': 'mimeType="application/vnd.google-apps.spreadsheet"'}

            if page_token:
                param['pageToken'] = page_token

            files = api_service.files().list(**param).execute()
            results.extend(files.get('files'))

            # Google Drive API shows our files in multiple pages when the number of files exceed 100
            page_token = files.get('nextPageToken')

            if not page_token:
                break

        except errors.HttpError as error:
            print(f'An error has occurred: {error}')
            break

    spreadsheet_id = [result.get('id') for result in results if result.get('name') == spreadsheet_name][0]

    return spreadsheet_id

def sheet_to_json(sheets_instance, spreadsheet_id, sheet_name):
    result = sheets_instance.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_name).execute()
    
    d = {}
    for i, res in enumerate(result.get('values')):
    	if i > 0:
    		d[res[0]] = res[1]
    return d

def get_ingredients():
	spreadsheet_name = 'recipe_ingredients'
	sheet_name = 'Sheet1'
	drive, sheets = get_api_services()
	spreadsheet_id = get_spreadsheet_id(drive, spreadsheet_name)
	return sheet_to_json(sheets, spreadsheet_id, sheet_name)









