from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from extensions import db
from models import User, Recipe, Tag
from flask import redirect, url_for, request
from flask_login import current_user
from wtforms import BooleanField
from flask_wtf import FlaskForm


class AdminModelView(ModelView):
    def is_accessible(self):
        # Only allow access if the current user is authenticated and is an admin
        return current_user.is_authenticated and getattr(current_user, 'is_admin', False)

    def inaccessible_callback(self, name, **kwargs):
        # If user is not allowed access, redirect to the login page
        return redirect(url_for('auth.login', next=request.url))
    

class UserAdmin(AdminModelView):
    form_columns = ['username', 'email', 'is_admin']
    

class RecipeAdmin(AdminModelView):
    form_columns = ['title', 'description', 'ingredients', 'instructions', 'created_at', 'user_id', 'tags']
    
def setup_admin(app):
    # Create the Flask-Admin instance attached to the Flask app
    admin = Admin(app, name="Admin", template_mode="bootstrap4", url="/admin")

    # Add the User model view, using the special UserAdmin view to manage the is_admin checkbox
    admin.add_view(UserAdmin(User, db.session))

    # Add the Recipe and Tag models with normal admin access control (no special form fields)
    admin.add_view(AdminModelView(Recipe, db.session))
    admin.add_view(AdminModelView(Tag, db.session))

    return admin

