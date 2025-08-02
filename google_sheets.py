import os
import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = os.environ.get("SHEET_ID")

def insert_screenshot_link(sheet_type, row_id, link):
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
    creds = Credentials.from_service_account_file(creds_path)
    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(SHEET_ID)
    worksheet = spreadsheet.worksheet(sheet_type)

    try:
        row = int(row_id) + 1
    except ValueError:
        raise ValueError(f"Invalid row ID: {row_id}")

    col = 13 if sheet_type == "Yetkazmalar" else 5
    formula = f'=HYPERLINK("{link}", "📷 Screenshot")'
    worksheet.update_cell(row, col, formula)
