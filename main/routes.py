from flask import Blueprint, render_template, redirect, flash, url_for
#Ex of use: login_user(user_id) login an user, logout_user() logs out a session, 
# @login_required decorator to protect routes, current_user User object with session 
from flask_login import login_user, logout_user, login_required, current_user

main = Blueprint('main', __name__)

# Home route
@login_required
@main.route('/home')
def home():
  return render_template("main/index.html", user=current_user)

