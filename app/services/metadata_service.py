import requests
import logging
from flask import current_app

logger = logging.getLogger(__name__)


class MetadataService:
    def __init__(self, base_url):
        self.base_url = base_url

    def upload_file(self, file_path, chunk_size=400):
        """Upload file to the Metadata server"""
        try:
            url = f"{self.base_url}/api/files/uploadChunked"

            with open(file_path, 'rb') as file:
                files = {'file': file}
                payload = {'chunkSize': str(chunk_size)}

                response = requests.post(url, files=files, data=payload)

                if response.status_code == 200:
                    logger.info(f"File uploaded successfully: {file_path}")
                    return response.json()
                else:
                    logger.error(f"Error uploading file: {response.text}")
                    raise Exception(f"Upload failed: {response.text}")
        except Exception as e:
            logger.error(f"Error in upload_file: {str(e)}")
            raise

    def get_file_chunks(self, file_uuid):
        """Get file metadata and chunks information from Metadata server"""
        try:
            url = f"{self.base_url}/api/storage/download"
            payload = {"fileUUID": file_uuid}

            response = requests.post(url, json=payload)

            if response.status_code == 200:
                logger.info(f"Retrieved file chunks for: {file_uuid}")
                return response.json()
            else:
                logger.error(f"Failed to get file chunks: {response.text}")
                raise Exception(f"Failed to get file chunks: {response.text}")
        except Exception as e:
            logger.error(f"Error in get_file_chunks: {str(e)}")
            raise

    def delete_file(self, file_uuid):
        """Delete file from the system"""
        try:
            url = f"{self.base_url}/api/files/{file_uuid}"

            response = requests.delete(url)

            if response.status_code == 200:
                logger.info(f"File deleted: {file_uuid}")
                return True
            else:
                logger.error(f"Failed to delete file: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error in delete_file: {str(e)}")
            return False
