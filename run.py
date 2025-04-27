# Import project files
from app.routes import app
from app.services import db_service

if __name__ == '__main__':
    db_service.global_init()
    app.run(host='0.0.0.0', debug=True)
