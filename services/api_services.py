######################### Utils to consult an external recipes API #####################
######################### Functions for fetching were defined with help of GPT #########

import requests
from models import Recipe
from datetime import datetime, timezone
import html



# Get recipes from the search of the external API mealbd
def fetch_recipes_from_mealdb(query):
  url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={query}"

  response = requests.get(url)
  if response.status_code == 200:
        data = response.json()
        return data.get("meals", [])
  return []


# Get a random recipe from the external API
def fetch_random_recipe():
    url = "https://www.themealdb.com/api/json/v1/1/random.php"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["meals"][0] if data["meals"] else None
    return None

# Get recipe from api by external_id
def fetch_recipe_by_id(external_id):
  url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={external_id}"
  response = requests.get(url)
  if response.status_code == 200:
        data = response.json()
        return data.get("meals", [])
  return []


# Get the ingredients from the API recipe in a list fo dictionaries
def get_ingredients(api_recipe):
    ingredients = []
    for i in range(1, 21):  # The API includes 20 ingredients fields, if less some fields are empty
        name = api_recipe.get(f"strIngredient{i}")
        quantity = api_recipe.get(f"strMeasure{i}")
        if name and name.strip():
            ingredients.append({
                "name": name.strip(),
                "quantity": quantity.strip() if quantity else "to taste"
            })
    return ingredients

# Function to convert the recipe from API to my model 
def convert_api_to_recipe(api_recipe):
    # Set data
    title = html.escape(api_recipe.get("strMeal", "Untitled"))
    description = html.escape(api_recipe.get("strCategory", "") + " | " + api_recipe.get("strArea", ""))
    instructions = html.escape(api_recipe.get("strInstructions", ""))
    ingredients = get_ingredients(api_recipe)
    image_url = api_recipe.get("strMealThumb")  # URL from internet
    external_id=api_recipe.get("idMeal")

    # Create instance
    recipe = Recipe(
        title=title,
        description=description,
        ingredients=ingredients,
        instructions=instructions,
        photo_url=image_url,
        created_at=datetime.now(timezone.utc),
        source='api',
        external_id=external_id
    )

    return recipe