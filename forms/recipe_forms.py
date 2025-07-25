from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, HiddenField, SubmitField, SelectMultipleField, FileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed


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
    source = HiddenField() # Field to store the source 'local' or 'api' 
    photo_url = HiddenField() # Field to store the photo_url for external recipes 
    external_id = HiddenField()
    submit = SubmitField('Save')

    def __init__(self, all_tags, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asign the tags to the form
        self.tags.choices = [(tag.id, tag.name) for tag in all_tags]
