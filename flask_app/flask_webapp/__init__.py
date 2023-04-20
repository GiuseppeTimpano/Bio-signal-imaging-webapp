from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'f0d9750d6c694693beba7b033d08a66b'

from flask_webapp import routes

