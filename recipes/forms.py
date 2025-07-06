from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, HiddenField, SubmitField, SelectMultipleField, FileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed, FileRequired
from werkzeug.utils import secure_filename
import os
from flask import redirect, flash ,current_app #Proxy to use the current app and aviod circular calls
from models import Recipe, Tag
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
from flask_login import current_user
import uuid #module used to generate unique name to a file

# Form to create a new recipe
class NewRecipeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    instructions = TextAreaField('Instructions')
    # Use a hiddenField because we will save the ingredients in a list of dictionaries with keys 'name' 'quantity'
    ingredients = HiddenField('Ingredients (JSON)', validators=[DataRequired()])
    tags = SelectMultipleField('Tags', coerce=int)
    photo = FileField('Photo', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Only image files are allowed')
    ])
    submit = SubmitField('Save')

# Function to save a recipe from the form
def save_recipe(form):
    if form.validate_on_submit():
        photo = form.photo.data
        filename = None
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
            user=current_user
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