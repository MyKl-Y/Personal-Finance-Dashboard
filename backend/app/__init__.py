# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from flask_migrate import Migrate
#from flask_redis import FlaskRedis
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
#migrate = Migrate()
#redis_client = FlaskRedis()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    #migrate.init_app(app, db)
    #redis_client.init_app(app)

    login_manager.login_view = '/web/templates/login.html' # Redirect to login page if user tries to access a protected route
    login_manager.init_app(app)
    
    bcrypt.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from . import routes 
    app.register_blueprint(routes.bp)

    with app.app_context():
        db.create_all()

    return app