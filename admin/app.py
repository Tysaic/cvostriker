from flask import Flask, render_template, redirect, url_for, request, session, jsonify, send_from_directory, send_file
from models import GeneralInfo, Multimedia, Experience, Certification
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
app.config['CERTIFICATES_FOLDER'] = os.path.join(os.path.dirname(__file__), 'media', 'certificates')
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
    multimedia_files = session.query(Multimedia).all()

    if request.method == 'GET':
        session.close()
        return render_template('multimedia/multimedia.html', multimedia_files=multimedia_files)

    elif request.method == 'POST':
       
        if request.files['file'] and filter_file_multimedia(file.filename):
            file = request.files['file']
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
            session.close()            
            file.save(file_path)
            return redirect(url_for('multimedia'))


@app.route('/media/multimedia/<filename>')
def uploaded_file(filename):
    file = os.path.join(app.config['MEDIA_FOLDER'], filename)
    #return send_file(file)
    # Evita ataques de directorio traversal
    return send_from_directory(app.config['MEDIA_FOLDER'], filename)

@app.route('/multimedia/delete/<filename>')
def delete_file(filename):

    session = Session()
    file_to_delete = session.query(Multimedia).filter_by(filename=filename).first()
    absolute_path = os.path.join(app.config['MEDIA_FOLDER'], file_to_delete.filename)

    if os.path.exists(absolute_path):
        os.remove(absolute_path)

    multimedia_files = session.query(Multimedia).all()
    session.delete(file_to_delete)
    session.commit()
    session.close()

    return redirect(url_for('multimedia'))
    
    

@app.route('/experience', methods=['GET', 'POST'])
def experience():
    session = Session()
    experiences = session.query(Experience).all()
    return render_template('experience/experience.html', experiences=experiences)

@app.route('/new_experience', methods=['POST'])
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
        end_date = end_date
    )
    session.add(new_experience)
    session.commit()
    session.refresh(new_experience)
    session.close()
    return redirect(url_for('experience'))

@app.route('/edit_experience/<int:id>', methods=['GET', 'POST'])
def edit_experience(id):
    # Set New view here and return to the main template
    session = Session()
    experience = session.query(Experience).get(id)
    if request.method == 'GET':
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
def delete_experience(id):
    session = Session()
    experience = session.query(Experience).get(id)
    session.delete(experience)
    session.commit()
    session.close()
    return redirect(url_for('experience'))

@app.route('/certificates', methods=['GET', 'POST'])
def certificates():
    session = Session()
    certificates = session.query(Certification).all()
    if request.method == 'GET':
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
        ) 
        session.add(new_certification)
        session.commit()
        session.refresh(new_certification)
        session.close()
        file.save(file_path)
        return redirect(url_for('certificates'))

    return render_template('certificates/certificates.html')

@app.route('/certificates/edit/<int:id>', methods=['GET', 'POST'])
def edit_certification(id):
    session = Session()
    certification_to_edit = session.query(Certification).get(id)
    if request.method == 'GET':
        return render_template('certificates/edit_certificates.html', certification=certification_to_edit)
    elif request.method == 'POST':
        certification_to_edit.title = request.form['title']
        certification_to_edit.description = request.form['description']
        session.commit()
        session.close()
        return redirect(url_for('certificates'))

@app.route('/certificates/delete/<int:id>', methods=['GET', 'POST'])
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

if __name__ == '__main__':
    # Create the media folder if it doesn't exist
    if not os.path.exists(app.config['MEDIA_FOLDER']):
        os.makedirs(app.config['MEDIA_FOLDER'], mode=0o755, exist_ok=True)
    # Create the certificates folder if it doesn't exist
    if not os.path.exists(app.config['CERTIFICATES_FOLDER']):
        os.makedirs(app.config['CERTIFICATES_FOLDER'], mode=0o755, exist_ok=True)
    app.run(port=5002, debug=True)