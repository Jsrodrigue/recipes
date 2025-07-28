from flask import Blueprint, render_template, redirect, flash, url_for, jsonify, request, current_app
import uuid
from flask_login import login_required, current_user
from forms.recipe_forms import NewRecipeForm
from services.recipe_services import  save_recipe, update_recipe, prefill_form_with_recipe, delete_recipe_by_id
from models import Recipe, Tag
from extensions import db
import json
import os
import html

recipes = Blueprint('recipes', __name__)

@recipes.route('/myrecipes')
@login_required
def index():
    return render_template("recipes/my_recipes_page.html", user=current_user, recipes=current_user.recipes)


# Route to create a new recipe
@recipes.route('/new', methods=["GET", "POST"])
@login_required
def new():
    
    # Get the tags in the db by alphabetical order and add to the form
    all_tags = Tag.query.order_by(Tag.name).all()
    form = NewRecipeForm(all_tags)

    if form.validate_on_submit():
        save_recipe(form)
        return redirect(url_for("recipes.index"))
    return render_template("recipes/add_edit_recipe.html", form=form, user=current_user, recipe=None)

# Route to see a recipe by id
@recipes.route('/<recipe_id>')
@login_required
def get_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    print(repr(recipe.instructions))
    recipe.title = html.escape(recipe.title)
    recipe.description = html.escape(recipe.description).replace("\r\n", "<br>")
    recipe.instructions = html.escape(recipe.instructions).replace("\r\n", "<br>")
   
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
    result, status_code = delete_recipe_by_id(recipe_id, current_user.id)

    if status_code == 403:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(result), 403
        else:
            flash("Unauthorized user")
            return redirect(url_for("recipes.index"))

    if status_code == 404:
        flash("Recipe not found")
        return redirect(url_for("recipes.index"))

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return "", 204

    flash("Recipe deleted successfully!", "success")
    return redirect(url_for("recipes.index"))

# Route edit a recipe by id
@recipes.route('edit/<recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):

    recipe = Recipe.get_by_id(recipe_id)
    
    # Redirect to index if the recipe is not found
    if not recipe:
        flash("Recipe not found", "danger")
        return redirect(url_for("recipes.index"))
    
    # Get the tags in the db by alphabetical order and use in the form
    all_tags = Tag.query.order_by(Tag.name).all()
    form = NewRecipeForm(all_tags)

    
    if form.validate_on_submit():
        update_recipe(form, recipe_id)
        return redirect(url_for("recipes.get_recipe", recipe_id=recipe_id))
    
    # Set the fields in the form
    prefill_form_with_recipe(recipe, form)

    return render_template("recipes/add_edit_recipe.html", form=form, user=current_user, recipe= recipe)


