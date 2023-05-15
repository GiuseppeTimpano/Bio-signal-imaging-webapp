from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, template_folder="templates")
app.config['SECRET_KEY'] = 'f0d9750d6c694693beba7b033d08a66b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(base_dir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['MESSAGE_FLASHING_OPTIONS'] = {'duration': 5}
path_to_save = 'flask_app/uploads'
app.config['UPLOAD_FOLDER'] = path_to_save
app.static_url_path = 'Papaya/release/current/standard'
db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from flask_webapp import routes, models