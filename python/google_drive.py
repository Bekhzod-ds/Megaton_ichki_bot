import os
import mimetypes
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# Define the Drive access scope
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Load or refresh token
def get_drive_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('oauth_creds.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('drive', 'v3', credentials=creds)

# Upload file
def upload_file_to_drive(file_path, filename, folder_type):
    service = get_drive_service()

    # These are your folder IDs from your personal Drive
    FOLDER_IDS = {
        'Yetkazmalar': '1OgmyEQV9sUoCNANzkCNzT5bewEs21WD9',
        "To'lovlar": '16B5DMoyt30xmuKulkDk7GgkkYj7_6bdo'
    }

    folder_id = FOLDER_IDS[folder_type]
    mimetype = mimetypes.guess_type(file_path)[0]

    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }

    media = MediaFileUpload(file_path, mimetype=mimetype)
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    file_id = file.get('id')
    return f"https://drive.google.com/file/d/{file_id}/view"