from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, DeclarativeBase

app = Flask(__name__)
app.config['SECRET_KEY'] = 'f0d9750d6c694693beba7b033d08a66b'

from flask_webapp import models
from flask_webapp import prova
from flask_webapp import routes


