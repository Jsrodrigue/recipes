from flask_login import UserMixin  # Class for model users
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Table, JSON, Boolean
from extensions import db
from datetime import datetime, timezone

##################################################  
##### User model #################################
##################################################

# We use Mapped and mapped_column from SQLAlchemy 2.0 to define model fields.
# Mapped tells Python the type of the field (like int or str).
# mapped_column creates the actual database column with options like primary key or uniqueness.

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

##################################################  
##### Models for recipes and tags ################
##################################################

# Table to model the relationship between tags and recipes
recipe_tags = Table(
    'recipe_tags',
    db.metadata,
    db.Column('recipe_id', Integer, ForeignKey('recipes.id'), primary_key=True),
    db.Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class Recipe(db.Model):
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    ingredients = db.Column(db.JSON, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    # Foreign key linking this recipe to the user who created it
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationship to access the User object directly from a Recipe instance (e.g., recipe.user.username)
    user = db.relationship('User', backref='recipes')

    photo_filename = db.Column(db.String(100), nullable=True)
    
    # Defines many-to-many relationship between Recipe and Tag via the recipe_tags association table.
    tags = db.relationship('Tag', secondary=recipe_tags, backref='recipes')

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
