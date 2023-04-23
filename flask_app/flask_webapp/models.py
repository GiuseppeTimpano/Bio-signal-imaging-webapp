from flask_webapp import db

class Patient(db.Model):
    __tablename__ = 'patient'
    id_patient = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    phone_number = db.Column(db.BigInteger)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String, nullable=False)
    CF = db.Column(db.Text, nullable=False)

class Department(db.Model):
    __tablename__ = 'department'
    department_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    department_name = db.Column(db.String, unique=True, nullable=False)
    department_email = db.Column(db.String, unique=True, nullable=False)

class MedicalRecord(db.Model):
    __tablename__ = 'medicalrecord'
    record_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    terapy = db.Column(db.Text)

class Hospedalization(db.Model):
    __tablename__ = 'hospedalization'
    hospedalization_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    hosp_reason = db.Column(db.Text, nullable=False)
class HealthcareWorker(db.Model):
    __tablename__ = 'healthcareworker'
    id_worker = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    worker_type = db.Column(db.String, nullable=False)
    medical_speciality = db.Column(db.String, nullable=True)
    nurse_grade = db.Column(db.String, nullable=True)
class Bioimage(db.Model):
    __tablename__ = 'bioimage'
    id_bioimage = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    exame_type = db.Column(db.String, unique=False, nullable=False)
    exame_name = db.Column(db.String, unique=False, nullable=False)
    def _repr_(self):
        return f"Bioimage('{ self.id_bioimage}', '{ self.exame_type}')"

class Biosignal(db.Model):
    __tablename__ = 'biosignal'
    id_Biosignal = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    test_name = db.Column(db.String, nullable=False)
    exame_type = db.Column(db.String, nullable=False)
