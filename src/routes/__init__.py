from flask import request, redirect

from .auth import auth_bp
from .users import users_bp
from .entries import entries_bp
from .body_parts import body_parts_bp

def init_app(app):

    @app.before_request
    def before_request():
        if not request.is_secure and request.headers.get('x-forwarded-proto') != 'https' and app.env != "development":
            url = request.url.replace("http://", "https://", 1)
            code = 301
            return redirect(url, code=code)

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(entries_bp)
    app.register_blueprint(body_parts_bp)