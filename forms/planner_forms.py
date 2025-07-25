from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, SubmitField, DateField
from wtforms.validators import DataRequired
from models import MealType


# Form to create a new planned meal 
class PlannerForm(FlaskForm):
    recipe_id = SelectField('Recipe', coerce=int, validators=[DataRequired()])
    planned_date = DateField('Planned Date', format='%Y-%m-%d', validators=[DataRequired()])
    meal_type = SelectField('Meal Type', 
                            choices=[(m.name, m.value.replace('_', ' ').title()) for m in MealType], 
                            validators=[DataRequired()])
    submit = SubmitField('Add to Planner')

    def __init__(self, all_tags, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asign the tags to the form
        self.tags.choices = [(tag.id, tag.name) for tag in all_tags]
