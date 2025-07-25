######################### Utils to consult an external recipes API #####################
######################### Functions for fetching were defined with help of GPT #########

import requests
from models import Recipe
from datetime import datetime, timezone
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


BASE_URL = "https://www.themealdb.com/api/json/v1/1"

# Get a random recipe from the external API
def fetch_random_recipe():
    url = f"{BASE_URL}/random.php"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["meals"][0] if data["meals"] else None
    return None

# Get recipe from api by external_id
def fetch_recipe_by_id(external_id):
    url = f"{BASE_URL}/lookup.php?i={external_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        meals = data.get("meals", [])
        if meals:
            return meals[0]
    return None


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
    title = api_recipe.get("strMeal", "Untitled")
    description = api_recipe.get("strCategory", "") + " | " + api_recipe.get("strArea", "")
    instructions = api_recipe.get("strInstructions", "")
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


# Search recipes by title
def search_by_title(query):
    res = requests.get(f"{BASE_URL}/search.php?s={query}")
    if res.status_code == 200:
        return res.json().get("meals") or []
    return []


######################## Search by category, area and ingredient ##############
######################## Made with help of  gpt to make multiple requests simountanously##

# Search recipes by filter and fetch details in parallel
def search_by_filter(filter_key, query):
    res = requests.get(f"{BASE_URL}/filter.php?{filter_key}={query}")
    if res.status_code != 200:
        return []

    recipes = res.json().get("meals") or []
    if not recipes:
        return []

    ids_to_lookup = [r["idMeal"] for r in recipes if "idMeal" in r]

    detailed = []
    with ThreadPoolExecutor() as executor:
        for full_recipe in executor.map(fetch_recipe_by_id, ids_to_lookup):
            if isinstance(full_recipe, dict):
                detailed.append(full_recipe)

    return detailed


# Unified search (title, category, area, ingredient)
def fetch_recipes_from_search(query):
    query = query.strip().lower()
    results = []

    def search_title():
        return search_by_title(query)

    filter_keys = ["c", "a", "i"]  # category, area, ingredient

    # Search in paralel
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {}

        # Search by title
        futures[executor.submit(search_title)] = "title"

        # Search by parameters
        for key in filter_keys:
            futures[executor.submit(search_by_filter, key, query)] = key

        for future in as_completed(futures):
            try:
                data = future.result()
                if data:
                    results.extend(data)
            except Exception as e:
                print(f"Error in search {futures[future]}: {e}")

    # Remove duplicates
    unique = {recipe["idMeal"]: recipe for recipe in results if "idMeal" in recipe}
    return list(unique.values())