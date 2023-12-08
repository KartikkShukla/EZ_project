from flask import Flask, request, jsonify, render_template
from flask_security import Security, SQLAlchemyUserDatastore, login_required, current_user
from werkzeug.utils import secure_filename
from .models import db, User, UploadedFile
import os
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SECURITY_PASSWORD_SALT'] = 'your_salt'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = True
app.config['UPLOAD_FOLDER'] = 'uploads'

db.init_app(app)
security = Security(app, SQLAlchemyUserDatastore(db, User, None))

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Save file information to the database
        uploaded_file = UploadedFile(filename=filename, user=current_user)
        db.session.add(uploaded_file)
        db.session.commit()

        return jsonify({'message': 'File uploaded successfully'}), 200
    else:
        return jsonify({'message': 'File type not allowed'}), 400

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pptx', 'docx', 'xlsx'}

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_security import Security, SQLAlchemyUserDatastore, login_required, current_user, roles_required
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from .models import db, User, UploadedFile
import os
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SECURITY_PASSWORD_SALT'] = 'your_salt'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = True
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAIL_SERVER'] = 'your_mail_server'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'your_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'

db.init_app(app)
security = Security(app, SQLAlchemyUserDatastore(db, User, None))
mail = Mail(app)

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()

    # Send verification email
    send_verification_email(user)

    return jsonify({'message': 'User registered successfully. Check your email for verification.'}), 200

def send_verification_email(user):
    token = secrets.token_hex(16)
    user.token = token
    db.session.commit()

    msg = Message('Verify Your Email', sender='your_email@example.com', recipients=[user.email])
    msg.body = f'Click the following link to verify your email: {url_for("verify_email", token=token, _external=True)}'
    mail.send(msg)

@app.route('/verify/<token>')
def verify_email(token):
    user = User.query.filter_by(token=token).first()

    if user:
        user.active = True
        user.token = None
        db.session.commit()
        return jsonify({'message': 'Email verification successful'}), 200
    else:
        return jsonify({'message': 'Invalid token'}), 400

@app.route('/download/<file_id>')
@login_required
def download_file(file_id):
    uploaded_file = UploadedFile.query.get(file_id)

    if uploaded_file and uploaded_file.user == current_user:
        return jsonify({'download_link': f'/download/{file_id}', 'message': 'success'}), 200
    else:
        return jsonify({'message': 'Access denied'}), 403

@app.route('/download/<file_id>', methods=['POST'])
@login_required
def download_file_post(file_id):
    # Implement secure file download logic here
    return jsonify({'message': 'File downloaded successfully'}), 200

@app.route('/files')
@login_required
def list_files():
    files = UploadedFile.query.filter_by(user=current_user).all()
    file_list = [file.filename for file in files]
    return jsonify({'files': file_list}), 200

if __name__ == '__main__':
    app.run(debug=True)
