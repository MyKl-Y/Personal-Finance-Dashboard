# app/web.py
import re

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, render_template_string
from ..models import db, User, Transaction, Budget
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash

bp = Blueprint('web', __name__)

@bp.route('/toggle-login-input', methods=['POST'])
def toggle_login_input():
    use_email = 'useEmail' in request.form
    username_or_email = request.form.get('username_or_email')
    if use_email:
        input_html = """
        <div id="login-input-container">
            <div class="form-floating mb-3">
                <input 
                    class="form-control" 
                    type="email" 
                    id="username_or_email" 
                    name="username_or_email" 
                    placeholder="Email" 
                    value="{{ request.form.get('username_or_email', '') }}"
                    required>
                <label for="username_or_email">Email <span class="text-danger">*</span></label>
                <div class="invalid-feedback">Please provide a valid email.</div>
            </div>
        </div>
        """
    else:
        input_html = """
        <div id="login-input-container">
            <div class="form-floating mb-3">
                <input 
                    class="form-control" 
                    type="text" 
                    id="username_or_email" 
                    name="username_or_email" 
                    placeholder="Username" 
                    value="{{ request.form.get('username_or_email', '') }}"
                    required>
                <label for="username_or_email">Username <span class="text-danger">*</span></label>
                <div class="invalid-feedback">Please provide a valid username.</div>
            </div>
        </div>
        """
    
    return render_template_string(input_html)

@bp.route('/')
def home():
    #if request.accept_mimetypes.accept_json:
    #    return jsonify({"message": "Welcome to the Personal Finance Dashboard"}), 200
    return render_template('home.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            return render_template('register.html', username=username, email=email, error="Username already exists.")
        if User.query.filter_by(email=email).first():
            return render_template('register.html', username=username, email=email, error="Email already exists.")
        if email.count('@') != 1 or email.count('.') < 1:
            return render_template('register.html', username=username, email=email, error="Email address is invalid.")
        new_user = User(username=username, email=email)
        if len(password) < 8:
            return render_template('register.html', username=username, email=email, error="Password must be at least 8 characters long.")
        if not re.search(r'[a-z]', password):
            return render_template('register.html', username=username, email=email, error="Password must contain at least one lowercase letter.")
        if not re.search(r'[A-Z]', password):
            return render_template('register.html', username=username, email=email, error="Password must contain at least one uppercase letter.")
        if not re.search(r'[0-9]', password):
            return render_template('register.html', username=username, email=email, error="Password must contain at least one number.")
        if not re.search(r'[-_!@$%*&./?]', password):
            return render_template('register.html', username=username, email=email, error="Password must contain at least one special character (-_!@$%*&./?).")
        if not re.fullmatch(r'[a-zA-Z0-9-_!@$%*&./?]{8,}', password):
            return render_template('register.html', username=username, email=email, error="Password must contain only letters, numbers, special characters (-_!@$%*&./?) and be at least 8 characters long.")
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('web.login'))
    
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email')
        password = request.form.get('password')
        remember = 'remember' in request.form
        use_email = 'useEmail' in request.form
        # Validate if the input is an email or username based on the checkbox state
        if use_email:
            user = User.query.filter_by(email=username_or_email).first()
        else:
            user = User.query.filter_by(username=username_or_email).first()
        if user is None:
            if use_email:
                return render_template('login.html', username_or_email=username_or_email, error="Invalid email")
            else:
                return render_template('login.html', username_or_email=username_or_email, error="Invalid username")
        if not user.check_password(password):
            return render_template('login.html', username_or_email=username_or_email, error="Invalid password")
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
    return render_template('dashboard.html')

@bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')