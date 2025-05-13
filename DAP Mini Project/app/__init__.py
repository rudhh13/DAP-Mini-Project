from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from app.config.config import Config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
# Add default redirect view after login if not specified
login_manager.login_message = 'Please log in to access this page.'
bcrypt = Bcrypt()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    
    # Import and register blueprints
    from app.routes.main import main
    from app.routes.auth import auth
    from app.routes.dashboard import dashboard
    from app.routes.transactions import transactions
    from app.routes.reports import reports
    from app.routes.budgets import budgets
    
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(transactions)
    app.register_blueprint(reports)
    app.register_blueprint(budgets)
    
    return app 