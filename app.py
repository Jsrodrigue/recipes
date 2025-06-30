from flask import Flask
from instance.config import Config
from extensions import db
from flask_login import LoginManager, current_user # Login session management and current_user object to manage current user
from models import User
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

# Import blueprints 
from auth import auth 
from main import main
from recipes import recipes

# Register blueprints 
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(main, url_prefix='/')
app.register_blueprint(recipes, url_prefix='/recipes')

# object to manage authentication
login_manager = LoginManager(app)
# Set login route to redirect non-loged users when try to access routes that requieres login 
login_manager.login_view = 'auth.login'


# Decorator to specify the function that login_manager uses the class User as user object 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Starting
if __name__ == '__main__':
    app.run(debug=True)