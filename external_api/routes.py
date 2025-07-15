from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from services.api_services import fetch_random_recipe, convert_api_to_recipe, fetch_recipe_by_id
import concurrent.futures # Module to make multiple api requests in paralel
import json
from forms.recipe_forms import NewRecipeForm
from models import Tag
from services.recipe_services import prefill_form_with_recipe
import html

external_api = Blueprint('external_api', __name__)

# Render five random recipes from the db api. Refacotred my code with GPT because my original 
# code was getting the recipes from the api in serie which make the page too slow to load the content

@external_api.route("/")
@login_required
def discover():
    recipes = []  # List to store unique recipes
    seen_titles = set()  # Set to keep track of recipe titles we've already seen to avoid duplicates
    
    # Create a ThreadPoolExecutor to run tasks concurrently using up to 5 worker threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit 10 fetch_recipe tasks to the executor to run in parallel
        futures = [executor.submit(fetch_random_recipe) for _ in range(10)]

        # As each future completes (in any order), process its result
        for future in concurrent.futures.as_completed(futures):
            api_data = future.result()  # Get the actual recipe data from the completed future
            if not api_data:
                # If no data was returned (None or empty), skip this result
                continue

            title = api_data.get("strMeal")  # Extract the recipe title

            if title in seen_titles:
                # If we've already seen this recipe title, skip it to avoid duplicates
                continue

            # Convert the API recipe data to my Recipe model instance
            recipe = convert_api_to_recipe(api_data)

            recipes.append(recipe)  # Add the recipe to the list
            seen_titles.add(title)  # Mark this title as seen

            if len(recipes) >= 5:
                # Once we've collected 5 unique recipes, stop processing further results
                break

    # Render the template
    return render_template("external_api/discover.html", recipes=recipes, user=current_user)

# Route to see a recipe by id
@external_api.route('/<external_id>')
@login_required
def get_recipe(external_id):
    # Fetch recipe by id
    data = fetch_recipe_by_id(external_id)
    if data and len(data) > 0:
      recipe = data[0]
    else:
      recipe = None
    
    #Check if recipe is None
    if not recipe:
       flash("External recipe not found", "danger")
       return redirect(url_for("external_api.discover"))
    
    # Convert recipe and render
    recipe = convert_api_to_recipe(recipe)
    
    #escape html
    recipe.title = html.escape(recipe.title)
    recipe.description = html.escape(recipe.description).replace("\r\n", "<br>")
    recipe.instructions = html.escape(recipe.instructions).replace("\r\n", "<br>")
    return render_template("recipes/get_recipe.html", user=current_user, recipe=recipe)

# Route to save an external recipe
@external_api.route('/save/<external_id>')
@login_required
def save(external_id):
    # Fetch recipe by id
    data = fetch_recipe_by_id(external_id)
    if data and len(data) > 0:
      recipe = convert_api_to_recipe(data[0])
    else:
      recipe = None
    
    #Check if recipe is None
    if not recipe:
       flash("External recipe not found", "danger")
       return redirect(url_for("external_api.discover"))
    
   # Get the tags in the db by alphabetical order and use in the form
    all_tags = Tag.query.order_by(Tag.name).all()
    form = NewRecipeForm(all_tags)

    
    if form.validate_on_submit():
        return 
    
    # Set the fields in the form
    prefill_form_with_recipe(recipe, form)
    return render_template("recipes/add_edit_recipe.html", form=form, user=current_user, recipe=recipe)
    