from flask import Blueprint, render_template, redirect, flash, url_for
from .forms import RegistrationForm, LoginForm
#Ex of use: login_user(user_id) login an user, logout_user() logs out a session, 
# @login_required decorator to protect routes, current_user User object with session 
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from extensions import db

auth = Blueprint('auth', __name__)

# Login route
@auth.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('main.home'))
  form = LoginForm()
  # When submiting
  if form.validate_on_submit():
    # Check if the user exists
    if not User.query.filter_by(username=form.username.data).first():
      flash("User doesn't exist!", "danger")
    else:
      user = User.query.filter_by(username=form.username.data).first()
      if user.check_password(form.password.data):
        login_user(user)
        return redirect(url_for('main.home'))
      else:
        flash("Incorrect password", "danger")
  return render_template('auth/login.html', form=form, user =current_user)
  
  
# Register route
@auth.route('/register', methods=['GET', 'POST'])
def register():
  form = RegistrationForm()
  # Check if form was submited
  if form.validate_on_submit():
    # Check if username exists in the db
    if User.query.filter_by(username=form.username.data).first():
      flash('Username alredy exists!', 'danger')
    # Check if the email is registered  
    elif User.query.filter_by(email=form.email.data).first():
      flash('Email alredy in use!', 'danger')
    else:
      # Add user to the db
      user = User(username = form.username.data, email=form.email.data)
      user.set_password(form.password.data)
      db.session.add(user)
      db.session.commit()
      flash('User created!', 'success')
      return redirect(url_for('auth.login'))
  return render_template('auth/register.html', form=form, user=current_user)

#Logout route 
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))