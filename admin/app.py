from flask import Flask

app = Flask(__name__)

@app.route('/')
def dashboard():
    return 'This is a admin page'

if __name__ == '__main__':
    app.run(port=5002, debug=True)