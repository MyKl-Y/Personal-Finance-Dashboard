# app/web.py
import io
import re
import datetime
import random
import sys 
import math

#import bankstatementparser as bsp

from flask import Blueprint, flash, Response, request, jsonify, render_template, redirect, url_for, render_template_string
from ..models import db, User, Transaction, Budget, Account
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime as dt

import numpy as np
import pandas as pd

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
                    <option value="Housing">Housing</option>
                    <option value="Transportation">Transportation</option>
                    <option value="Utilities">Utilities</option>
                    <option value="Insurance">Insurance</option>
                    <option value="Medical">Medical</option>
                    <option value="Savings">Savings</option>
                    <option value="Investments">Investments</option>
                    <option value="Retirement">Retirement</option>
                    <option value="Personal">Personal</option>
                    <option value="Recreation">Recreation</option>
                    <option value="Debt">Debt</option>
                    <option value="Education">Education</option>
                    <option value="Childcare">Childcare</option>
                    <option value="Gifts">Gifts</option>
                    <option value="Donations">Donations</option>
                    <option value="Food">Food</option>
                    <option value="Subscriptions">Subscriptions</option>
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

@bp.route('/expenses-by-category')
@login_required
def chart_data():
    # Get the transactions for the current user
    transactions = Transaction.query.filter_by(user_id=current_user.id, type='2').all()

    # Example: Group transactions by category for a pie chart
    categories = {}
    for transaction in transactions:
        #if transaction.category not in categories:
        #    categories[transaction.category] = 0
        #categories[transaction.category] += transaction.amount if transaction.type == '1' else -transaction.amount
        categories[transaction.category] = categories.get(transaction.category, 0) + transaction.amount

    data = {
        "labels": list(categories.keys()),
        "datasets": [{
            "label": "Expenses by Category",
            "data": list(categories.values()),
            "backgroundColor": [
                "rgba(255, 36, 0, 0.4)",
                "rgba(224, 17, 95, 0.4)",
                "rgba(191, 10, 48, 0.4)",
                "rgba(240, 128, 128, 0.4)"
            ],
            "borderColor": [
                "rgba(255, 36, 0, 1)",
                "rgba(224, 17, 95, 1)",
                "rgba(191, 10, 48, 1)",
                "rgba(240, 128, 128, 1)"
            ],
            "borderWidth": 1
        }]
    }

    return jsonify(data)

@bp.route('/balance-by-account')
@login_required
def balance_by_account():
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    total_balance = sum(account.balance for account in accounts)
    
    datasets = []
    for account in accounts:
        percentage = (account.balance / total_balance) * 100
        datasets.append({
            "label": f"{account.name} ({percentage:.2f}%) - ${account.balance:,.2f}",
            "data": [percentage],  # Store the percentage as the data value
            "backgroundColor": [
                "rgba(0, 128, 255, 0.2)",
                "rgba(101, 147, 245, 0.2)",
                "rgba(16, 52, 166, 0.2)",
                "rgba(14, 77, 146, 0.2)"
            ],
            "borderColor": [
                "rgba(0, 128, 255, 1)",
                "rgba(101, 147, 245, 1)",
                "rgba(16, 52, 166, 1)",
                "rgba(14, 77, 146, 1)"
            ],
            "borderWidth": 1
        })
    
    data = {
        "labels": ["Accounts"],  # We only need one label because everything stacks in one column
        "datasets": datasets
    }
    
    return jsonify(data)


@bp.route('/income-by-category')
@login_required
def income_by_category():
    transactions = Transaction.query.filter_by(user_id=current_user.id, type='1').all()
    categories = {}
    for transaction in transactions:
        categories[transaction.category] = categories.get(transaction.category, 0) + transaction.amount

    data = {
        "labels": list(categories.keys()),
        "datasets": [{
            "label": "Income by Category",
            "data": list(categories.values()),
            "backgroundColor": [
                "rgba(32, 178, 170, 0.4)",
                "rgba(0, 255, 205, 0.4)",
                "rgba(3, 192, 60, 0.4)",
                "rgba(124, 252, 0, 0.4)"
            ],
            "borderColor": [
                "rgba(32, 178, 170, 1)",
                "rgba(0, 255, 205, 1)",
                "rgba(3, 192, 60, 1)",
                "rgba(124, 252, 0, 1)"
            ],
            "borderWidth": 1
        }]
    }
    return jsonify(data)

@bp.route('/income-sparkline')
@login_required
def income_sparkline():
    transactions = Transaction.query.filter_by(user_id=current_user.id, type='1').all()
    transactions.sort(key=lambda x: x.timestamp)
    dates = [transaction.timestamp.strftime("%Y-%m-%d") for transaction in transactions]
    amounts = [transaction.amount for transaction in transactions]

    data = {
        "labels": dates,
        "datasets": [{
            "data": amounts,
            "borderColor": "rgba(75, 192, 192, 1)",
            "fill": False
        }]
    }
    return jsonify(data)

@bp.route('/expenses-sparkline')
@login_required
def expenses_sparkline():
    transactions = Transaction.query.filter_by(user_id=current_user.id, type='2').all()
    transactions.sort(key=lambda x: x.timestamp)
    dates = [transaction.timestamp.strftime("%Y-%m-%d") for transaction in transactions]
    amounts = [transaction.amount for transaction in transactions]

    data = {
        "labels": dates,
        "datasets": [{
            "data": amounts,
            "borderColor": "rgba(255, 99, 132, 1)",
            "fill": False
        }]
    }
    return jsonify(data)

@bp.route('/income-expense-combined')
@login_required
def income_expense_combined():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    transactions.sort(key=lambda x: x.timestamp)
    dates = list(sorted(set([transaction.timestamp.strftime("%Y-%m-%d") for transaction in transactions])))

    income_data = []
    expense_data = []
    for date in dates:
        daily_income = sum(transaction.amount for transaction in transactions if transaction.timestamp.strftime("%Y-%m-%d") == date and transaction.type == '1')
        daily_expense = sum(transaction.amount for transaction in transactions if transaction.timestamp.strftime("%Y-%m-%d") == date and transaction.type == '2')
        income_data.append(daily_income)
        expense_data.append(daily_expense)

    data = {
        "labels": dates,
        "datasets": [
            {
                "label": "Income",
                "data": income_data,
                "backgroundColor": "rgba(75, 192, 192, .2)",
                "borderColor": "rgba(75, 192, 192, 1)",
                "fill": False
            },
            {
                "label": "Expenses",
                "data": expense_data,
                "backgroundColor": "rgba(255, 99, 132, .2)",
                "borderColor": "rgba(255, 99, 132, 1)",
                "fill": False
            }
        ]
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
        timestamp = request.form.get('date')
        print(timestamp, datetime.datetime.fromisoformat(timestamp),datetime.datetime.now(datetime.timezone.utc))
        new_transaction = Transaction(
            user_id=current_user.id,
            amount=amount,
            description=description,
            category=category,
            account=account,
            type=transaction_type,
            timestamp=datetime.datetime.fromisoformat(timestamp)
        )
        db.session.add(new_transaction)
        account_to_change = Account.query.filter_by(name=account).first()
        if transaction_type == '1':
            account_to_change.balance += float(amount)
        elif transaction_type == '2':
            account_to_change.balance -= float(amount)
        db.session.commit()
        return redirect(url_for('web.dashboard'))
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    if accounts:
        has_accounts = True
    else:
        has_accounts = False
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    return render_template('transactions.html', transactions=transactions, accounts=accounts, has_accounts=has_accounts)

@bp.route('/import', methods=['POST'])
@login_required
def import_transactions():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('web.transactions'))
    
    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('web.transactions'))
    
    try:
        #filename = sys.argv[1]
        type = request.form.get('type')
        bank = request.form.get('bank')
        account = request.form.get('account')
        print(type, bank, account)
        if type == '2':
            if bank == '2':
                #df = pd.read_csv(filename)
                df = pd.read_csv(io.StringIO(file.stream.read().decode('utf-8')))
                for index, row in df.iterrows():
                    desc = row['Transaction Description']
                    category = math.nan
                    amount = 0

                    row['Transaction Date'] = dt.strptime(row['Transaction Date'], '%m/%d/%Y').strftime('%Y-%m-%d')

                    if row['Transaction Type'] == 'Debit':
                        row['Transaction Type'] = '2'
                        amount = float(row['Debit'].replace('$', '').replace(',', ''))
                    else:
                        row['Transaction Type'] = '1'
                        amount = float(row['Credit'].replace('$', '').replace(',', ''))

                    if row['Transaction Type'] == '1':
                        if re.search(r'interest', desc, re.IGNORECASE):
                            category = 'Interest'
                        elif re.search(r'deposit.*dda to dda', desc, re.IGNORECASE):
                            category = 'Salary'
                        elif re.search(r'acctverify', desc, re.IGNORECASE):
                            category = 'Other'
                    else:
                        if re.search(r'acctverify', desc, re.IGNORECASE):
                            category = 'Other'
                        
                    new_transaction = Transaction(
                        user_id=current_user.id,
                        amount=amount,
                        description=desc,
                        category=category,
                        account=account,
                        type=row['Transaction Type'],
                        timestamp=datetime.datetime.fromisoformat(f"{row['Transaction Date']}T00:00:00")
                    )
                    db.session.add(new_transaction)
                    account_to_change = Account.query.filter_by(name=account).first()
                    if row['Transaction Type'] == '1':
                        account_to_change.balance += float(amount)
                    elif row['Transaction Type'] == '2':
                        account_to_change.balance -= float(amount)
                    db.session.commit()
                    #print(row['Transaction Date'], amount, row['Transaction Type'], category, row['Transaction Description'])
        elif type == '1':
            if bank == '1':
                #df = pd.read_csv(filename)
                #df = pd.read_csv(io.StringIO(file.stream.read().decode('utf-8')))
                #if 'Date' not in df.columns:
                #    headers = ['Date', 'Amount', 'Type', 'Category', 'Description']
                #    #df.to_csv(filename, header=headers, index=False)
                #    #df = pd.read_csv(filename)
                #    temp = df.to_csv(io.StringIO(file.stream.read().decode('utf-8')), header=headers, index=False)
                #    df = pd.read_csv(temp)

                raw_data = file.stream.read().decode('utf-8')
                #print(raw_data)
                if 'Transaction Date' not in raw_data:
                    headers = ['Transaction Date', 'Amount', 'Type', 'Category', 'Description']
                    raw_data = f"{','.join(headers)}\n" + raw_data

                df = pd.read_csv(io.StringIO(raw_data))

                for index, row in df.iterrows():
                    amount = float(row['Amount'])
                    desc = row['Description']

                    row['Transaction Date'] = dt.strptime(row['Transaction Date'], '%m/%d/%Y').strftime('%Y-%m-%d')
                    row['Amount'] = float(row['Amount'])

                    if row['Amount'] < 0:
                        row['Type'] = '2'
                    else:
                        row['Type'] = '1'

                    if row['Type'] == '1':
                        if re.search(r'pay|salary', desc, re.IGNORECASE):
                            row['Category'] = 'Salary'
                        elif re.search(r'from sombreros|zelle|transfer|irs.*tax', desc, re.IGNORECASE):
                            row['Category'] = 'Gift'
                        else:
                            row['Category'] = 'Other'
                    else:
                        if re.search(r'recurring payment|mojang|nintendo', desc, re.IGNORECASE):
                            row['Category'] = 'Subscription'
                        elif re.search(r'recurring transfer', desc, re.IGNORECASE):
                            row['Category'] = 'Savings'
                        elif re.search(r'FID BKG SVC LLC MONEYLINE', desc, re.IGNORECASE):
                            row['Category'] = 'Investments'
                        elif re.search(r'kindercare', desc, re.IGNORECASE):
                            row['Category'] = 'Childcare'
                        elif re.search(r'zelle to.*lucie', desc, re.IGNORECASE):
                            row['Category'] = 'Gifts'
                        else:
                            row['Category'] = 'Other'
                    
                    row['Amount'] = abs(row['Amount'])

                    #print(row['Date'], row['Amount'], row['Type'], row['Category'], row['Description'])

                    new_transaction = Transaction(
                        user_id=current_user.id,
                        amount=abs(row['Amount']),
                        description=row['Description'],
                        category=row['Category'],
                        account=account,
                        type=row['Type'],
                        timestamp=datetime.datetime.fromisoformat(
                            f"{row['Transaction Date']}T00:00:00"
                        )
                    )
                    db.session.add(new_transaction)
                    account_to_change = Account.query.filter_by(name=account).first()
                    if row['Type'] == '1':
                        account_to_change.balance += float(row['Amount'])
                    elif row['Type'] == '2':
                        account_to_change.balance -= float(row['Amount'])
                    #print(row['Date'], abs(row['Amount']), row['Type'], row['Category'], row['Description'])
    except Exception as e:
        print(e)
        flash('Error parsing file')
        return redirect(url_for('web.transactions'))
    
    db.session.commit()
    return redirect(url_for('web.dashboard'))


@bp.route('/accounts', methods=['GET', 'POST'])
@login_required
def accounts():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        account_type = request.form.get('account-type')
        balance = request.form.get('balance')

        # Check if an account with the same name already exists for the user
        existing_account = Account.query.filter_by(user_id=current_user.id, name=name).first()
        if existing_account:
            flash('An account with this name already exists. Please choose a different name.')
            return redirect(url_for('web.transactions'))

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
        transactions = Transaction.query.filter_by(account=account.name).all()
        for transaction in transactions:
            db.session.delete(transaction)
        db.session.delete(account)
        db.session.commit()
        return redirect(url_for('web.dashboard'))
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    return render_template('accounts.html', accounts=accounts)

@bp.route('/account/<int:account_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def account(account_id):
    if request.method == 'GET':
        account = Account.query.get(account_id)
        return render_template('account.html', account=account)
    if request.method == 'PUT':
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
        account = Account.query.get(account_id)
        transactions = Transaction.query.filter_by(account=account.name).all()
        for transaction in transactions:
            db.session.delete(transaction)
        db.session.delete(account)
        db.session.commit()
        return redirect(url_for('web.dashboard'))