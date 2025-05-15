# Distributed File Storage System Web Server

A Flask-based web interface for the distributed file storage system that provides user authentication, file management capabilities, and seamless integration with the metadata server. The web server allows users to upload, download, and manage files through an intuitive browser interface.

## Key Features

- **User Authentication**
Secure login and registration system with session management
- **Intuitive File Management**
Upload, download, and delete files through browser interface
- **Metadata Server Integration**
Communicates with the distributed storage backend system
- **Database Persistence**
User data and file references stored in PostgreSQL
- **Responsive Design**
Clean interface with CSS styling for various devices


## Tech Stack

- **Core**: Python 3.12, Flask 2.2.3
- **Database**: PostgreSQL with SQLAlchemy 2.0.29
- **Authentication**: Flask-Login 0.6.3
- **Forms**: Flask-WTF 1.2.2, WTForms 2.3.3
- **Containerization**: Docker, Docker Compose
- **Environment**: python-dotenv 1.0.0


## System Architecture

### Component structure

```
web_server/
├── .github/
│   ├── workflows/
│       └── main.yml
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
├── docker-compose.yml
├── Dockerfile
├── README.md
├── requirements.txt
└── run.py
```


## Quick Start

### Prerequisites

- Docker \& Docker Compose
- Metadata server running (see [dfs-metadata](https://github.com/Nexonm/dfs-metadata))
- Storage nodes running (see [dfs-storage-node](https://github.com/Nexonm/dfs-storage-node))


### Setup and Deployment

1. Clone the repository
```bash
git clone https://github.com/harutoyume/dfs-web-server.git
cd dfs-web-server
```

2. Create a `.env` file (or rename file.env to .env) with your configuration
```bash
cp file.env .env
# Edit .env as needed
```

3. Start the web server and database
```bash
docker-compose up --build
```

4. Access the web interface at http://localhost:9000 (or your configured port)

## Configuration

### Environment Variables

The web server uses environment variables for configuration. Below is the template for your `.env` file:

```env
# General config
SECRET_KEY='dev-key'
METADATA_SERVER_URL='http://<meta_data_host>:<meta_data_port>'

# Server config
WEB_ADDRESS='<web_server_host>'
WEB_PORT='<web_server_port>'

# Database config
DB_USER='postgres'
DB_PASSWORD='postgres'
DB_HOST='db'
DB_PORT='<data_base_port>'
DB_NAME='postgres'

# Docker config
CONTAINER_DB='<database_container_name>'
CONTAINER_WEB='<web_server_container_name>'
```

**Environment variables:**

- **General config**:
    - `SECRET_KEY`: Security key for Flask session encryption and CSRF protection. Use a random string for production.
    - `METADATA_SERVER_URL`: Full URL of your [dfs-metadata](https://github.com/Nexonm/dfs-metadata) server (e.g., `http://192.168.1.10:8080`)
- **Server config**:
    - `WEB_ADDRESS`: IP address the web server will bind to (use `0.0.0.0` to accept connections from any IP)
    - `WEB_PORT`: Port number for the web interface (e.g., `9000`)
- **Database config**:
    - `DB_USER`: PostgreSQL username (default: `postgres`)
    - `DB_PASSWORD`: PostgreSQL password (default: `postgres`)
    - `DB_HOST`: Database hostname (use `db` to reference the Docker service)
    - `DB_PORT`: PostgreSQL port (standard: `5432`)
    - `DB_NAME`: Database name (default: `postgres`)
- **Docker config**:
    - `CONTAINER_DB`: Name for your database container (e.g., `dfs_web_db`)
    - `CONTAINER_WEB`: Name for your web server container (e.g., `dfs_web_server`)

**Example configuration:**

```env
# General config
SECRET_KEY='dev-key'
METADATA_SERVER_URL='http://10.247.1.88:8080'

# Server config
WEB_ADDRESS='0.0.0.0'
WEB_PORT='9000'

# Database config
DB_USER='postgres'
DB_PASSWORD='postgres'
DB_HOST='db'
DB_PORT='5432'
DB_NAME='postgres'

# Docker config
CONTAINER_DB='dfs_web_db'
CONTAINER_WEB='dfs_web_server'
```

## Usage

### User Registration and Login

1. Navigate to `/register` to create a new account
2. Log in with credentials at `/login`

### File Management

1. Upload files through the upload interface
2. View and manage your files in the file list
3. Download or delete files as needed

## Integration

The web server integrates with the [Distributed File Storage System Metadata Server](https://github.com/Nexonm/dfs-metadata) specified in the `METADATA_SERVER_URL` environment variable.

Before using the web interface, ensure that:

1. The [dfs-metadata server](https://github.com/Nexonm/dfs-metadata) is properly configured and running
2. At least two [dfs-storage-nodes](https://github.com/Nexonm/dfs-storage-node) are running to support file chunk replication
3. The metadata server can successfully communicate with all storage nodes

For complete system setup, follow the documentation in the [dfs-metadata](https://github.com/Nexonm/dfs-metadata) repository first, then set up storage nodes using the [dfs-storage-node](https://github.com/Nexonm/dfs-storage-node) repository.

<div style="text-align: center">⁂</div>