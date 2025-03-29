from flask import Flask, render_template, redirect, url_for, request, session
import os
from models import GeneralInfo
from database import DATABASE_URL, engine, SessionLocal, get_session, Base

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SECRET_KEY'] = os.urandom(24)

# Creating Database in case to ne neccessary

Base.metadata.create_all(bind=engine)

@app.route('/', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')

@app.route('/aboutme', methods=['GET', 'POST'])
def about_me():
    session = SessionLocal()
    general_info = session.query(GeneralInfo).get(1)
    if request.method == 'GET':
        if general_info:
            return render_template('about_me.html', general_info=general_info)
        else:
            return render_template('about_me.html', general_info=None)




@app.route('/multimedia', methods=['GET', 'POST'])
def multimedia():
    return render_template('multimedia.html')

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
    session = SessionLocal()
    new_user = GeneralInfo(
        name = 'John',
        coname = 'Doe',
        address = 'Calle 123',
        country = 'Mexico',
        email = 'sockerpunch@mail.com',
        phone = '123456789',
        short_description = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    session.close()
    
    user = session.get(GeneralInfo, 1)
    return 'User created successfully! ID: {}'.format(user.id)

@app.route('/get_user', methods=['GET'])
def get_user():
    session = SessionLocal()
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
    
    app.run(port=5002, debug=True)