from flask import Blueprint, render_template
from flask_login import login_required, current_user

external_api = Blueprint('external_api', __name__, template_folder='templates')

from .routes import external_api

@external_api.route('/discover')
@login_required
def index():
    return render_template("external_api/discover.html", user=current_user, recipes=current_user.recipes)
