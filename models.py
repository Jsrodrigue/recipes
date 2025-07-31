from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Table, JSON, Boolean, Date, Enum
from extensions import db
from datetime import datetime, timezone, date
import enum

##################################################
##### User model #################################
##################################################

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    # One user can have multiple recipes an multiple planners
    recipes: Mapped[list["Recipe"]] = relationship(back_populates="user")
    planner: Mapped[list["MealPlan"]] = relationship(back_populates="user")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
    

##################################################
##### Association recipe-tag Table ###############
##################################################

recipe_tags = Table(
    'recipe_tags',
    db.metadata,
    db.Column('recipe_id', Integer, ForeignKey('recipes.id'), primary_key=True),
    db.Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

##################################################
##### Recipe model ###############################
##################################################

class Recipe(db.Model):
    __tablename__ = 'recipes'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ingredients is a dict wit keys 'name', 'quantity'
    ingredients: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    ## Fields to include recipes for external API
    source: Mapped[str] = mapped_column(String(20), default="local") # 'local' or 'api'
    external_id: Mapped[str | None] = mapped_column(String, nullable=True) # ID of API for external recipes
    photo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    photo_filename: Mapped[str | None] = mapped_column(String(512), nullable=True)

    

    #relationships
    # Oner recipe can have only one user, but multiplre planners and tags
    user: Mapped["User"] = relationship(back_populates="recipes")
    planner: Mapped[list["MealPlan"]] = relationship(back_populates="recipe")
    tags: Mapped[list["Tag"]] = relationship(
        secondary=recipe_tags,
        back_populates="recipes"
    )

    @classmethod
    def get_by_id(cls, id: int) -> "Recipe | None":
        return cls.query.filter_by(id=id).first()

##################################################
##### Tag model ##################################
##################################################

class Tag(db.Model):
    __tablename__ = 'tags'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    #Relationship, one tag can be in multiple recipes
    recipes: Mapped[list["Recipe"]] = relationship(
        secondary=recipe_tags,
        back_populates="tags"
    )

###### Class used to restrict the options for the meal_type field in the planner model####
class MealType(enum.Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    MORNING_SNACK = "morning_snack"
    AFTERNOON_SNACK = "afternoon_snack"

########### Planer table ########################
class MealPlan(db.Model):
    __tablename__ = 'planner'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    recipe_id: Mapped[int] = mapped_column(ForeignKey('recipes.id'), nullable=False)
    planned_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    meal_type: Mapped[MealType] = mapped_column(
        Enum(MealType, name="meal_type"), 
        nullable=False
    )
    
    #Relashionships, one planner have only one recipe and user
    user: Mapped["User"] = relationship(back_populates="planner")
    recipe: Mapped["Recipe"] = relationship(back_populates="planner")

    # Method to get a dictionary with recipe_id, recipe_title, meal_type and planned_Date
    def to_dict(self):
        return {
            "id" : self.id,
            "recipe_id": self.recipe_id,
            "recipe_title": self.recipe.title if self.recipe else None,
            "meal_type": self.meal_type.value,
            "planned_date": self.planned_date.isoformat()
        }