# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    #SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///finance.db'
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///finance.db'
    #SQLALCHEMY_TRACK_MODIFICATIONS = False
    #REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    #PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
    #PLAID_SECRET = os.environ.get('PLAID_SECRET')
    #PLAID_ENV = os.environ.get('PLAID_ENV', 'sandbox') # 'sandbox' or 'development' or 'production'