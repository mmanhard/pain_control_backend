from flask import Flask, Response
from flask_cors import CORS
import os

class JSONResponse(Response):
    default_mimetype = 'application/json'

def create_app():
    from . import models, routes

    # Create and configure the app
    app = Flask(__name__)
    app.config.from_object(os.environ['APP_SETTINGS'])
    app.response_class = JSONResponse

    # Initialize the models and router.
    models.init_app(app)
    routes.init_app(app)

    # Enable cross-origin resource sharing.
    CORS(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

