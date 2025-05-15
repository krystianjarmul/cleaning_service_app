import io

from django.conf import settings

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload


SCOPES = settings.GOOGLE_DRIVE_SCOPES
CREDENTIALS_FILE = settings.GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE
ROOT_FOLDER_ID = settings.GOOGLE_DRIVE_ROOT_FOLDER_ID


class GoogleDriveClient:

    def __init__(self, credentials_file_path: str = CREDENTIALS_FILE):
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_file_path,
            scopes=SCOPES
        )
        self.service = build('drive', 'v3', credentials=self.credentials)
        self.root_folder_id = ROOT_FOLDER_ID

    def download(self, file_id: str, output_path: str):
        request = self.service.files().get_media(fileId=file_id)

        fh = io.FileIO(output_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"  Download {int(status.progress() * 100)}%")

        print(f"{output_path} downloaded successfully!")

    def _get_file(self, filename: str, parent_id: str) -> dict:
        query = f"name = '{filename}' and mimeType != 'application/vnd.google-apps.folder' and trashed = false"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        return files[0] if files else None

    def _update_file(self, file_id: str, media: MediaIoBaseUpload) -> str:
        self.service.files().update(
            fileId=file_id,
            media_body=media
        ).execute()
        return file_id

    def _create_file(self, media: MediaIoBaseUpload, metadata: dict) -> str:
        uploaded_file = self.service.files().create(
            body=metadata,
            media_body=media,
            fields='id'
        ).execute()
        return uploaded_file['id']

    def upload(self, filename: str, file: io.BytesIO, parent_id: str) -> str:

        file_metadata = {
            'name': filename,
            'parents': [parent_id]
        }

        media = MediaIoBaseUpload(file, mimetype='application/octet-stream')

        file = self._get_file(filename=filename, parent_id=parent_id)

        if file:
            file_id =  self._update_file(file_id=file['id'], media=media)
            print(f"File {filename} updated successfully. (UPDATED)")
            return file_id

        file_id = self._create_file(media=media, metadata=file_metadata)
        print(f"File {filename} uploaded successfully. (CREATED)")
        return file_id

    def create_folder_structure(self, name: str) -> str:
        path_parts = name.strip('/').split('/')

        parent_id = self.root_folder_id
        for folder_name in path_parts:
            parent_id = self._get_or_create_folder(folder_name, parent_id)

        return parent_id

    def _get_or_create_folder(self, folder_name, parent_id):
        query = (
            f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' "
            f"and '{parent_id}' in parents and trashed = false"
        )
        results = self.service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        files = results.get('files', [])
        if files:
            return files[0]['id']

        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }

        folder = self.service.files().create(body=file_metadata, fields='id').execute()
        return folder['id']

    def create_root_folder(self, folder_name: str) -> str:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
        }

        folder = self.service.files().create(body=file_metadata, fields='id').execute()
        return folder['id']


    def convert_docx_to_pdf(self, file_id: str, filename: str, folder_id: str):

        pdf_name = filename.replace('.docx', '.pdf')

        copied_file = (
            self.service
            .files()
            .copy(
                fileId=file_id,
                body={'mimeType': 'application/vnd.google-apps.document'}
            )
            .execute()
        )
        copied_file_id = copied_file['id']

        request = (
            self.service
            .files()
            .export_media(
                fileId=copied_file_id,
                mimeType='application/pdf'
            )
        )

        pdf_metadata = {
            'name': pdf_name,
            'parents': [folder_id],
            'mimeType': 'application/pdf'
        }

        pdf_content = request.execute()

        media = MediaIoBaseUpload(
            io.BytesIO(pdf_content),
            mimetype='application/pdf'
        )

        file = self._get_file(filename=pdf_name, parent_id=folder_id)

        if file:
            file_id = self._update_file(file_id=file['id'], media=media)
        else:
            file_id = self._create_file(media=media, metadata=pdf_metadata)

        print(f"Converted {filename} to PDF and saved to destination folder")
        self.service.files().delete(fileId=copied_file_id).execute()

        return file_id


