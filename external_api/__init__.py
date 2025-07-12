from flask import Blueprint

external_api = Blueprint('external_api', __name__, template_folder='templates')

from .routes import external_api