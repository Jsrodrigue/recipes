from flask import Blueprint, render_template, jsonify, redirect, flash, url_for
from flask_login import login_required, current_user
import datetime
from models import Planner

planner = Blueprint('planner', __name__)

@planner.route("/")
@login_required
def index():
  return render_template("planner/planner_calendar.html", user=current_user)

@planner.route("/meals/<date_str>")
@login_required
def meals(date_str):
  try:
    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
  except ValueError:
    return
  
  # Filter the planner instances with for date and current_user 
  planners = Planner.query.filter(
    Planner.planned_date == date_obj,
    Planner.user_id == current_user.id
  ).all()

  list = [p.to_dict() for p in planners]
  return jsonify(list)
  