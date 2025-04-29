# Import downloaded modules
import requests

# Import built-in modules
import os
import hashlib
import logging

logger = logging.getLogger(__name__)


class MetadataService:
    def __init__(self, base_url):
        self.base_url = base_url

    def sha256(self, file_path):
        BUF_SUZE = 65536 # 64KB
        sha256 = hashlib.sha256()

        with open(file_path, 'rb') as f:
            while True:
                data = f.read(BUF_SUZE)
                if not data:
                    break
                sha256.update(data)
        
        return sha256.hexdigest()


    def upload_file(self, file_path):
        """Upload file to the Metadata server"""
        try:
            url = f"{self.base_url}/api/files/upload"
            logger.info(f"Sending request to {url=}")
            with open(file_path, 'rb') as file:
                files = {'file': (os.path.basename(file_path), file, 'application/octet-stream')}
                payload = {'fileHash': self.sha256(file_path)}

                response = requests.post(url, files=files, data=payload)

                if response.status_code == 200:
                    logger.info(f"File uploaded successfully: {file_path}")
                    logger.info(f"Response json: {response.json()}")
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
            url = f"{self.base_url}/api/files/download"
            payload = {"fileUUID": file_uuid}

            logger.info(f"{url=}\n\n{payload=}")

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
