from flask import Flask

app = Flask(__name__)

@app.route('/')
def public_page():
    return 'This is a public page'

if __name__ == '__main__':
    app.run(port=5001, debug=True)