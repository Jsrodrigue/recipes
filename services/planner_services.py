
from models import MealPlan
from extensions import db
from flask import flash, current_app
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

# function to save a planned meal from the form
def save_planned(form):

  # Instance MealPlan object and fill with the fields of the form 
  meal_plan = MealPlan()
  meal_plan.user_id = current_user.id
  meal_plan.recipe_id = form.recipe_id.data
  meal_plan.planned_date = form.planned_date.data
  meal_plan.meal_type = form.meal_type.data

  # Save the meal_plan in the db
  try:
    db.session.add(meal_plan)
    db.session.commit()
    flash('Planned meal added')
  except SQLAlchemyError as e:
    db.session.rollback()
    flash("Database error", 'danger')
    current_app.logger.error(f"SQLAlchemy error: {str(e)}")
  except Exception as e:
    flash("Unexpected error", 'danger')
    current_app.logger.exception("Unexpected error while saving recipe")

