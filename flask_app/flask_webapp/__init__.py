from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import mysql.connector
import os

base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'f0d9750d6c694693beba7b033d08a66b'

app.config['SQLALCHEMY_DATABASE_URI'] =\
    "sqlite:///" + os.path.join(base_dir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)

from flask_webapp import routes

