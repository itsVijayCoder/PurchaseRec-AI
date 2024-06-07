from apiflask import APIFlask
from flask import request
from markupsafe import escape

app = APIFlask(__name__)

@app.route('/')
def hello():
    name = request.args.get('name', 'Human')
    return f'Hello, {escape(name)}'