from flask import Blueprint, render_template, redirect, flash, url_for, current_app, request, jsonify
import uuid
from flask_login import login_required, current_user
from .forms import NewRecipeForm, save_recipe
from models import Recipe, Tag
import os
from werkzeug.utils import secure_filename
from extensions import db
import json

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
        return redirect(url_for("recipes.new"))
    return render_template("recipes/add_recipe_page.html", form=form, user=current_user, action='new')

# Route to see a recipe by id
@recipes.route('/<recipe_id>')
@login_required
def get_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    # Nedded to transform ingredients into a list of dictioanries
    recipe.ingredients = json.loads(recipe.ingredients)
    return render_template("recipes/get_recipe.html", user=current_user, recipe=recipe)

# Route delete a recipe by id
@recipes.route('delete/<recipe_id>', methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if recipe.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    db.session.delete(recipe)
    db.session.commit()
    return "", 204

# Route edit a recipe by id
@recipes.route('edit/<recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    pass
