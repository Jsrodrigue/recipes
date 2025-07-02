from flask import Blueprint, render_template, redirect, flash, url_for
from flask_login import login_required, current_user
from .forms import NewRecipeForm
from models import Recipe

recipes = Blueprint('recipes', __name__)

@recipes.route('/')
def index():
  return render_template('recipes/recipes_manage.html', user=current_user)

@recipes.route('/new', methods=["GET", "POST"])
@login_required
def new():
  form = NewRecipeForm()
  if form.validate_on_submit:
    recipe = Recipe(title=form.title.data, description=form.description.data, )
  return render_template("recipes/add_recipe_form.html", form=form)