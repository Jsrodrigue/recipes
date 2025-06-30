from flask import Blueprint

main = Blueprint('auth', __name__, template_folder='templates')

from .routes import main