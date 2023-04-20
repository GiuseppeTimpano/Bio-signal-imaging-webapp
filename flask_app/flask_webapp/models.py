from flask_webapp import db
from flask_webapp import Column

class Bioimage(db.Model):
    __tablename__ = 'bioimage'
    idBioimages= db.Column(db.Integer, primary_key=True)
    Name_exame = db.Column(db.String(45), unique=True)
    Type = db.Column(db.String(45), nullable=False)

    def _repr_(self):
        return f"Bioimage('{ self.idBioimages}', '{ self.Name_exame}', '{ self.Type }')"
    