# app/routes.py
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from ..models import db, User, Transaction, Budget
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash

bp = Blueprint('web', __name__)

@bp.route('/')
def home():
    #if request.accept_mimetypes.accept_json:
    #    return jsonify({"message": "Welcome to the Personal Finance Dashboard"}), 200
    return render_template('home.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json() if request.accept_mimetypes.accept_json else request.form
        if User.query.filter_by(username=data['username']).first():
            return jsonify({"message": "Username already exists"}), 400 if request.accept_mimetypes.accept_json else render_template('register.html', error="Username already exists")
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"message": "Email already exists"}), 400 if request.accept_mimetypes.accept_json else render_template('register.html', error="Email already exists")
        new_user = User(username=data['username'], email=data['email'])
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('web.home'))
    
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            return render_template('login.html', error="Invalid username or password")
        login_user(user, remember=remember)
        return redirect(url_for('web.home'))

    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('web.home'))

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('home.html')