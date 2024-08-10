import requests
from fasthtml.fastapp import fast_app
from fasthtml.common import *

db = database('../backend/instance/finance.db')
users, transactions, budgets = db.t.users, db.t.transactions, db.t.budgets
User, Transaction, Budget = users.dataclass(), transactions.dataclass(), budgets.dataclass()

login_redirect = RedirectResponse('/login', status_code=303)

def before(req, sess):
    auth = sess.get('auth', None)
    req.scope['auth'] = auth
    if not auth: return login_redirect

beforeware = Beforeware(
    before,
    skip=[r'/favicon\.ico', r'/static/.*', r'.*\.css', r'.*\.js', '/login', '/']
)

def not_found(req, exc): return Titled("404 Not Found")

exceptions = {404: not_found}

app, rt = fast_app(exception_handlers=exceptions, before=beforeware)

setup_toasts(app)

def login_form():
    return Div(
        Titled("Personal Finance Dashboard"), 
        H1('Login'),
        Form(
            Input(name='username', placeholder='Username', cls='username-input'),
            Input(name='password', type='password', placeholder='Password', cls='password-input'),
            Button('Login', cls='login-button'),
            cls='login-form',
            #hx_post=True
            method='post',
            action='/login'
        ),
        cls='login-container'
    )

def register_form():
    return Div(
        Title("Personal Finance Dashboard"), 
        H1('Register'),
        Form(
            Input(name='username', placeholder='Username', cls='username-input'),
            Input(name='email', placeholder='Email', cls='email-input'),
            Input(name='password', type='password', placeholder='Password', cls='password-input'),
            Button('Register', cls='register-button'),
            cls='register-form',
            #hx_post=True
            method='post',
            action='/register'
        ),
        cls='register-container'
    )

@rt('/')
def get():
    return (
        Title("Personal Finance Dashboard"), 
        Main(
            H1('Hello, welcome!')
        ),
    )
    #response = requests.get('http://localhost:6969/api/users')
    #data = response.json()
    #return P(''.join([user for user in data]))

@rt('/login')
async def post(username: str, password: str, session):
    if not username or not password: return login_redirect
    response = requests.post('http://localhost:6969/api/login', json={'username': username, 'password': password})
    if response.status_code != 200:
        add_toast(session, response.json()['message'], 'error')
        return (
            login_form(),
        )
    add_toast(session, response.json()['message'], 'success')
    return (
        login_form(),
        RedirectResponse('/dashboard', status_code=303),
        Script('setTimeout(() => window.location.href = "/dashboard", 2000)')
    )

@rt('/login')
def get():
    return login_form()

@rt('/register')
async def post(username: str, email: str, password: str, session):
    response = requests.post('http://localhost:6969/api/register', json={'username': username, 'email': email, 'password': password})
    if response.status_code != 201:
        add_toast(session, response.json()['message'], 'error')
        return (
            register_form(),
        )
    add_toast(session, response.json()['message'], 'success')
    return (
        register_form(),
        Script('setTimeout(() => window.location.href = "/login", 2000)')
    )

@rt('/register')
def get():
    return register_form()

@rt('/dashboard')
async def get(auth):
    response = requests.get('http://localhost:6969/api/current',cookies=cookies)
    requests.post('http://localhost:6969/api/logout')
    return (
        Titled(f"{auth}'s Personal Finance Dashboard"), 
        Main(
            H1('Dashboard')
        ),
    )

serve()