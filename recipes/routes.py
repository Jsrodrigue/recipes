from flask import Blueprint, render_template, redirect, flash, url_for
from flask_login import login_required, current_user

recipes = Blueprint('recipes', __name__)

@recipes.route('/')
def index():
  return render_template('recipes/recipes_manage.html', user=current_user)
