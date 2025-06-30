from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, HiddenField, SubmitField, SelectMultipleField, FileField
from wtforms.validators import DataRequired, FileAllowed

# Form to create a new recipe
class NewRecipeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    instructions = TextAreaField('Instructions')
    # Use a hiddenField because we will save the ingredients in a list of dictionaries with keyw 'name' 'qunantity'
    ingredients = HiddenField('Ingredients (JSON)', validators=[DataRequired()])
    tags = SelectMultipleField('Tags', coerce=int)
    photo = FileField('Recipe Photo', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Save')
