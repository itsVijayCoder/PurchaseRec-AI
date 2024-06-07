from apiflask import APIFlask
from blueprints.auth import auth_blueprint
from blueprints.analyse import analyse_blueprint

app = APIFlask(__name__)

app.register_blueprint(auth_blueprint, url_prefix='/api/v1/')
app.register_blueprint(analyse_blueprint, url_prefix='/api/v1/analyse')

if __name__ == '__main__': 
    app.run(host = '127.0.0.1', port = 8080, debug = True)