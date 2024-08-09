# config.py
import os 

class Config:
    #SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey'
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///finance.db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///finance.db'
    #SQLALCHEMY_TRACK_MODIFICATIONS = False
    #REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'