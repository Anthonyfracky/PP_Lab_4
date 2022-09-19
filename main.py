from flask import Flask
from waitress import serve

app = Flask(__name__)


@app.route('/api/v1/hello-world-13')
def variant():
    return 'Hello world 13'


if __name__ == '__main__':
    serve(app, host='localhost', port=8080)
    # app.run()

# http://localhost:8080/api/v1/hello-world-13
