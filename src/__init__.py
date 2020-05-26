from flask import Flask, Response
from flask_cors import CORS

class JSONResponse(Response):
    default_mimetype = 'application/json'

def create_app():
    from . import models, routes

    # Create and configure the app
    app = Flask(__name__)
    app.config.from_object('config')
    app.response_class = JSONResponse

    models.init_app(app)
    routes.init_app(app)
    CORS(app)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

