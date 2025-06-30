from flask import Blueprint, render_template, redirect, flash, url_for
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

# Home route

@main.route('/')
def index():
  return redirect(url_for("main.home"))

@main.route('/home')
@login_required
def home():
  return render_template("main/index.html", user=current_user)

