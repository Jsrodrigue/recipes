from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, HiddenField, SubmitField, SelectMultipleField, FileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed, FileRequired
from werkzeug.utils import secure_filename
import os
from flask import flash, current_app #Proxy to use the current app
from models import Recipe, Tag
from extensions import db

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
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        
        # Save the recipe to the database
        recipe = Recipe(
            title=form.title.data,
            description=form.description.data,
            instructions=form.instructions.data,
            ingredients=form.ingredients.data,  # If you store as JSON string
            photo_filename=filename
        )
        # Add tags
        recipe.tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()
        try: 
            db.session.add(recipe)
            db.session.commit()
            flash("Recipe successfully added", 'success')
        except:
            flash("Error saving recipe", 'danger')
        
