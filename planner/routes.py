from flask import Blueprint, render_template, jsonify, redirect, flash, url_for, request
from flask_login import login_required, current_user
import datetime
from models import MealPlan, Recipe
from forms.planner_forms import PlannerForm
from services.planner_services import save_planned, delete_plan_by_id

planner = Blueprint('planner', __name__)

@planner.route("/")
@login_required
def index():
  return render_template("planner/planner_calendar.html", user=current_user)

# Route to return the meals planned for a date as JSON
@planner.route("/meals/<date_str>")
@login_required
def meals(date_str):
  try:
    # Get the date as a date object
    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
  except ValueError:
    return
  
  # Filter the planner instances with for date and current_user 
  planners = MealPlan.query.filter(
    MealPlan.planned_date == date_obj,
    MealPlan.user_id == current_user.id
  ).all()

  list = [p.to_dict() for p in planners]
  return jsonify(list)

# Route to get and post the form to create new planned meal
@planner.route("/new_planned_meal", methods=["GET", "POST"])
@login_required
def new_plan():
  form = PlannerForm()

  # Query recipes for the user and fill the form with ids and titles
  recipes = Recipe.query.filter_by(user_id=current_user.id).all()
  form.recipe_id.choices = [(r.id, r.title) for r in recipes]

  if form.validate_on_submit():
    save_planned(form)
  return render_template('planner/planner_form.html', user=current_user, form=form)


# Route to return all scheduled meals as events
@planner.route('/planner/events')
def calendar_events():
    events = MealPlan.query.filter_by(user_id=current_user.id).all()  # Filter planned meals
    return jsonify([
        {
            "id": meal.id,
            "title": f"{meal.recipe.title} ({meal.meal_type.value})",
            "start": meal.planned_date.isoformat(),  # formato YYYY-MM-DD
            "allDay": True
        }
        for meal in events
    ])


# Route to delete a meal plan by id
@planner.route('/delete/<plan_id>', methods=['DELETE'])
@login_required
def delete(plan_id):
    # Call function to delete plan and get result and status code
    result, status_code = delete_plan_by_id(plan_id, current_user.id)

    # Handle unauthorized access
    if status_code == 403:
        # If request is AJAX, return JSON response with 403 status
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(result), 403

    # Handle plan not found
    if status_code == 404:
        # If request is AJAX, return JSON response with 404 status
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(result), 404

    # For successful deletion via AJAX, return HTTP 204 No Content
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return '', 204
  
