## Web_server part 
#### architecture
```
web_server/
├── app/
│   ├── routes.py
│   ├── services/
│   │   ├── db_models.py
│   │   ├── db_service.py
│   │   ├── form_service.py
│   │   ├── metadata_service.py
│   │   └── storage_service.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── files.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   └── upload.html
│   └── static/
│       └── css/
│           └── style.css
├── .env
├── .gitignore
├── config.py
├── Dockerfile
├── README.md
├── requirements.txt
└── run.py
```

#### requirements
```
Flask==2.2.3
requests==2.28.2
Werkzeug==2.2.3
gunicorn==20.1.0
python-dotenv==1.0.0
WTFForms==2.3.3
Flask-WTF==1.2.2
Flask-Login==0.6.3
SQLAlchemy==2.0.29
sqlalchemy-serializer==1.4.22
```
