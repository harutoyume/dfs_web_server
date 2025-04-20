import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
    METADATA_SERVER_URL = os.environ.get('METADATA_SERVER_URL', 'http://localhost:8080')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB limit
