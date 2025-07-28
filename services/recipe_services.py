
from werkzeug.utils import secure_filename
import os
from flask import flash ,current_app #Proxy to use the current app and aviod circular calls
from models import Recipe, Tag
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
import uuid #module used to generate unique name to a file
import json
from flask_login import current_user


# Function to save a recipe from the form
def save_recipe(form):
    if form.validate_on_submit():
        photo = form.photo.data
        filename = None
        photo_url=form.photo_url.data
        if photo:
            # Add unique name to filename
            original_filename = secure_filename(photo.filename)
            unique_name = uuid.uuid4().hex
            extension = os.path.splitext(original_filename)[1]
            filename = f"{unique_name}{extension}"

            try:
                photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            except Exception as e:
                current_app.logger.exception("Error saving uploaded file")
                flash("Failed to save the photo", "danger")
                filename = None
                return
            
        # Create recipe object
        recipe = Recipe(
            title=form.title.data,
            description=form.description.data,
            instructions=form.instructions.data,
            ingredients=form.ingredients.data,  # Store as JSON string
            photo_filename=filename,
            user=current_user,
            photo_url=photo_url,
            source=form.source.data,
            external_id=form.external_id.data
        )

        

       # Save the recipe to the database
        try: 
            db.session.add(recipe)
            # Assign selected tags from the form to the recipe using their IDs
            recipe.tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()
            db.session.commit()
            flash("Recipe successfully added", 'success')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Database error", 'danger')
            current_app.logger.error(f"SQLAlchemy error: {str(e)}")
        except Exception as e:
            flash("Unexpected error", 'danger')
            current_app.logger.exception("Unexpected error while saving recipe")

def update_recipe(form, recipe_id):
    if form.validate_on_submit():
        recipe = Recipe.get_by_id(recipe_id)
        if not recipe:
            flash("Recipe not found", "danger")
            return

        # Update fields
        recipe.title = form.title.data
        recipe.description = form.description.data
        recipe.instructions = form.instructions.data

        # Ingredients: always save as JSON string
        ingredients_data = form.ingredients.data
        if isinstance(ingredients_data, str):
            recipe.ingredients = json.loads(ingredients_data)
        else:
            recipe.ingredients = ingredients_data

        # Tags
        recipe.tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()

        # Photo update 
        photo = form.photo.data
        if photo:
            # Save new photo
            original_filename = secure_filename(photo.filename)
            unique_name = uuid.uuid4().hex
            extension = os.path.splitext(original_filename)[1]
            filename = f"{unique_name}{extension}"
            try:
                photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                # Only after saving new photo, delete the old one
                if recipe.photo_filename:
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], recipe.photo_filename)
                    try:
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    except Exception as e:
                        current_app.logger.warning(f"Could not delete old photo: {e}")
                recipe.photo_filename = filename
            except Exception as e:
                current_app.logger.exception("Error saving uploaded file")
                flash("Failed to save the new photo", "danger")

        try:
            db.session.commit()
            flash("Recipe updated successfully", "success")
        except Exception as e:
            db.session.rollback()
            flash("Error updating recipe", "danger")
            current_app.logger.exception("Error updating recipe")

# Function to prefill a form with the recipes data
def prefill_form_with_recipe(recipe, form):
  
    # Prefill the form fields
    form.title.data = recipe.title
    form.description.data = recipe.description
    form.instructions.data = recipe.instructions
    form.source.data=recipe.source

    if recipe.photo_url:
        form.photo_url.data = recipe.photo_url
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


# Function to delete recipe
def delete_recipe_by_id(recipe_id, user_id):
    recipe = Recipe.query.get(recipe_id)

    if not recipe:
        return {"error": "Recipe not found"}, 404

    if recipe.user_id != user_id:
        return {"error": "Unauthorized"}, 403


    for plan in recipe.planner:
        db.session.delete(plan)

    db.session.delete(recipe)
    db.session.commit()
    
    # Delete photo if it exists
    if recipe.photo_filename:
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], recipe.photo_filename)
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            current_app.logger.warning(f"Could not delete photo: {e}")

    return {"success": True}, 204