from .auth import auth_bp
from .users import users_bp
from .entries import entries_bp
from .body_parts import body_parts_bp

def init_app(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(entries_bp)
    app.register_blueprint(body_parts_bp)