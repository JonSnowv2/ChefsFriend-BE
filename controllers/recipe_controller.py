from flask import current_app, jsonify, request, g
from flask_cors import cross_origin
from config import db, app
from models.recipe import Recipe 
from models.user import User
from authentication_service.authentication import login

def get_all_recipes():
    return Recipe.query.all()


@app.route('/api/recipes/add', methods=['POST'])
@cross_origin(origin="*")
def create_recipe():
    data = request.json  
    title = data.get('title')
    description = data.get('description')
    ingredients_list = data.get('ingredients')
    instructions_list = data.get('instructions')
    category = data.get('category')
    image = data.get('image')

    user = g.user

    if not user:
        return jsonify({'error': 'User not authenticated'}), 401


    ingredients = ','.join(ingredients_list)
    instructions = ','.join(instructions_list)

    if title is None or description is None or ingredients is None or instructions is None or category is None or image is None:
        return jsonify({'error': 'Missing required data in the request'}), 400

    with current_app.app_context():
        new_recipe = Recipe(
            title=title,
            description=description,
            ingredients=ingredients,
            instructions=instructions,
            category=category,
            image=image,
            user_username=user.username
        )
        db.session.add(new_recipe)
        db.session.commit()

    return jsonify({'message': 'Recipe created successfully'}), 200

@app.route('/api/recipes', methods=['GET'])
@cross_origin(origin="*")
def get_recipes():
    print(g.user)
    user = g.user
    if not user:
        return jsonify({'error': 'User not authenticated'}), 401
    
    recipes = Recipe.query.filter_by(user_username=user.username).all()

    recipes_list = [
        {
            'id': recipe.id,
            'title': recipe.title,
            'description': recipe.description,
            'ingredients': recipe.ingredients,
            'instructions': recipe.instructions,
            'category': recipe.category,
            'image': recipe.image,
            'user_username': recipe.user_username
        }
        for recipe in recipes
    ]
    return jsonify(recipes_list)

@app.route('/api/recipes/<int:recipe_id>', methods=['DELETE'])
@cross_origin(origin="*")
def delete_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if recipe:
        db.session.delete(recipe)
        db.session.commit()
        return '', 204
    else:
        return jsonify({'error': 'Recipe not found'}), 404