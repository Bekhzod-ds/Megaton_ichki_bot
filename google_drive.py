import os
import mimetypes
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials

# Load service account and initialize Google Drive API
def get_drive_service():
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
    creds = Credentials.from_service_account_file(creds_path, scopes=['https://www.googleapis.com/auth/drive'])
    return build('drive', 'v3', credentials=creds)

# Upload file to Google Drive
def upload_file_to_drive(folder_type, filename, file_path):
    service = get_drive_service()

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
