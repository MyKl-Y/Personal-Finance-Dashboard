# app/routes.py
from flask import Blueprint, request, jsonify
from .models import db, User, Transaction
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash

bp = Blueprint('main', __name__)

@bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Username already exists"}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already exists"}), 400
    new_user = User(username=data['username'], email=data['email'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201

@bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user is None or not user.check_password(data['password']):
        return jsonify({"message": "Invalid username or password"}), 401
    login_user(user)
    return jsonify({"message": "Logged in successfully"}), 200

@bp.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200

@bp.route('/api/users', methods=['GET'])
@login_required
def users():
    if current_user.id != 1:
        return jsonify({"message": "Access denied"}), 403
    #users = db.session.query(User).all()
    users = User.query.all() # Same as above
    return jsonify([f'{u.id}: {u.username} ({u.email}) [{u.password_hash}]' for u in users])

@bp.route('/api/users/<int:user_id>', methods=['DELETE', 'GET', 'PUT', 'PATCH'])
@login_required
def user(user_id):
    if user_id != current_user.id:
        return jsonify({"message": "Access denied"}), 403
    if request.method == 'DELETE':
        return delete_user(user_id)
    elif request.method == 'GET':
        return get_user(user_id)
    else:
        return update_user(user_id)
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"})
    else:
        return jsonify({"message": "User not found"}), 404
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({"username": user.username, "email": user.email, "password_hash": user.password_hash})
    else:
        return jsonify({"message": "User not found"}), 404
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    data = request.get_json()
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    if 'password' in data:
        user.password_hash = generate_password_hash(data['password'])
    db.session.commit()
    return jsonify({"message": "User updated successfully"})

@bp.route('/api/transactions', methods=['POST'])
@login_required
def add_transaction():
    data = request.get_json()
    new_transaction = Transaction(user_id=data['user_id'], amount=data['amount'], category=data['category'])
    db.session.add(new_transaction)
    db.session.commit()
    return jsonify({"message": "Transaction added successfully"}), 201

@bp.route('/api/transactions/<int:user_id>', methods=['GET'])
@login_required
def get_transactions(user_id):
    if user_id != current_user.id:
        return jsonify({"message": "Access denied"}), 403
    transactions = Transaction.query.filter_by(user_id=user_id).all()
    return jsonify([t.to_dict() for t in transactions])
