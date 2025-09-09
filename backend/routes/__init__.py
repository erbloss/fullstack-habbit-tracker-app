# registers route blueprints
from .auth_routes import auth_bp
from .habit_routes import habit_bp
from .log_routes import logs_bp
from .frontend_routes import frontend_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(habit_bp)
    app.register_blueprint(logs_bp)
    app.register_blueprint(frontend_bp)
