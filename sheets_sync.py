from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pandas as pd

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = 'your_spreadsheet_id'  # You'll need to replace this
RANGE_NAME = 'Sheet1!A1'  # Adjust as needed

def sync_to_sheets():
    # Load credentials
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json',  # You'll need to get this from Google Cloud Console
        SCOPES
    )
    creds = flow.run_local_server(port=0)
    
    # Create Sheets API service
    service = build('sheets', 'v4', credentials=creds)
    
    # Read local CSV
    df = pd.read_csv('updated_order_list.csv')
    
    # Convert DataFrame to values list
    values = [df.columns.values.tolist()] + df.values.tolist()
    
    # Update Google Sheet
    body = {
        'values': values
    }
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption='RAW',
        body=body
    ).execute()

if __name__ == '__main__':
    sync_to_sheets()