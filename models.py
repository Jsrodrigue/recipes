from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Table, JSON, Boolean
from extensions import db
from datetime import datetime, timezone

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

    recipes: Mapped[list["Recipe"]] = relationship(back_populates="user")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
    

##################################################
##### Association Table ##########################
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
    ingredients: Mapped[dict] = mapped_column(JSON, nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    ## Fields to include recipes for external API
    source = db.Column(db.String(20), default="local")  # 'local' or 'api'
    external_id = db.Column(db.String, nullable=True)  # ID of API for external recipes
    
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship(back_populates="recipes")

    photo_filename: Mapped[str | None] = mapped_column(String(100), nullable=True)

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

    recipes: Mapped[list["Recipe"]] = relationship(
        secondary=recipe_tags,
        back_populates="tags"
    )

