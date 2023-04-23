from googleapiclient.discovery import build
from google.oauth2 import service_account

SERVICE_ACCOUNT_FILE = 'Gemini_project_key.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = None
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = ''

service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

print('-------------')
print('Inputting Data into Google Sheets')

class GoogleSheetsService:
    def __init__(self, sheet_id):
        self.sheet_id = sheet_id

    def read_value(self, tab, col, row):
        value = sheet.values().get(spreadsheetId=self.sheet_id,
                                    range=f"{tab}!{col}{row}").execute()
        return value

    def update_value(self, tab, col, row, value):
        google_instance = sheet.values().update(spreadsheetId=self.sheet_id,
                                                range=f"{tab}!{col}{row}", valueInputOption="USER_ENTERED",
                                                body={"values": [[str(value)]]}).execute()

        return google_instance

    def bold_value(self, tab, col, row):
        pass

