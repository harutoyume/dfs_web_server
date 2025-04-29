# Import downloaded modules
import requests

# Import built-in modules
import logging
import tempfile
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class StorageService:
    def download_chunk(self, chunk_info):
        """Download a single chunk from a storage node"""
        chunk_uuid = chunk_info["chunkUUID"]
        chunk_index = chunk_info["chunkIndex"]
        hosts = chunk_info["hosts"]

        # Try each host until successful
        for host_info in hosts:
            host = host_info["host"]
            port = host_info["port"]

            try:
                url = f"http://{host}:{port}/api/chunk/download"
                payload = {
                    "fileUUID": self.file_uuid,
                    "chunkUUID": chunk_uuid,
                    "chunkIndex": chunk_index
                }

                logger.info(f"Downloading chunk {chunk_index} from {host}:{port}")
                response = requests.post(url, json=payload)

                if response.status_code == 200:
                    logger.info(f"Successfully downloaded chunk {chunk_index}")
                    return {
                        "index": chunk_index,
                        "data": response.content
                    }
                else:
                    logger.warning(f"Failed to download chunk from {host}:{port}: {response.text}")
            except Exception as e:
                logger.warning(f"Error downloading chunk from {host}:{port}: {str(e)}")

        # If all hosts failed
        raise Exception(f"Failed to download chunk {chunk_index} from any host")

    def download_and_assemble_file(self, file_uuid, file_info, temp_path):
        """Download all chunks and assemble them into a complete file"""
        self.file_uuid = file_uuid  # Store for use in download_chunk

        chunks = file_info["chunks"]
        chunks.sort(key=lambda x: x["chunkIndex"])  # Ensure chunks are in order

        # Create a temporary directory for chunks
        temp_dir = tempfile.mkdtemp()

        # Download chunks in parallel
        with ThreadPoolExecutor(max_workers=min(10, len(chunks))) as executor:
            downloaded_chunks = list(executor.map(self.download_chunk, chunks))

        # Sort chunks by index (in case they were returned out of order)
        downloaded_chunks.sort(key=lambda x: x["index"])

        # Assemble chunks into the final file
        with open(temp_path, 'wb') as output_file:
            for chunk in downloaded_chunks:
                output_file.write(chunk["data"])

        logger.info(f"Successfully assembled file: {file_info['filename']}")
        return temp_path
