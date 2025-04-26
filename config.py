# Import dowloaded modules
from dotenv import load_dotenv

# Import built-in modules
import os

# Check if there's .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    # Load environment variables
    load_dotenv(dotenv_path)

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    METADATA_SERVER_URL = os.getenv('METADATA_SERVER_URL', 'http://localhost:8080')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB limit
