from flask import Flask, render_template, redirect, url_for, request, session
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')

@app.route('/aboutme', methods=['GET', 'POST'])
def about_me():
    return render_template('about_me.html')

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


# Configuracion
## Gestion información personal
## Password manager & OTP
## API / Token



if __name__ == '__main__':
    app.run(port=5002, debug=True)