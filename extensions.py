# Etensions to avoid circular importations and to use modularity

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Create extensions
db = SQLAlchemy()
login_manager = LoginManager()
