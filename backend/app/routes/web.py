# app/web.py
import io
import re
import datetime
import random

from flask import Blueprint, Response, request, jsonify, render_template, redirect, url_for, render_template_string
from ..models import db, User, Transaction, Budget, Account
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash

bp = Blueprint('web', __name__)

@bp.context_processor
def inject_now():
    return {'now': datetime.datetime.now()}

@bp.route('/account-type', methods=['POST'])
def account_type():
    transaction_type = request.values.get('account-type')
    if transaction_type == '1':
        input_html = """<span id="account-type"></span>"""
    elif transaction_type == '2':
        input_html = """
            <div id="account-type" class="form-floating mb-3">
                <input type="number" min="0" step="0.01" class="form-control" id="interest" name="interest" placeholder="Interest Rate" required>
                <label for="interest">Interest Rate</label>
            </div>
        """
    else:
        input_html = """<span id="account-type"></span>"""
    return render_template_string(input_html)

@bp.route('/transaction-type', methods=['POST'])
def transaction_type():
    transaction_type = request.values.get('transaction-type')
    if transaction_type == '1':
        input_html = """
            <span id="transaction-type">
                <select name="category" class="form-select mb-3">
                    <option selected>Category</option>
                    <option value="Salary">Salary</option>
                    <option value="Gift">Gift</option>
                    <option value="Interest">Interest</option>
                    <option value="Other">Other</option>
                </select>
                <div class="input-group mb-3">
                    <span id="transaction-type" class="input-group-text bg-success text-light">+</span>
                    <span class="input-group-text">$</span>
                    <div class="form-floating">
                        <input type="number" min="0" step="0.01" class="form-control" id="amount" name="amount" placeholder="Amount" required>
                        <label for="amount">Amount</label>
                    </div>
                </div>
            </span>
        """
    elif transaction_type == '2':
        input_html = """
            <span id="transaction-type">
                <select name="category" class="form-select mb-3">
                    <option selected>Category</option>
                    <option value="Bills">Housing</option>
                    <option value="Transportation">Transportation</option>
                    <option value="Utilities">Utilities</option>
                    <option value="Insurance">Insurance</option>
                    <option value="Medical">Medical</option>
                    <option value="Savings">Savings</option>
                    <option value="Personal">Personal</option>
                    <option value="Recreation">Recreation</option>
                    <option value="Debt">Debt</option>
                    <option value="Education">Education</option>
                    <option value="Childcare">Childcare</option>
                    <option value="Gifts">Gifts</option>
                    <option value="Donations">Donations</option>
                    <option value="Food">Food</option>
                    <option value="Other">Other</option>
                </select>
                <div class="input-group mb-3">
                    <span id="transaction-type" class="input-group-text bg-danger text-light">-</span>
                    <span class="input-group-text">$</span>
                    <div class="form-floating">
                        <input type="number" min="0" step="0.01" class="form-control" id="amount" name="amount" placeholder="Amount" required>
                        <label for="amount">Amount</label>
                    </div>
                </div>
            </span>
        """
    else:
        input_html = """
            <span id="transaction-type">
                <select name="category" class="form-select mb-3" disabled>
                    <option selected>Category</option>
                </select>
                <div class="input-group mb-3">
                    <span id="transaction-type" class="input-group-text">?</span>
                    <span class="input-group-text">$</span>
                    <div class="form-floating">
                        <input type="number" min="0" step="0.01" class="form-control" id="amount" name="amount" placeholder="Amount" disabled required>
                        <label for="amount">Amount</label>
                    </div>
                </div>
            </span>
        """
    return render_template_string(input_html)

@bp.route('/dashboard-mode', methods=['POST'])
def dashboard_mode():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()

    year_month_combinations = set([(transaction.timestamp.year, transaction.timestamp.month) for transaction in transactions])

    year_month_days_combinations = set([(transaction.timestamp.year, transaction.timestamp.month, transaction.timestamp.day) for transaction in transactions])

    mode = request.values.get('dashboard-mode')

    years = {year for year, _ in year_month_combinations}
    months = {(year, month) for year, month in year_month_combinations}
    days = {(year, month, day) for year, month, day in year_month_days_combinations}

    if mode == 'Mode' or mode == '1':
        # No selected or YTD
        input_html = """
            <div id="mode-type">
                <select class="form-select" aria-label="Type" disabled>
                    <option selected>Type</option>
                </select>
            </div>
        """
    elif mode == "2" and years:
        # Yearly
        input_html = """
            <div id="mode-type">
                <select class="form-select" aria-label="Type">
                    <option selected>Type</option>
                    {% for year in years %}
                    <option value="{{ year }}">{{ year }}</option>
                    {% endfor %}
                </select>
            </div>
        """
    elif mode == "3" and months:
        # Monthly
        input_html = """
            <div id="mode-type">
                <select class="form-select" aria-label="Type">
                    <option selected>Type</option>
                    {% for year, month in months %}
                    <option value="{{ year }}-{{ month }}">{{ year }}-{{ month }}</option>
                    {% endfor %}
                </select>
            </div>
        """
    elif mode in ["4", "5"] and days:
        # Weekly or Daily
        input_html = """
            <div id="mode-type">
                <select class="form-select" aria-label="Type">
                    <option selected>Type</option>
                    {% for year, month, day in days %}
                    <option value="{{ year }}-{{ month }}-{{ day }}">{{ year }}-{{ month }}-{{ day }}</option>
                    {% endfor %}
                </select>
            </div>
        """
    else:
        input_html = """
            <div id="mode-type">
                <select class="form-select" aria-label="Type" disabled>
                    <option selected>Type</option>
                </select>
            </div>
        """
    return render_template_string(input_html, years=years, months=months, days=days)

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

@bp.route('/chart-data')
@login_required
def chart_data():
    # Get the transactions for the current user
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()

    # Example: Group transactions by category for a pie chart
    categories = {}
    for transaction in transactions:
        if transaction.category not in categories:
            categories[transaction.category] = 0
        categories[transaction.category] += transaction.amount if transaction.type == '1' else -transaction.amount

    data = {
        "labels": list(categories.keys()),
        "datasets": [{
            "label": "Expenses by Category",
            "data": list(categories.values()),
            "backgroundColor": [
                "rgba(75, 192, 192, 0.2)",
                "rgba(54, 162, 235, 0.2)",
                "rgba(255, 206, 86, 0.2)",
                "rgba(255, 99, 132, 0.2)"
            ],
            "borderColor": [
                "rgba(75, 192, 192, 1)",
                "rgba(54, 162, 235, 1)",
                "rgba(255, 206, 86, 1)",
                "rgba(255, 99, 132, 1)"
            ],
            "borderWidth": 1
        }]
    }

    return jsonify(data)


@bp.route('/dashboard')
@login_required
def dashboard():
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    if accounts:
        has_accounts = True
    else:
        has_accounts = False
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    total_balance = sum([account.balance for account in accounts])

    return render_template(
        'dashboard.html',
        accounts=accounts,
        has_accounts=has_accounts,
        transactions=transactions,
        total_balance=total_balance
    )

@bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@bp.route('/transaction/<int:transaction_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def transaction(transaction_id):
    if request.method == 'GET':
        transaction = Transaction.query.get(transaction_id)
        return render_template('transaction.html', transaction=transaction)
    if request.method == 'PUT':
        amount = request.form.get('amount')
        description = request.form.get('description')
        category = request.form.get('category')
        account = request.form.get('account')
        transaction_type = request.form.get('transaction-type')
        transaction = Transaction.query.get(transaction_id)
        account_to_change = Account.query.filter_by(name=account).first()
        if transaction.type == '1':
            account_to_change.balance += float(transaction.amount)
            account_to_change.balance -= float(amount)
        elif transaction.type == '2':
            account_to_change.balance -= float(transaction.amount)
            account_to_change.balance += float(amount)
        transaction.amount = amount
        transaction.description = description
        transaction.category = category
        transaction.account = account
        transaction.type = transaction_type
        db.session.commit()
        return redirect(url_for('web.dashboard'))
    if request.method == 'DELETE':
        transaction = Transaction.query.get(transaction_id)
        account_to_change = Account.query.filter_by(name=transaction.account).first()
        if transaction.type == '1':
            account_to_change.balance -= float(transaction.amount)
        elif transaction.type == '2':
            account_to_change.balance += float(transaction.amount)
        db.session.delete(transaction)
        db.session.commit()

        remaining_transactions = Transaction.query.filter_by(user_id=current_user.id).all()
        return render_template('account_balance.html', account=account_to_change, transactions=remaining_transactions)

@bp.route('/transactions', methods=['GET', 'POST'])
@login_required
def transactions():
    if request.method == 'POST':
        amount = request.form.get('amount')
        description = request.form.get('description')
        category = request.form.get('category')
        account = request.form.get('account')
        transaction_type = request.form.get('transaction-type')
        new_transaction = Transaction(
            user_id=current_user.id,
            amount=amount,
            description=description,
            category=category,
            account=account,
            type=transaction_type
        )
        db.session.add(new_transaction)
        account_to_change = Account.query.filter_by(name=account).first()
        if transaction_type == '1':
            account_to_change.balance += float(amount)
        elif transaction_type == '2':
            account_to_change.balance -= float(amount)
        db.session.commit()
        return redirect(url_for('web.dashboard'))
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    return render_template('transactions.html', transactions=transactions)

@bp.route('/accounts', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
def accounts():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        account_type = request.form.get('account-type')
        balance = request.form.get('balance')
        new_account = Account(
            user_id=current_user.id,
            name=name,
            description=description,
            type=account_type,
            balance=balance
        )
        db.session.add(new_account)
        db.session.commit()
        return redirect(url_for('web.dashboard'))
    if request.method == 'PUT':
        account_id = request.form.get('account-id')
        name = request.form.get('name')
        description = request.form.get('description')
        account_type = request.form.get('account-type')
        balance = request.form.get('balance')
        account = Account.query.get(account_id)
        account.name = name
        account.description = description
        account.type = account_type
        account.balance = balance
        db.session.commit()
        return redirect(url_for('web.dashboard'))
    if request.method == 'DELETE':
        account_id = request.form.get('account-id')
        account = Account.query.get(account_id)
        db.session.delete(account)
        db.session.commit()
        return redirect(url_for('web.dashboard'))
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    return render_template('accounts.html', accounts=accounts)