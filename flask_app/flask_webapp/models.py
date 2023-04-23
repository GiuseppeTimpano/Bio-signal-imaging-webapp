from flask_webapp import db

class Bioimage(db.Model):
    __tablename__ = 'bioimage'
    identify = db.Column(db.Integer, primary_key=True)
    patient = db.Column(db.String, unique=True, nullable=False)
    
    def _repr_(self):
        return f"Bioimage('{ self.identify}', '{ self.patient}')"
