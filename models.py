from flask_login import UserMixin # Class for model users
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from datetime import datetime, timezone


class User(db.Model, UserMixin):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)
  email = db.Column(db.String(80), unique=True, nullable=False)
  password_hash=db.Column(db.String(128), nullable=False)

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)
  
  def check_password(self, password):
    return check_password_hash(self.password_hash, password)
  
##### Models for recipes and tags ################

# Table to model the relationship between tags and recipes
recipe_tags = db.Table('recipe_tags',
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipes.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)


class Recipe(db.Model):
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    ingredients = db.Column(db.JSON, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default= datetime.now(timezone.utc))
    
    # Foreign key linking this recipe to the user who created it
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationship to access the User object directly from a Recipe instance (e.g., recipe.user.username)
    user = db.relationship('User', backref='recipes') 

    photo_filename = db.Column(db.String(100), nullable=True)
    
    # Defines many-to-many relationship between Recipe and Tag via the recipe_tags association table.
    # Allows accessing tags of a recipe and recipes of a tag (via backref).
    tags = db.relationship('Tag', secondary=recipe_tags, backref=db.backref('recipes', lazy='dynamic'))

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)