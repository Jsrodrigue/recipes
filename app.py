from flask import Flask
from instance.config import Config
from extensions import db, login_manager
from flask_login import current_user # current_user object to manage current user
from models import User
from flask_migrate import Migrate
import click
from models import Tag

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

# Import blueprints 
from auth import auth 
from main import main
from recipes import recipes

# Register blueprints 
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(main, url_prefix='/')
app.register_blueprint(recipes, url_prefix='/recipes')

# object to manage authentication
login_manager.init_app(app)
# Set login route to redirect non-loged users when try to access routes that requieres login 
login_manager.login_view = 'auth.login'


# Decorator to specify the function that login_manager uses the class User as user object 
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Define seed-tags to initialized the tags in the db in command line
@app.cli.command("seed-tags")
def seed_tags():
    tags = [
    "Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Nut-Free",
    "Low Carb", "High Protein", "Keto", "Paleo", "Quick",
    "Easy", "Healthy", "Comfort Food", "Dessert", "Breakfast",
    "Lunch", "Dinner", "Snack", "Appetizer", "Soup",
    "Salad", "Grill", "Baking", "Slow Cooker", "One-Pot",
    "Seafood", "Poultry", "Beef", "Pork", "Pasta",
    "Rice", "Vegetables", "Fruits", "Spicy", "Sweet",
    "Low Fat", "Holiday", "Party", "Kid-Friendly", "Vegan Dessert",
    "Raw", "Fermented", "Street Food", "Crockpot", "Instant Pot",
    "Mediterranean", "Asian", "Mexican", "Italian", "Indian",
    "French", "Middle Eastern", "Comfort Food", "Budget-Friendly"
]
    for name in tags:
        if not Tag.query.filter_by(name=name).first():
            db.session.add(Tag(name=name))
    db.session.commit()
    click.echo("Tags seeded successfully!")


# Starting
if __name__ == '__main__':
    app.run(debug=True)