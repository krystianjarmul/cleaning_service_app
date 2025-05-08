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

        results = self.service.files().list(q=query,
                                            fields="files(id, name)").execute()
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

    def convert_docx_to_pdf_in_drive(self):
        # Configuration
        latest_month = self.find_latest_month_folder()

        if not latest_month:
            print("No month folders found")
            return

        print(f"Processing files in folder: {latest_month['full_path']}")

        source_folder_id = latest_month['id']
        destination_folder_id = self._get_or_create_folder('pdf', source_folder_id)

        # List files in source folder
        results = self.service.files().list(
            q=f"'{source_folder_id}' in parents and mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'",
            fields="files(id, name)").execute()
        files = results.get('files', [])

        for file in files:
            file_id = file['id']
            file_name = file['name']
            pdf_name = file_name.replace('.docx', '.pdf')

            copied_file = self.service.files().copy(
                fileId=file_id,
                body={'mimeType': 'application/vnd.google-apps.document'}
            ).execute()


            file_id = copied_file['id']
            # Export file as PDF
            request = self.service.files().export_media(fileId=file_id,
                                                         mimeType='application/pdf')

            # Create a new file in the destination folder
            pdf_metadata = {
                'name': pdf_name,
                'parents': [destination_folder_id],
                'mimeType': 'application/pdf'
            }

            # Use the exported PDF content directly
            pdf_content = request.execute()

            # Create the file in Drive
            self.service.files().create(
                body=pdf_metadata,
                media_body=MediaIoBaseUpload(io.BytesIO(pdf_content),
                                             mimetype='application/pdf')
            ).execute()

            # Optionally, delete the copied file
            self.service.files().delete(fileId=file_id).execute()

            print(f"Converted {file_name} to PDF and saved to destination folder")

    def find_latest_month_folder(self, path_type="customers", employee_name=None):
        """
        Find the latest month folder in the specified path structure.

        Args:
            drive_service: Authenticated Google Drive service
            root_folder_id: ID of the root folder
            path_type: Either "customers" or "employees"
            employee_name: Required only when path_type is "employees"

        Returns:
            Dictionary with folder information or None if not found
        """
        try:
            # Step 1: Find the proper starting folder (customers or employees)
            query = f"'{self.root_folder_id}' in parents and name='{path_type}' and mimeType='application/vnd.google-apps.folder'"
            results = self.service.files().list(q=query, fields="files(id, name)").execute()
            category_folders = results.get('files', [])

            if not category_folders:
                print(f"No {path_type} folder found")
                return None

            category_folder_id = category_folders[0]['id']

            # Step 2: For employees, we need to find the specific employee folder
            if path_type == "employees":
                if not employee_name:
                    print("Employee name is required for employee path")
                    return None

                query = f"'{category_folder_id}' in parents and name='{employee_name}' and mimeType='application/vnd.google-apps.folder'"
                results = self.service.files().list(q=query, fields="files(id, name)").execute()
                employee_folders = results.get('files', [])

                if not employee_folders:
                    print(f"No folder found for employee: {employee_name}")
                    return None

                folder_id = employee_folders[0]['id']
            else:
                folder_id = category_folder_id

            # Step 3: Find the latest year folder
            query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder'"
            results = self.service.files().list(q=query, fields="files(id, name)").execute()
            year_folders = results.get('files', [])

            # Sort years numerically in descending order
            year_folders.sort(key=lambda x: int(x['name']), reverse=True)

            if not year_folders:
                print("No year folders found")
                return None

            latest_year = year_folders[0]

            # Step 4: Find the latest month folder within the latest year
            query = f"'{latest_year['id']}' in parents and mimeType='application/vnd.google-apps.folder'"
            results = self.service.files().list(q=query,
                                                 fields="files(id, name)").execute()
            month_folders = results.get('files', [])

            # Sort months numerically in descending order
            month_folders.sort(key=lambda x: int(x['name']), reverse=True)

            if not month_folders:
                print(f"No month folders found in year {latest_year['name']}")
                return None

            latest_month = month_folders[0]

            # Construct path information
            if path_type == "employees":
                path = f"{path_type}/{employee_name}/{latest_year['name']}/{latest_month['name']}"
            else:
                path = f"{path_type}/{latest_year['name']}/{latest_month['name']}"

            return {
                'id': latest_month['id'],
                'name': latest_month['name'],
                'year': latest_year['name'],
                'path_type': path_type,
                'employee_name': employee_name if path_type == "employees" else None,
                'full_path': path
            }

        except Exception as e:
            print(f"Error finding latest month folder: {str(e)}")
            return None

    def empty_folder(self, folder_id):
        """
        Deletes all files and folders inside the specified folder, making it empty.

        Args:
            drive_service: Authenticated Google Drive service
            folder_id: ID of the folder to empty

        Returns:
            Number of items deleted
        """
        try:
            # Get all items (files and folders) in the folder
            query = f"'{folder_id}' in parents"
            results = self.service.files().list(
                q=query,
                fields="files(id, name)"
            ).execute()

            items = results.get('files', [])
            deleted_count = 0

            # Delete each item
            for item in items:
                self.service.files().delete(fileId=item['id']).execute()
                print(f"Deleted: {item['name']}")
                deleted_count += 1

            print(f"Successfully emptied folder. Deleted {deleted_count} items.")
            return deleted_count

        except Exception as e:
            print(f"Error emptying folder: {str(e)}")
            return 0


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

        file_id = copied_file['id']
        request = (
            self.service
            .files()
            .export_media(
                fileId=file_id,
                mimeType='application/pdf'
            )
        )

        pdf_metadata = {
            'name': pdf_name,
            'parents': [folder_id],
            'mimeType': 'application/pdf'
        }

        # Use the exported PDF content directly
        pdf_content = request.execute()

        # Create the file in Drive
        (
            self.service
            .files()
            .create(
                body=pdf_metadata,
                media_body=MediaIoBaseUpload(
                    io.BytesIO(pdf_content),
                    mimetype='application/pdf'
                )
            ).execute()
        )

        # Optionally, delete the copied file
        self.service.files().delete(fileId=file_id).execute()

        print(f"Converted {filename} to PDF and saved to destination folder")
