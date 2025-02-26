from flask import Flask, redirect

app = Flask(__name__)

@app.route('/')
def public():
    return redirect('http://127.0.0.1:5001/')

@app.route('/admin')
def admin():
    return redirect('http://127.0.0.1:5002')

if __name__ == '__main__':
    app.run(port=5000, debug=True)