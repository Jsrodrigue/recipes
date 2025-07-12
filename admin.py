from flask import redirect, url_for, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from wtforms import BooleanField, TextAreaField
import json

from extensions import db
from models import User, Recipe, Tag


# Base class that restricts access to admin panel
class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'is_admin', False)

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))

    can_view_details = True
    column_display_pk = True


# Custom admin view for User
class UserAdmin(AdminModelView):
    form_overrides = {
        'is_admin': BooleanField,
    }
    form_args = {
        'is_admin': {
            'label': 'Admin User',
            'default': False,
        }
    }
    column_list = ['id', 'username', 'email', 'is_admin']
    form_columns = ['username', 'email', 'password_hash', 'is_admin']


# Custom admin view for Recipe with relationships
class RecipeAdmin(AdminModelView):
    form_columns = [
        'title',
        'description',
        'ingredients',
        'instructions',
        'created_at',
        'user',    # Shows dropdown with users
        'tags'     # Shows multiselect for tags
    ]
    column_list = [
        'id',
        'title',
        'user.username',  # Show username of author
        'created_at',
    ]

    form_overrides = {
        'ingredients': TextAreaField,
    }

    def on_model_change(self, form, model, is_created):
        # Convert JSON string in ingredients to dict
        if isinstance(model.ingredients, str):
            try:
                model.ingredients = json.loads(model.ingredients)
            except Exception:
                raise ValueError("Ingredients must be valid JSON")


# Tag admin
class TagAdmin(AdminModelView):
    column_list = ['id', 'name']
    form_columns = ['name']


# Setup function to initialize admin
def setup_admin(app):
    admin = Admin(app, name="Admin", template_mode="bootstrap4", url="/admin")

    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(RecipeAdmin(Recipe, db.session))
    admin.add_view(TagAdmin(Tag, db.session))

    return admin
