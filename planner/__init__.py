from flask import Blueprint

planner = Blueprint('planner', __name__, template_folder='templates')

from .routes import planner