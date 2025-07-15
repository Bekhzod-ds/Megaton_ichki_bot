import os
import pickle
import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SHEET_ID = "1B4fDbjokwUOIGy4oB1hnJaMU1mQzpw7CXQkTlGyiaYo"
TOKEN_FILE = "token.pickle"

def insert_screenshot_link(sheet_type, row_id, link):
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("❌ Google Drive token is missing or invalid.")

    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SHEET_ID)
    worksheet = spreadsheet.worksheet(sheet_type)

    row = int(row_id) + 1

    if sheet_type == "Yetkazmalar":
        col = 13  # Column M
    elif sheet_type == "To'lovlar":
        col = 5   # Column E
    else:
        raise ValueError("Unknown sheet type")

    # ✅ Insert formatted hyperlink
    worksheet.update_cell(row, col, f'=HYPERLINK("{link}"; "📷 Screenshot")')