from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..services.api_services import fetch_random_recipe, convert_api_to_recipe

external_api = Blueprint('external_api', __name__)

@external_api.route("/")
@login_required
def discover():
  recipes = []

  # Loop to get 10 recipes
  for _ in range(5):
    while True:
      recipe = convert_api_to_recipe(fetch_random_recipe(),current_user.id)
      if recipe not in recipes:
        break
    recipes.append(recipe)
  for recipe in recipes: 
    print(type(recipe))

  return render_template("external_api/discover.html", recipes=recipes, user=current_user)