from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "keys.json"

creds = None
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1jBN-UhmwGr_zjj0pZ5J6Gci4JKlHaHmrcdG4YvsH608"

service = build("sheets", "v4", credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()
result = (
    sheet.values()
    .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet1!A1:C3")
    .execute()
)
values = result.get("values", [])

print(values)
