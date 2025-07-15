import os
import gspread
from google.oauth2.service_account import Credentials

# 🔐 Get Sheet ID from Render env vars
SHEET_ID = os.environ.get("SHEET_ID")

def insert_screenshot_link(sheet_type, row_id, link):
    # Load credentials.json (must be uploaded as Secret File in Render)
    creds = Credentials.from_service_account_file("credentials.json")
    client = gspread.authorize(creds)

    # 📄 Open correct Google Sheet
    spreadsheet = client.open_by_key(SHEET_ID)

    # 🧾 Select sheet (tab)
    worksheet = spreadsheet.worksheet(sheet_type)  # 'Yetkazmalar' or 'Tolovlar'

    # 🧮 Row number (+1 because sheets are 1-indexed)
    row = int(row_id) + 1

    # 🔢 Column to update
    if sheet_type == "Yetkazmalar":
        col = 13  # Column M
    elif sheet_type == "Tolovlar":
        col = 5   # Column E
    else:
        raise ValueError("Unknown sheet type")

    # 🔗 Insert HYPERLINK formula (clickable 📷)
    formula = f'=HYPERLINK("{link}", "📷 Screenshot")'
    worksheet.update_cell(row, col, formula)
