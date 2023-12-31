from flask import g, jsonify, request
from flask_cors import cross_origin
from config import db, app
from models.user import User
from passlib.hash import scrypt
from service.user_service import add_user
from flask_jwt_extended import create_access_token
from service.serialize_recipe import serialize_recipe

@app.route('/register', methods=['POST'])
@cross_origin(origin="*")
def register():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']

        try:
            add_user(username, name, password)
            return jsonify({'message': 'User registered successfully'}), 200
        except Exception as e:
            return jsonify({'message': str(e)}), 500

from flask import jsonify

@app.route('/login', methods=['GET', 'POST'])
@cross_origin(origin="*")
def login():
    if request.method == 'POST':
        data = request.get_json()

        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'message': 'Invalid request'}), 400

        username = data['username']
        password = data['password']

        user = User.query.filter_by(username=username).first()

        if user:
            if scrypt.verify(password, user.password):
                access_token = create_access_token(identity=user.username)
                user.access_token = access_token
                db.session.commit()
                print(user.favorite_recipes)
                user_data = {
                    'username': user.username,
                    'name': user.name,
                    'password': user.password,
                    'recipes': [recipe.id for recipe in user.recipes],
                    'favorites_list': [recipe.id for recipe in user.favorite_recipes],
                }
                response_data = {
                    'user': user_data,
                    'access_token': access_token
                }
                return jsonify(response_data), 200
            return jsonify({'message': 'Invalid username or password'}), 401

    return jsonify({'message': 'Welcome to the login page'}), 200

@app.route('/logout', methods=['POST'])
@cross_origin(origins="*")
def logout():
    try:
        data = request.get_json()

        token = data['token']

        user = User.query.filter_by(access_token=token).first()

        if not user:
            return jsonify({'message': 'user with token not found'}), 404
        
        user.token = None

        db.session.commit()
        return jsonify({'message': 'successful'}), 200
    
    except Exception as e:
        return jsonify({'message': f'json contents invalid, {e}'}), 400
    

