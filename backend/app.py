from flask import Flask
from flask_cors import CORS
from models import User
from config import Config
from extensions import db, login_manager
from routes import register_blueprints
from utils.scheduler import init_scheduler

def create_app():
    app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
    app.config.from_object(Config)

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # match the blueprint endpoint

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    with app.app_context():
        db.create_all()

    register_blueprints(app)
    init_scheduler(app)

    from flask_cors import CORS

    CORS(app,
         supports_credentials=True,
         origins=["http://localhost:3000"])



    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
