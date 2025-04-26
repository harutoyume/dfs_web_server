## Web_server part 
#### architecture
```
web_server/
web_server/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── services/
│   │   ├── __init__.py  
│   │   ├── metadata_service.py
│   │   └── storage_service.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── files.html
│   │   └── upload.html
│   └── static/
│       └── css/
│           └── style.css
├── config.py
├── requirements.txt
├── run.py
└── Dockerfile
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
```
