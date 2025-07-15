import os
import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = os.environ.get("SHEET_ID")

def insert_screenshot_link(sheet_type, row_id, link):
    # 🔐 Load credentials from Secret File (Render safe path)
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
    creds = Credentials.from_service_account_file(creds_path)
    client = gspread.authorize(creds)

    # 📄 Open Google Sheet
    spreadsheet = client.open_by_key(SHEET_ID)
    worksheet = spreadsheet.worksheet(sheet_type)

    # 🔢 Determine row
    try:
        row = int(row_id) + 1
    except ValueError:
        raise ValueError(f"Invalid row ID: {row_id}")

    # 📌 Determine column
    if sheet_type == "Yetkazmalar":
        col = 13
    elif sheet_type == "Tolovlar":
        col = 5
    else:
        raise ValueError(f"Unknown sheet type: {sheet_type}")

    # 🔗 Add Screenshot Link
    formula = f'=HYPERLINK("{link}", "📷 Screenshot")'
    worksheet.update_cell(row, col, formula)
