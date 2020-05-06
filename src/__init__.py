from flask import Flask

def create_app(test_config=None):
    from . import models, routes

    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = 'dev'
    app.config['MONGODB_SETTINGS'] = {
        'host': 'mongodb://localhost:27017/pain_control_v2'
    }

    models.init_app(app)
    routes.init_app(app)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

