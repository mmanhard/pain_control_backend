from flask import Flask

def create_app():
    from . import models, routes

    # Create and configure the app
    app = Flask(__name__)
    app.config.from_object('config')

    models.init_app(app)
    routes.init_app(app)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

