from apiflask import APIFlask
from blueprints.auth import auth_blueprint
from blueprints.analyse import analyse_blueprint
from blueprints.ingest import ingest_blueprint
from flask_cors import CORS

app = APIFlask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})

app.register_blueprint(auth_blueprint, url_prefix='/api/v1/')
app.register_blueprint(analyse_blueprint, url_prefix='/api/v1/analyse')
app.register_blueprint(ingest_blueprint, url_prefix='/api/v1/ingest')

@app.route('/health', methods=['GET'])
def health_endpoint():
    return {'message': 'OK !'}

if __name__ == '__main__': 
    app.run(host = '0.0.0.0', port = 8080, debug = True)