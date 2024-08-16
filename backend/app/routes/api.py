# app/api.py
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from ..models import db, User, Transaction, Budget
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash

bp = Blueprint('api', __name__)

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
    return jsonify({"message": "Logged in successfully", "session": request.cookies.get('session')}), 200

@bp.route('/api/current', methods=['GET'])
@login_required
def current():
    return jsonify({"id": current_user.id, "username": current_user.username, "email": current_user.email}), 200

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

@bp.route('/api/transactions/<int:transaction_id>', methods=['DELETE', 'GET', 'PUT', 'PATCH'])
@login_required
def transaction(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return jsonify({"message": "Transaction not found"}), 404
    if transaction.user_id != current_user.id:
        return jsonify({"message": "Access denied"}), 403
    if request.method == 'DELETE':
        db.session.delete(transaction)
        db.session.commit()
        return jsonify({"message": "Transaction deleted successfully"})
    elif request.method == 'GET':
        return jsonify(transaction.to_dict())
    else:
        data = request.get_json()
        if 'amount' in data:
            transaction.amount = data['amount']
        if 'category' in data:
            transaction.category = data['category']
        db.session.commit()
        return jsonify({"message": "Transaction updated successfully"})
    
@bp.route('/api/budgets', methods=['POST'])
@login_required
def add_budget():
    data = request.get_json()
    new_budget = Budget(user_id=data['user_id'], name=data['name'], total_amount=data['total_amount'], start_date=data['start_date'], end_date=data['end_date'], categories=data['categories'])
    db.session.add(new_budget)
    db.session.commit()
    return jsonify({"message": "Budget added successfully"}), 201

@bp.route('/api/budgets/<int:user_id>', methods=['GET'])
@login_required
def get_budgets(user_id):
    if user_id != current_user.id:
        return jsonify({"message": "Access denied"}), 403
    budgets = Budget.query.filter_by(user_id=user_id).all()
    return jsonify([b.to_dict() for b in budgets])

@bp.route('/api/budgets/<int:budget_id>', methods=['DELETE', 'GET', 'PUT', 'PATCH'])
@login_required
def budget(budget_id):
    budget = Budget.query.get(budget_id)
    if not budget:
        return jsonify({"message": "Budget not found"}), 404
    if budget.user_id != current_user.id:
        return jsonify({"message": "Access denied"}), 403
    if request.method == 'DELETE':
        db.session.delete(budget)
        db.session.commit()
        return jsonify({"message": "Budget deleted successfully"})
    elif request.method == 'GET':
        return jsonify(budget.to_dict())
    else:
        data = request.get_json()
        if 'name' in data:
            budget.name = data['name']
        if 'total_amount' in data:
            budget.total_amount = data['total_amount']
        if 'start_date' in data:
            budget.start_date = data['start_date']
        if 'end_date' in data:
            budget.end_date = data['end_date']
        if 'categories' in data:
            budget.categories = data['categories']
        db.session.commit()
        return jsonify({"message": "Budget updated successfully"})