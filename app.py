from flask import Flask, render_template, redirect, url_for, request, jsonify, send_from_directory, send_file, flash
from flask import session as fsession
from flask_wtf.csrf import CSRFProtect
from flask_session import Session as FlaskSession
from models import GeneralInfo, Multimedia, Experience, Certification, Projects, User, Session as SessionUser
from database import DATABASE_URL, engine, Session, Base
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import date, timedelta
from itsdangerous import URLSafeTimedSerializer
from io import BytesIO
import os
import uuid
import datetime
import pyotp
import qrcode
import base64

"""-----------------------Declaration--------------------------"""
# Flask app
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MEDIA_FOLDER'] = os.path.join(os.path.dirname(__file__), 'media', 'multimedia')
app.config['CERTIFICATES_FOLDER'] = os.path.join(os.path.dirname(__file__), 'media', 'certificates')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'webm', 'mp3', 'wav'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB
app.config['SECURITY_PASSWORD_SALT'] = 'my_precious_two'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_COOKIE_HTTPONLY'] = True # Not accessible via JavaScript
app.config['SESSION_COOKIE_SECURE'] = False # Set to True if using https
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' # 'Lax' for development, 'Strict' for production
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60) # Set session lifetime to 60 minutes

FlaskSession(app)
csrf = CSRFProtect(app)


# Creating Database in case to be neccessary
"""----------------------------Basic Tools functions ----------------------------"""

Base.metadata.create_all(bind=engine)

def filter_file_multimedia(filename):
    # Check if the file is allowed on the correct extensions multimedia
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

def get_session_user(session):
    user = session.query(User).filter_by(id=fsession.get('user_id')).first()
    return user

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in fsession:
            flash('You need to log in first.')
            print("User not logged in")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def generate_reset_token(email):
    
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

def verify_reset_token(token):

    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=3600)
        return (True, email)
    except Exception as e:
        print("Error:", e)
        return (False, None)

def otp_validator(otp_code, user):

    if otp_code and user.OTP:
        otp_user = pyotp.TOTP(user.OTP)
        validating_otp = otp_user.verify(otp_code)
        # Aqui deberia de desencriptar el otp para verificarlo 
        return validating_otp
    elif user.OTP is None:
        return True
    elif (otp_code is None and user.OTP is not None):
        return False


def exists_otp(user):
    # Check if the user has OTP enabled
    return True if user.OTP else False

def get_client_ip():
    
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        ip = request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
    elif request.environ.get('HTTP_X_REAL_IP'):
        ip = request.environ['HTTP_X_REAL_IP']
    else:
        ip = request.remote_addr
    
    return ip

def get_user_agent():
    return request.headers.get('User-Agent', 'Unknown')

"""-----------------------Login and Sessions--------------------------"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    #token = generate_reset_token('fake@mail.com')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        otp_code = request.form['otp']
        
        session = Session()
        user_to_login = session.query(User).filter_by(username=username).first()
        if user_to_login is None:
            user_to_login = session.query(GeneralInfo).filter_by(email=username).first()
            if user_to_login is not None:
                user_to_login = user_to_login.user
            else:
                return render_template('login/login.html', message='Invalid User/Password!')

        otp = otp_validator(otp_code, user_to_login)
        validating_login = (
            user_to_login and 
            check_password_hash(user_to_login.password, password) and 
            (not user_to_login.OTP or otp) 
        )
        if validating_login:
            flash('Login Successfully here!')
            if isinstance(user_to_login, User):
                user_to_login.last_login = datetime.datetime.now()
            elif isinstance(user_to_login, GeneralInfo):
                user_to_login.user.last_login = datetime.datetime.now()
            session.commit()
            fsession['user_id'] = str(user_to_login.id)
            fsession['username'] = str(user_to_login.username)
            session.close()
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username/password or OTP')
            session.close()
            return render_template('login/login.html', message='Invalid User/Password or OTP Code if enable!')
    
    if request.method == 'GET' and fsession.get('user_id'):

        return redirect(url_for('dashboard'))

    return render_template('login/login.html')

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    session = Session()
    user = get_session_user(session)
    exists_current_session = session.query(SessionUser).filter_by(
        user_id = user.id,
        is_active = True
    ).order_by(SessionUser.created_at.desc()).first()
    exists_current_session.is_active = False
    session.commit()
    session.close()
    fsession.pop('user_id', None)
    fsession.pop('username', None)
    fsession.clear()

    return redirect(url_for('login'))

@app.before_request
def security_middleware():

    # Not take public routes
    session = Session()
    user = get_session_user(session)
    public_points = ['login', 'reset_password', 'recovery_password', 'create_new_user', 'get_user']
    endpoints_validator = request.endpoint in public_points
    # Save First or another time in session database
    ip_client = get_client_ip()
    user_agent = get_user_agent()

    # Get Ip address
    # Get User Agent
    # and the logic of session security middleware
    """
    if usersession not exists created for the first time,
    if exists and the expired is true delete the activation to 0 a drop fsession.
    Set async function to drop expired sessions.
    """
    # Usuario logueado y con sesion abierta.
    if user:
        exists_current_session = session.query(SessionUser).filter_by(
            user_id = user.id,
            is_active = True
        ).order_by(SessionUser.created_at.desc()).first()

        time_today = datetime.datetime.now()
        if exists_current_session:
            if (exists_current_session.expires_at < time_today):
                exists_current_session.is_active = False
                session.commit()
                session.close()
                print("Usuario debe desloguearse!")
                logout()
            else:
                print('Usuario aun puede seguir logueado, finaliza a las:', exists_current_session.expires_at )
                return None

        else:
            session_user = SessionUser(
                user_id = user.id,
                created_at = datetime.datetime.now(),
                last_activity = datetime.datetime.now(),
                is_active = True,
                ip_address = ip_client,
                expires_at = datetime.datetime.now() + timedelta(minutes=60),
                user_agent = user_agent,
            )
            session.add(session_user)
            session.commit()
            session.close() 
    else:
        # Usuario no logueado.
        print("Usuario debe Loguearse!")
    
        


"""-----------------------URLS--------------------------"""
@app.route('/', methods=['GET'])
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/aboutme', methods=['GET', 'POST'])
@login_required
def about_me():
    session = Session()
    general_info = session.query(GeneralInfo).get(1)

    if request.method == 'GET':
        session.close()
        if general_info:
            return render_template('about_me.html', general_info=general_info)
        else:
            return render_template('about_me.html', general_info=None)

    elif request.method == 'POST':
        if general_info:
            general_info.name = request.form['name']
            general_info.coname = request.form['coname']
            general_info.address = request.form['address']
            general_info.country = request.form['country']
            general_info.email = request.form['email']
            general_info.phone = request.form['phone']
            general_info.short_description = request.form['short_description']
            session.commit()
            session.refresh(general_info)
            session.close()
        else:
            new_info = GeneralInfo(
                name=request.form['name'],
                coname=request.form['coname'],
                address=request.form['address'],
                country=request.form['country'],
                email=request.form['email'],
                phone=request.form['phone'],
                short_description=request.form['short_description']
            )
            session.add(new_info)
            session.commit()
            session.refrest(new_info)
            session.close()

        session.close()
        return redirect(url_for('about_me'))
    

@app.route('/multimedia', methods=['GET', 'POST'])
@login_required
def multimedia():

    session = Session()
    #multimedia_files = session.query(Multimedia).all()
    multimedia_files = get_session_user(session).multimedias
    if request.method == 'GET':

        session.close()
        return render_template('multimedia/multimedia.html', multimedia_files=multimedia_files)

    elif request.method == 'POST':

        file = request.files['file']
        if request.files['file'] and filter_file_multimedia(file.filename):
            
            extension = file_extension(file.filename)
            filename = secure_filename(file.filename)
            new_name = str(uuid.uuid4())+'.'+extension
            file_path = os.path.join(app.config['MEDIA_FOLDER'], new_name)

            multimedia = Multimedia(
                filename=new_name,
                file_type=extension,
                created_at=datetime.datetime.now(),
                user = get_session_user(session)
            )
            
            session.add(multimedia)
            session.commit()
            session.close()            
            file.save(file_path)
            return redirect(url_for('multimedia'))


@app.route('/media/multimedia/<filename>')
@login_required
def uploaded_file(filename):
    file = os.path.join(app.config['MEDIA_FOLDER'], filename)
    #return send_file(file)
    # Evita ataques de directorio traversal
    return send_from_directory(app.config['MEDIA_FOLDER'], filename)

@app.route('/multimedia/delete/<filename>')
@login_required
def delete_file(filename):

    session = Session()
    file_to_delete = session.query(Multimedia).filter_by(filename=filename).first()
    absolute_path = os.path.join(app.config['MEDIA_FOLDER'], file_to_delete.filename)

    if os.path.exists(absolute_path):
        os.remove(absolute_path)

    multimedia_files = get_session_user(session).multimedias
    session.delete(file_to_delete)
    session.commit()
    session.close()

    return redirect(url_for('multimedia'))
    
    

@app.route('/experience', methods=['GET', 'POST'])
@login_required
def experience():
    session = Session()
    experiences = get_session_user(session).experiences
    session.close()
    return render_template('experience/experience.html', experiences=experiences, current_date=date.today())

@app.route('/new_experience', methods=['POST'])
@login_required
def new_experience():
    session = Session()
    start_date = datetime.datetime.strptime(request.form['start_date'], '%Y-%m-%d')
    end_date = datetime.datetime.strptime(request.form['end_date'], '%Y-%m-%d') if request.form['end_date'] else None
    new_experience = Experience(
        short_description = request.form["short_description"],
        long_description = request.form["long_description"],
        company = request.form["company"],
        position = request.form['position'],
        location = request.form['location'],
        aptitudes = request.form['aptitudes'],
        start_date = start_date,
        end_date = end_date,
        user = get_session_user(session)
    )
    session.add(new_experience)
    session.commit()
    session.refresh(new_experience)
    session.close()
    return redirect(url_for('experience'))

@app.route('/edit_experience/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_experience(id):
    # Set New view here and return to the main template
    session = Session()
    experience = session.query(Experience).get(id)
    if request.method == 'GET':
        session.close()
        return render_template('experience/edit_experience.html', experience=experience)
    
    elif request.method == 'POST':

        experience.short_description = request.form['short_description']
        experience.long_description = request.form['long_description']
        experience.company = request.form['company']
        experience.position = request.form['position']
        experience.location = request.form['location']
        experience.aptitudes = request.form['aptitudes']
        experience.start_data = datetime.datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        experience.end_date = datetime.datetime.strptime(request.form['end_date'], '%Y-%m-%d') if request.form['end_date'] else None
        session.commit()
        session.close()
        return redirect(url_for('experience'))

    return Experience.experience_as_json(session, id)

@app.route('/delete_experience/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_experience(id):
    session = Session()
    experience = session.query(Experience).get(id)
    session.delete(experience)
    session.commit()
    session.close()
    return redirect(url_for('experience'))

@app.route('/certificates', methods=['GET', 'POST'])
@login_required
def certificates():
    session = Session()
    certificates = get_session_user(session).certifications
    if request.method == 'GET':
        session.close()
        return render_template('certificates/certificates.html', certificates=certificates)

    elif request.method == 'POST':
        file = request.files['file']
        extension = file_extension(file.filename)
        filename = secure_filename(file.filename)
        new_name = str(uuid.uuid4()) + '.' + extension
        file_path = os.path.join(app.config['CERTIFICATES_FOLDER'], new_name)
        
        new_certification = Certification(
            title = request.form['title'],
            description = request.form['description'],
            filename = new_name,
            file_type = extension,
            upload_at = datetime.datetime.now(),
            user = get_session_user(session)
        ) 
        session.add(new_certification)
        session.commit()
        session.refresh(new_certification)
        session.close()
        file.save(file_path)
        return redirect(url_for('certificates'))

    return render_template('certificates/certificates.html')

@app.route('/certificates/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_certification(id):
    session = Session()
    certification_to_edit = session.query(Certification).get(id)
    if request.method == 'GET':
        session.close()
        return render_template('certificates/edit_certificates.html', certification=certification_to_edit)
    elif request.method == 'POST':
        certification_to_edit.title = request.form['title']
        certification_to_edit.description = request.form['description']
        session.commit()
        session.close()
        return redirect(url_for('certificates'))

@app.route('/certificates/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_certification(id):
    session = Session()
    certification_to_delete = session.query(Certification).filter_by(id=id).first()
    # Delete the certification record from the database
    absolute_path = os.path.join(app.config['CERTIFICATES_FOLDER'], certification_to_delete.filename)
    if os.path.exists(absolute_path):
        os.remove(absolute_path)
    session.delete(certification_to_delete)
    session.commit()
    session.close()
    
    return redirect(url_for('certificates'))

@app.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    session = Session()
    projects = get_session_user(session).projects
    if request.method == 'GET':
        session.close()
        return render_template('projects/projects.html', projects=projects, current_date=date.today())
    elif request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        init_date = datetime.datetime.strptime(request.form['init_date'], '%Y-%m-%d')
        end_date = datetime.datetime.strptime(request.form['end_date'], '%Y-%m-%d') if request.form['end_date'] else None
        aptitudes = request.form['aptitudes']
        new_project = Projects(
            title=title,
            description=description,
            init_date=init_date,
            end_date=end_date,
            aptitudes=aptitudes,
            user = get_session_user(session)
        )
        session.add(new_project)
        session.commit()
        session.close()
    return redirect(url_for('projects'))

@app.route('/projects/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    session = Session()
    project_to_edit = session.query(Projects).filter_by(id=id).first()
    if request.method == 'GET':
        session.close()
        return render_template('projects/edit_projects.html', project=project_to_edit)
    elif request.method == 'POST':
        project_to_edit.title = request.form['title']
        project_to_edit.description = request.form['description']
        project_to_edit.aptitudes = request.form['aptitudes']
        project_to_edit.init_date = datetime.datetime.strptime(request.form['init_date'], '%Y-%m-%d')
        project_to_edit.end_date = datetime.datetime.strptime(request.form['end_date'], '%Y-%m-%d') if project_to_edit.end_date else None
        session.commit()
        session.close()
        return redirect(url_for('projects'))

@app.route('/projects/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_project(id):
    session = Session()
    project_to_delete = session.query(Projects).filter_by(id=id).first()
    session.delete(project_to_delete)
    session.commit()
    session.close()
    return redirect(url_for('projects'))

@app.route('/pdf_generator', methods=['GET', 'POST'])
@login_required
def pdf_generator():
    return render_template('pdf_generator.html')



"""------------------------Config Site------------------------"""

@app.route('/configuration', methods=['GET'])
@login_required
def configuration_dashboard():
    session = Session()
    user = get_session_user(session)
    session.close()
    return render_template('configuration/configuration.html', user=user)


@app.route('/configuration/otp', methods=['GET'])
@login_required
def configuration_otp():
    session = Session()
    user = get_session_user(session)
    session.close()
    if user.OTP:
        return render_template('configuration/otp.html', user=user, qr_validator=True)
    else:
        return render_template('configuration/otp.html', user=user, qr_validator=False)

@app.route('/configuration/otp/show', methods=['GET', 'POST'])
@login_required
def show_qr_code():
    session = Session()
    user = get_session_user(session)
    if request.method == 'POST':
        user_OTP = pyotp.random_base32()
        otp_uri = pyotp.totp.TOTP(user_OTP).provisioning_uri(
            name=user.username, 
            issuer_name='CVOStriker OTP'
        )
        qr = qrcode.make(otp_uri)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        buffer.seek(0)
        session.close()

        qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return render_template('configuration/confirm_otp.html', user=user, qr_base64=qr_base64, otp_string=user_OTP)

@app.route('/configuration/otp/verify_otp_creation', methods=[ 'POST'])
@login_required
def verify_otp_creation():
    session = Session()
    user = get_session_user(session)
    password = request.form['password']
    code_otp = request.form['otp_code']
    otp_string = request.form['otp_string']
    password_check = check_password_hash(user.password, password)
    totp_by_user = pyotp.TOTP(otp_string)
    code_otp_is_valid = totp_by_user.verify(code_otp)

    if password_check and code_otp_is_valid:
        # Aqui el OTP deberia ir encriptado al guardarlo.
        user.OTP = otp_string
        user.otp_created_at = datetime.datetime.now()
        session.commit()
        session.close()
        return redirect(url_for('configuration_otp', message='OTP has been successfully configured!'))
    else:
        session.close()
        return "Invalid OTP code or password. Please try again.", 400


@app.route('/configuration/otp/delete', methods=['GET', 'POST'])
@login_required
def configuration_otp_delete():
    session = Session()
    user = get_session_user(session)

    if request.method == 'POST':
        session.close()
        return redirect(url_for('confirm_password', option='delete_otp'))
    else:
        session.close()
    

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        session = Session()
        user_email = session.query(GeneralInfo).filter_by(email=email).first()
        session.close()
        if user_email:
            token = generate_reset_token(email)
            print("TOKEN URL:", "http://localhost:5000/password_recovery/"+token)
            # Send email here with the token to url/password_recovery/<token>
            # For example, you can use Flask-Mail or any other email service
            return redirect(url_for('login'))
        else:
            message = "Email not found, please try again!"

        return render_template('login/reset_password.html', message=message)
    return render_template('login/reset_password.html')

@app.route('/password_recovery/<token>', methods=['GET', 'POST'])
def recovery_password(token):
    validation, email = verify_reset_token(token)
    if request.method == 'POST':
        if validation:
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']
            if new_password == confirm_password:
                session = Session()
                user_to_change_password = session.query(GeneralInfo).filter_by(email=email).first()
                user_to_change_password.user.password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=16)
                session.commit()
                session.close()
                return redirect(url_for('login'))
            else:
                print("Password do not match")
                return redirect(url_for('recovery_password', token=token))

        return render_template('login/login.html', message="Token were invalid or don't match your password, please try again recovery!")
    else:
        return render_template('login/recovery_password.html', token=token)

@app.route('/configuration/email_recovery', methods=['GET', 'POST'])
@login_required
def email_recovery():
    session = Session()
    user = get_session_user(session)
    email_recovery = user.general_info.email_recovery if user.general_info.email_recovery else ''
    session.close()
    if request.method == 'GET':
        return render_template('configuration/email_recovery.html', user=user, email_recovery=email_recovery)
    elif request.method == 'POST':
        fsession['email_recovery'] = request.form['email_recovery']
        return redirect(url_for('confirm_password', option='set_email_recovery'))

    
"""------------------------Confirm Password and Two auth method to change option value ------------------------"""

@app.route('/configuration/otp/confirmation', methods=['GET', 'POST'])
@login_required
def confirm_otp():
    session = Session()
    user = get_session_user(session)
    otp = request.form['otp']
    verification = otp_validator(otp, user)
    session.close()
    if verification:
        return True
    else:
        return False

@app.route('/configuration/confirm_password/<option>', methods=['GET', 'POST'])
@login_required
def confirm_password(option):
    session = Session()
    user = get_session_user(session)
    exists_user_otp = exists_otp(user)
    if request.method == 'GET':
        session.close()
        return render_template('password_confirmation/edit_or_confirm_password.html', option=option, otp_exists=exists_user_otp)

    elif request.method == 'POST':
        password = request.form['password']
        confirm = request.form['confirm']
        otp = otp_validator(request.form["otp"], user)
        checking_passwords = ( (password == confirm) and check_password_hash(user.password, password) and otp )

        if checking_passwords:
            ## There are the options where enable confirm password
            if option == 'delete_otp':
                user.OTP = None
                user.otp_created_at = None
                session.commit()
                session.close()
                # Enviar mail con otp configurado
                return redirect(url_for('configuration_otp', message='OTP has been deleted!'))
            elif option == 'edit_password':
                new_password = request.form['new_password']
                hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=16)
                user.password = hashed_password
                session.commit()
                session.close()
                # Enviar email cuando password se haya cambiado
                return redirect(url_for('dashboard', message='Password were changed succesfully!'))
            elif option == 'set_email_recovery':
                user.general_info.email_recovery = fsession.get('email_recovery')
                fsession.pop('email_recovery', None)
                session.commit()
                session.close()
                # Enviar email cuando email recovery se haya cambiado o creado
                return redirect(url_for('email_recovery', message='Email recovery has been set!'))
        else:
            session.close()
            return render_template(
                'password_confirmation/edit_or_confirm_password.html', 
                option=option, 
                message='Password do not match from backend, please try again!'
            )

"""------------------------Creation User------------------------"""

@app.route('/create_new_user', methods=['GET'])
def create_new_user():
    session = Session()
    hashed_password = generate_password_hash('admin_12345!!', method='pbkdf2:sha256', salt_length=16)
    user_info = User(username='admin', password=hashed_password)
    session.add(user_info)
    new_user = GeneralInfo(
        id = user_info.id,
        user = user_info,
        name = 'John',
        coname = 'Doe',
        address = 'Street ###',
        country = 'USA',
        email = 'fakemail@mail.com',
        phone = '123456789',
        short_description = 'Short description here!'
    )
    session.add(user_info)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    print("ID:", user_info.id)
    message = f"created user {user_info.username} with password: {user_info.password} with name: {user_info.general_info.name} and email: {user_info.general_info.email}"
    session.close()
    return jsonify({'Status': 'Success', 'Message': message}), 200

@app.route('/get_user', methods=['GET'])
def get_user():
    session = Session()
    #user = session.query(GeneralInfo).filter_by(id=1).first()
    try:
        user_info = session.query(User).get(1)
        user = session.query(GeneralInfo).get(1)
        information = {
            'id': user.id,
            'name': user.name,
            'coname': user.coname,
            'address': user.address,
            'country': user.country,
            'email': user.email,
            'phone': user.phone,
            'short_description': user.short_description,
            'username': user_info.username,
            'password': user_info.password,
            'email_recovery': user.email_recovery
        }
        session.close()
        return jsonify(information), 200
    except Exception as e:
        session.close()
        return jsonify({'error': str(e), 'Message': 'Set /create_new_user to create new one'}), 500

@app.route('/connection_status')
def connection_status():
    pool = engine.pool
    return jsonify({
        'pool_size': pool.size(),
        'checked_in': pool.checkedin(),
        'checked_out': pool.checkedout(),
        'overflow': pool.overflow(),
        'total_connections': pool.size() + pool.overflow(),
    })

if __name__ == '__main__':
    # Create the media folder if it doesn't exist
    if not os.path.exists(app.config['MEDIA_FOLDER']):
        os.makedirs(app.config['MEDIA_FOLDER'], mode=0o755, exist_ok=True)
    # Create the certificates folder if it doesn't exist
    if not os.path.exists(app.config['CERTIFICATES_FOLDER']):
        os.makedirs(app.config['CERTIFICATES_FOLDER'], mode=0o755, exist_ok=True)
    #app.run(port=5000, debug=True)
    app.run(port=5000, debug=False)