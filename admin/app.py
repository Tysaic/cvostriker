from flask import Flask, render_template, redirect, url_for, request, session, jsonify, send_from_directory, send_file
from models import GeneralInfo, Multimedia
from database import DATABASE_URL, engine, Session, get_session, Base
from werkzeug.utils import secure_filename
import os
import uuid
import datetime


"""-----------------------Declaration--------------------------"""
# Flask app
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MEDIA_FOLDER'] = os.path.join(os.path.dirname(__file__), 'media', 'multimedia')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'webm', 'mp3', 'wav'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB
app.config['SECRET_KEY'] = os.urandom(24)



# Creating Database in case to be neccessary

Base.metadata.create_all(bind=engine)

def filter_file_multimedia(filename):
    # Check if the file is allowed on the correct extensions multimedia
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def file_extension(filename):

    return filename.rsplit('.', 1)[1].lower()

"""-----------------------Functions--------------------------"""
@app.route('/', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')

@app.route('/aboutme', methods=['GET', 'POST'])
def about_me():
    session = Session()
    general_info = session.query(GeneralInfo).get(1)

    if request.method == 'GET':
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
        
        return redirect(url_for('about_me'))




@app.route('/multimedia', methods=['GET', 'POST'])
def multimedia():
    session = Session()
    if request.method == 'GET':
        # Develop here the function to get the multimedia files from the database
        # and show them in the page
        multimedia_files = session.query(Multimedia).all()
        session.close()
        if multimedia_files:
            return render_template('multimedia.html', multimedia_files=multimedia_files)   
    
    if request.method == 'POST':

        if 'file' not in request.files:
            return jsonify({'error': 'There are not file in the request'}), 400
        
        file = request.files['file']

        if file and filter_file_multimedia(file.filename):

            extension = file_extension(file.filename)
            filename = secure_filename(file.filename)
            new_name = str(uuid.uuid4())+'.'+extension
            file_path = os.path.join(app.config['MEDIA_FOLDER'], new_name)

            multimedia = Multimedia(
                filename=new_name,
                file_type=extension,
                created_at=datetime.datetime.now()
            )
            
            session.add(multimedia)
            session.commit()            
            file.save(file_path)
            session.close()

            return jsonify({'status': 'Success'}), 200
        else:
            return jsonify({'error': 'File not allowed'}), 400

    return render_template('multimedia.html')   

@app.route('/media/multimedia/<filename>')
def uploaded_file(filename):
    file = os.path.join(app.config['MEDIA_FOLDER'], filename)
    return send_file(file)


@app.route('/experience', methods=['GET', 'POST'])
def experience():
    return render_template('experience.html')
    
@app.route('/certificates', methods=['GET', 'POST'])
def certificates():
    return render_template('certificates.html')

@app.route('/projects', methods=['GET', 'POST'])
def projects():
    return render_template('projects.html')

@app.route('/pdf_generator', methods=['GET', 'POST'])
def pdf_generator():
    return render_template('pdf_generator.html')

"""
@app.route('/create_new_user', methods=['GET'])
def create_new_user():
    session = Session()
    new_user = GeneralInfo(
        name = 'John',
        coname = 'Doe',
        address = 'Street ###',
        country = 'USA',
        email = 'fakemail@mail.com',
        phone = '123456789',
        short_description = 'Short description here!'
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    session.close()
    
    user = session.get(GeneralInfo, 1)
    return 'User created successfully! ID: {}'.format(user.id)

@app.route('/get_user', methods=['GET'])
def get_user():
    session = Session()
    #user = session.query(GeneralInfo).filter_by(id=1).first()
    user = session.query(GeneralInfo).get(1)
    information = {
        'id': user.id,
        'name': user.name,
        'coname': user.coname,
        'address': user.address,
        'country': user.country,
        'email': user.email,
        'phone': user.phone,
        'short_description': user.short_description
    }
    session.close()
    return information
"""

# Configuracion
## Gestion información personal
## Password manager & OTP
## API / Token



if __name__ == '__main__':
    if not os.path.exists(app.config['MEDIA_FOLDER']):
        os.makedirs(app.config['MEDIA_FOLDER'], mode=0o755, exist_ok=True)
    app.run(port=5002, debug=True)