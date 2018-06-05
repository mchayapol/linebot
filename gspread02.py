"""
Shows basic usage of the Sheets API. Prints values from a Google Spreadsheet.
"""
from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# Setup the Sheets API
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('sheets', 'v4', http=creds.authorize(Http()))

# Call the Sheets API
# SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
SPREADSHEET_ID = '1ywJhgyZJ_p3yJ8R6F9vlnCO5Ztt0iosuMEld2LvbOVI'

def readData():
    RANGE_NAME = 'Class Data!A2:E'
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                range=RANGE_NAME).execute()
    values = result.get('values', [])
    if not values:
        print('No data found.')
    else:
        print('Name, Major:')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print('%s, %s' % (row[0], row[4]))

range_name = 'Class Data!G:H'
values = [
    [1000,2000],
    [3000,4000]
]
body = {
    "values": values,
    "majorDimension": "ROWS"
}

result = service.spreadsheets().values().update(
    spreadsheetId=SPREADSHEET_ID, range=range_name,
    valueInputOption='USER_ENTERED',body=body).execute()
print('{0} cells updated.'.format(result.get('updatedCells')));

range_name = 'Class Data!G4' # =sum(G1:H3)
result = service.spreadsheets().values()
    .get(spreadsheetId=SPREADSHEET_ID,
        range=range_name).execute()
values = result.get('values', [])
for row in values:
    print(row[0])
