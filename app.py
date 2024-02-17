from flask import Flask, render_template, request
import requests

# Create the flask app
app = Flask(__name__)

# Replace with your Spoonacular API key
API_KEY = '2034930ec06a4162a61419499fd4404d'

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
        # Process the ingredients for the API call
        recipes = search_recipes(ingredients)
        # Render the main page with the search results and the search query
        return render_template('index.html', recipes=recipes, search_query=ingredients)
    
    # If it's a GET request or no form submitted, display the page without recipes
    return render_template('index.html', recipes=[], search_query='')

# Function to search for recipes based on the provided ingredients
def search_recipes(ingredients):
    url = 'https://api.spoonacular.com/recipes/findByIngredients'
    params = {
        'apiKey': API_KEY,
        'ingredients': ingredients,
        'number': 50,
        'ranking': 1,
        'ignorePantry': True,
        'instructionsRequired': True,
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        # Directly return the JSON response if successful
        return response.json()
    else:
        # Log error or handle it appropriately
        print(f"Error: API call failed with status code {response.status_code}")
        return []

# Route to view a specific recipe with a given recipe ID
@app.route('/recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    # Get the search query from the URL query parameters (optional, for display purposes)
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
