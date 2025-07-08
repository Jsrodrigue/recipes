from flask_login import UserMixin  # Class for model users
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Table, JSON
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
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)

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
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    ingredients: Mapped[dict] = mapped_column(JSON, nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    
    # Foreign key linking this recipe to the user who created it
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    
    # Relationship to access the User object directly from a Recipe instance (e.g., recipe.user.username)
    user: Mapped['User'] = relationship(backref='recipes')

    photo_filename: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # Defines many-to-many relationship between Recipe and Tag via the recipe_tags association table.
    tags: Mapped[list['Tag']] = relationship('Tag', secondary=recipe_tags, backref='recipes')

class Tag(db.Model):
    __tablename__ = 'tags'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
