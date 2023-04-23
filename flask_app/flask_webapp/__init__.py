from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_migrate import Migrate

base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'f0d9750d6c694693beba7b033d08a66b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///project.sqlite"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app, db, compare_type=True)



from flask_webapp import routes