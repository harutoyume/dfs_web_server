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
from app.services.db_models import User, File
from app.services import db_service

# Create application
app = Flask(__name__)
app.config.from_object(Config)

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Setup user-system manager
login_manager = LoginManager()
login_manager.init_app(app)

# Setup user loader to to reload the user object from the user ID stored in the session
@login_manager.user_loader
def load_user(user_id):
    db_session = db_service.create_session()
    return db_session.query(User).get(user_id)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        db_session = db_service.create_session()
        user = db_session.query(User).filter(User.email == form.email.data).first()

        if user and user.check_password(form.password.data):
            logger.info(f'User: "{user.username}"(id={user.id})\t->\tlogin')
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        
        else:
            return render_template('login.html', message="Wrong email or password!", form=form)
    
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logger.info(f'User: "{current_user.username}"(id={current_user.id})\t->\tlogout')
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

        logger.info(f'User: "{user.username}"\t->\tregister')

        return redirect('/login')

    return render_template('register.html', form=form)


@app.route('/files')
@login_required
def files():
    db_session = db_service.create_session()
    available_files = db_session.query(File).filter(File.user_id == current_user.id)

    logging.info(f'User: "{current_user.username}"(id={current_user.id})\t->\tfiles')
    return render_template('files.html', available_files=available_files)


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

            logger.info(f'User: "{current_user.username}"(id={current_user.id})\t->\tupload\t->\t"{filename}"')

            try:
                # Create metadata instance
                metadata_service = MetadataService(current_app.config['METADATA_SERVER_URL'])

                # Upload file to Meta Data server
                response, file_hash = metadata_service.upload_file(file_path)

                if response.get('status') != None:
                    raise Exception(f"Failed to upload file: {response}")

                # Make db session and make File instance
                db_session = db_service.create_session()
                file = File(
                    filename=filename,
                    filesize=response['fileSizeBytes'],
                    fileUUID=response['fileUUID'],
                    filehash=file_hash,
                    user_id=current_user.id
                )

                # Connect file with current user and add it in db
                db_session.add(file)
                db_session.commit()

                # Remove temporary file
                os.remove(file_path)

                flash(f'File {filename} uploaded successfully')
                logger.info(f"File uploaded: {filename}")

                return redirect(url_for('files'))
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

        # Get file from database
        db_session = db_service.create_session()
        file_data = db_session.query(File).filter(File.id == file_id and File.user_id == current_user.id).first()
        file_uuid = file_data.fileUUID
        filename = file_data.filename

        logger.info(f'User: "{current_user.username}"(id={current_user.id})\t->\tdownload\t->\t"{filename}"(id={file_data.id})')

        file_info = metadata_service.get_file_chunks(file_uuid)

        # Create temp file for assembled result
        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, filename)

        # Download and assemble chunks
        storage_service = StorageService()
        _, download_hash = storage_service.download_and_assemble_file(file_uuid, file_info, output_path)

        logger.info(f"File downloaded: {filename}")

        logger.info(f"Checking hash...")        
        if file_data.filehash != download_hash:
            raise Exception(f"Hash doesn't match: {file_data.filehash} != {download_hash}")

        # Send assembled file to user
        return send_file(output_path, as_attachment=True, download_name=filename)
    except Exception as e:
        flash(f'Error downloading file: try again, please')
        logger.error(f"Download error: {str(e)}")
        return redirect(url_for('files'))


@app.route('/delete/<file_id>')
@login_required
def delete(file_id):
    try:
        # Delete file from Metadata server
        metadata_service = MetadataService(current_app.config['METADATA_SERVER_URL'])
        
        # Get file from database
        db_session = db_service.create_session()
        file_data = db_session.query(File).filter(File.id == file_id and File.user_id == current_user.id).first()
        filename = file_data.filename
        file_uuid = file_data.fileUUID

        logger.info(f'User: "{current_user.username}"(id={current_user.id})\t->\tdelete\t->\t"{filename}"(id={file_data.id})')

        result = metadata_service.delete_file(file_uuid)

        if result:
            # Remove from database
            db_session.delete(file_data)
            db_session.commit()

            flash('File deleted successfully')
            logger.info(f"File deleted: {file_id}")
        else:
            flash('Error deleting file')

    except Exception as e:
        flash(f'Error: {str(e)}')
        logger.error(f"Delete error: {str(e)}")

    return redirect(url_for('files'))
