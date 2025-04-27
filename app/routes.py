# Import dowloaded modules
from flask import Flask, render_template, request, redirect, url_for, flash, current_app, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

# Import built-in modules
import os
import logging
import tempfile

# Import project file
from config import Config
from app.services.storage_service import StorageService
from app.services.metadata_service import MetadataService
from app.services.form_service import RegisterForm, LoginForm
from app.services.db_models import User, File, UserFiles
from app.services import db_service

# Create application
app = Flask(__name__)
app.config.from_object(Config)

# Configure logging
logger = logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Setup user-system manager
login_manager = LoginManager()
login_manager.init_app(app)

# In-memory store for available files (in a real app, this would be a database)
available_files = []
downloaded_files = []

# Setup user loader to to reload the user object from the user ID stored in the session
@login_manager.user_loader
def load_user(user_id):
    db_session = db_service.create_session()
    return db_session.query(User).get(user_id)


@app.route('/')
def index():
    db_session = db_service.create_session()
    
    if current_user.is_authenticated:
        print("Found authorized user!")

    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        db_session = db_service.create_session()
        user = db_session.query(User).filter(User.email == form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        
        else:
            return render_template('login.html', message="Wrong email or password!", form=form)
    
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', message="Passwords doesn't match!", form=form)
        
        db_session = db_service.create_session()
        if db_session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', message="Provided email is already used!", form=form)
        
        user = User(
            username=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)

        db_session.add(user)
        db_session.commit()

        return redirect('/login')

    return render_template('register.html', form=form)


@app.route('/files')
@login_required
def files():
    return render_template('files.html',
                           available_files=available_files,
                           downloaded_files=downloaded_files)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            try:
                # Upload file to Meta Data server
                chunk_size = request.form.get('chunkSize', '400')
                metadata_service = MetadataService(current_app.config['METADATA_SERVER_URL'])

                response = metadata_service.upload_file(file_path, chunk_size)

                file_info = {
                    'id': response.get('fileUUID'),
                    'name': filename,
                    'size': os.path.getsize(file_path),
                    'uploaded_at': response.get('uploadedAt', 'now')
                }
                available_files.append(file_info)

                # Remove temporary file
                os.remove(file_path)

                flash(f'File {filename} uploaded successfully')
                logger.info(f"File uploaded: {filename}")

                return redirect(url_for('main.files'))
            except Exception as e:
                flash(f'Error: {str(e)}')
                logger.error(f"Upload error: {str(e)}")

                if os.path.exists(file_path):
                    os.remove(file_path)

    return render_template('upload.html')


@app.route('/download/<file_id>')
@login_required
def download(file_id: int):
    try:
        # Get file metadata and chunks from Metadata server
        metadata_service = MetadataService(current_app.config['METADATA_SERVER_URL'])
        file_info = metadata_service.get_file_chunks(file_id)

        filename = file_info.get('filename')

        # Create temp file for assembled result
        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, filename)

        # Download and assemble chunks
        storage_service = StorageService()
        storage_service.download_and_assemble_file(file_id, file_info, output_path)

        # Add to downloaded files list
        if not any(f['id'] == file_id for f in downloaded_files):
            downloaded_files.append({
                'id': file_id,
                'name': filename,
                'downloaded_at': 'now'  # In a real app, use datetime
            })

        logger.info(f"File downloaded: {filename}")

        # Send assembled file to user
        return send_file(output_path, as_attachment=True, download_name=filename)
    except Exception as e:
        flash(f'Error downloading file: {str(e)}')
        logger.error(f"Download error: {str(e)}")
        return redirect(url_for('main.files'))

# ну такого бэк пока не могёт
# @main.route('/delete/<file_id>', methods=['POST'])
# def delete(file_id):
#     try:
#         # Delete file from Metadata server
#         metadata_service = MetadataService(current_app.config['METADATA_SERVER_URL'])
#         result = metadata_service.delete_file(file_id)
#
#         if result:
#             # Remove from our lists
#             global available_files, downloaded_files
#             available_files = [f for f in available_files if f['id'] != file_id]
#             downloaded_files = [f for f in downloaded_files if f['id'] != file_id]
#
#             flash('File deleted successfully')
#             logger.info(f"File deleted: {file_id}")
#         else:
#             flash('Error deleting file')
#
#     except Exception as e:
#         flash(f'Error: {str(e)}')
#         logger.error(f"Delete error: {str(e)}")
#
#     return redirect(url_for('main.files'))
