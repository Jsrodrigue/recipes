from flask import Blueprint, render_template, redirect, flash, url_for, jsonify, request, current_app
import uuid
from flask_login import login_required, current_user
from .forms import NewRecipeForm, save_recipe, update_recipe
from models import Recipe, Tag
from extensions import db
import json
import os

recipes = Blueprint('recipes', __name__)

@recipes.route('/myrecipes')
@login_required
def index():
    return render_template("recipes/my_recipes_page.html", user=current_user, recipes=current_user.recipes)


# Route to create a new recipe
@recipes.route('/new', methods=["GET", "POST"])
@login_required
def new():
    
    form = NewRecipeForm()

    # Get the tags in the db by alphabetical order and add to the form
    all_tags = Tag.query.order_by(Tag.name).all()
    form.tags.choices = [(tag.id, tag.name) for tag in all_tags]

    if form.validate_on_submit():
        save_recipe(form)
        return redirect(url_for("recipes.index"))
    return render_template("recipes/add_edit_recipe.html", form=form, user=current_user, recipe=None)

# Route to see a recipe by id
@recipes.route('/<recipe_id>')
@login_required
def get_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    
    # Check if ingredients is a str and if so transform to JSON
    if isinstance(recipe.ingredients, str):
        try:
            recipe.ingredients = json.loads(recipe.ingredients)
        except Exception:
            recipe.ingredients = []

    return render_template("recipes/get_recipe.html", user=current_user, recipe=recipe)

# Route delete a recipe by id
@recipes.route('delete/<recipe_id>', methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)

    # Check if the user is the creator of the recipe
    if recipe.user_id != current_user.id:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Unauthorized"}), 403
        else:
            flash("Unauthorized user")
            return redirect(url_for("recipes.index"))
   
    # Delete the photo from the folder
    if recipe.photo_filename:
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], recipe.photo_filename)
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
                current_app.logger.warning(f"Could not delete old photo: {e}")
            
    db.session.delete(recipe)
    db.session.commit()
    
    # Check if the petition is by AJAX
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return "", 204
    
    flash("Recipe deleted successfuly!", "success")
    # Redirect to myrecipes if the petition is by the form
    return redirect(url_for("recipes.index"))

# Route edit a recipe by id
@recipes.route('edit/<recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    form = NewRecipeForm()
    recipe = Recipe.get_by_id(recipe_id)
    
    # Redirect to index if the recipe is not found
    if not recipe:
        flash("Recipe not found", "danger")
        return redirect(url_for("recipes.index"))
    
    # Get the tags in the db by alphabetical order and add to the form
    all_tags = Tag.query.order_by(Tag.name).all()
    form.tags.choices = [(tag.id, tag.name) for tag in all_tags]

    if form.validate_on_submit():
        update_recipe(form, recipe_id)
        return redirect(url_for("recipes.get_recipe", recipe_id=recipe_id))
    
    # Prefill the form fields
    form.title.data = recipe.title
    form.description.data = recipe.description
    form.instructions.data = recipe.instructions 
    #Need to map correctly ingredients and tags

    # Convert to python list if it's a JSON string
    if isinstance(recipe.ingredients, str):
        try:
            ingredients_list = json.loads(recipe.ingredients)
        except Exception:
            ingredients_list = []
    else:
        ingredients_list = recipe.ingredients if recipe.ingredients else []

    form.ingredients.data = json.dumps(ingredients_list)
    form.tags.data = [tag.id for tag in recipe.tags]

    # Convert to python dictionary
    # Check if ingredients is a str and if so transform to JSON
    if isinstance(recipe.ingredients, str):
        recipe.ingredients = json.loads(recipe.ingredients)

    return render_template("recipes/add_edit_recipe.html", form=form, user=current_user, recipe= recipe)


