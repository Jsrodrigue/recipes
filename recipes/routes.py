from flask import Blueprint, render_template, redirect, flash, url_for, current_app, request, jsonify
import uuid
from flask_login import login_required, current_user
from .forms import NewRecipeForm, save_recipe
from models import Recipe, Tag
import os
from werkzeug.utils import secure_filename
from extensions import db

recipes = Blueprint('recipes', __name__)

@recipes.route('/')
def index():
    return redirect(url_for('recipes.new'))

@recipes.route('/new', methods=["GET", "POST"])
@login_required
def new():
    form = NewRecipeForm()
    all_tags = Tag.query.order_by(Tag.name).all()
    form.tags.choices = [(tag.id, tag.name) for tag in all_tags]

    if form.validate_on_submit():
        recipe = save_recipe(form)
        return jsonify({'success': True})

    # Si es AJAX y hay errores, devuelve los errores por campo
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': False, 'errors': form.errors})

    # Si no es AJAX, renderiza la página normal
    return render_template("recipes/add_recipe_page.html", form=form, user=current_user)
