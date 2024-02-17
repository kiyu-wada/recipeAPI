from flask import Flask, render_template, request
from rapidfuzz import process, fuzz
import requests

# Create the Flask app
app = Flask(__name__)

# Replace with your Spoonacular API key
API_KEY = '2034930ec06a4162a61419499fd4404d'

# List of valid ingredients for correction
valid_ingredients = ["apple", "orange", "flour", "milk", "eggs", "butter", "sugar", "salt", "cheese", "banana"]

# Define the route for the "Home" button
@app.route('/home', methods=['GET'])
def home():
    # Render the main page with empty recipe list and search query
    return render_template('index.html', recipes=[], search_query='')

# Define the main route for the app
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Capture the ingredients from the form input
        ingredients = request.form.get('search_query', '')
        # Correct the ingredients for spelling errors
        corrected_ingredients = correct_ingredients(ingredients)
        # Process the ingredients for the API call
        recipes = search_recipes(corrected_ingredients)
        # Render the main page with the search results and the corrected search query
        return render_template('index.html', recipes=recipes, search_query=corrected_ingredients)
    
    # If it's a GET request or no form submitted, display the page without recipes
    return render_template('index.html', recipes=[], search_query='')

def correct_ingredients(user_input):
    # Split the user's input into individual ingredients based on commas
    user_ingredients = [ingredient.strip().lower() for ingredient in user_input.split(',')]
    corrected_ingredients = []

    for ingredient in user_ingredients:
        # Attempt to find the closest match in valid_ingredients
        result = process.extractOne(ingredient, valid_ingredients, scorer=fuzz.WRatio, score_cutoff=80)
        
        if result:
            best_match = result[0]  # Access the best match directly
            corrected_ingredients.append(best_match)
        else:
            corrected_ingredients.append(ingredient)  # Use the original if no match found

    return ', '.join(corrected_ingredients)

# Function to search for recipes based on the provided ingredients
def search_recipes(corrected_ingredients):
    url = 'https://api.spoonacular.com/recipes/findByIngredients'
    params = {
        'apiKey': API_KEY,
        'ingredients': corrected_ingredients,
        'number': 50,
        'ranking': 1,
        'ignorePantry': True,
        'instructionsRequired': True,
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: API call failed with status code {response.status_code}")
        return []

# Route to view a specific recipe with a given recipe ID
@app.route('/recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    search_query = request.args.get('search_query', '')
    url = f'https://api.spoonacular.com/recipes/{recipe_id}/information'
    params = {'apiKey': API_KEY}

    response = requests.get(url, params=params)
    if response.status_code == 200:
        recipe = response.json()
        return render_template('view_recipe.html', recipe=recipe, search_query=search_query)
    else:
        return "Recipe not found", 404

# Run the app in debug mode if executed directly
if __name__ == '__main__':
    app.run(debug=True)
