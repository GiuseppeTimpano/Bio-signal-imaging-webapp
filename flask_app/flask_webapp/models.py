from flask_webapp import db, login_manager
from flask_uploads import UploadSet
import mudicom
from flask_webapp.dicom_handler import create_thumbnail
from flask_login import UserMixin
from datetime import datetime

uploaded_dicoms = UploadSet('dicoms', extensions=('dcm'))

@login_manager.user_loader
def load_patient(patient_id):
    return Patient.query.get(int(patient_id))

class Patient(db.Model, UserMixin):
    __tablename__ = 'patient'
    id_patient = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    password_patient = db.Column(db.Integer, unique=True, nullable=True)
    email = db.Column(db.String, unique=True, nullable=True)
    first_name = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    phone_number = db.Column(db.BigInteger, nullable=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String, nullable=True)
    CF = db.Column(db.Text, nullable=True, unique=True)
    hosp = db.relationship('Hospedalization', backref='pat_hosp', lazy=True)
    mr = db.relationship('MedicalRecord', backref='pat_mr', lazy=True)
    images = db.relationship('Dicom_Image', backref='images', lazy=True)

class Admin(db.Model):
    __tablename__ = "admin"
    id_admin = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)

class Department(db.Model):
    __tablename__ = 'department'
    department_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    department_name = db.Column(db.String, unique=True, nullable=False)
    department_email = db.Column(db.String, unique=True, nullable=False)
    med_rec = db.relationship('MedicalRecord', backref='reference_mr', lazy=False)
    h_work = db.relationship('HealthcareWorker', backref='reference_hw', lazy=True)


medicalrecord_has_dicom = db.Table('medical_dicom',
                                   db.Column('id_dicom', db.Integer, db.ForeignKey('dicom.dicom_id'), primary_key=True),
                                   db.Column('medical_record_id', db.Integer, db.ForeignKey('medicalrecord.record_id', primary_key=True)))


class MedicalRecord(db.Model):
    __tablename__ = 'medicalrecord'
    record_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    terapy = db.Column(db.Text)
    dep_id = db.Column(db.Integer, db.ForeignKey('department.department_id'), nullable=True)
    pat_id = db.Column(db.Integer, db.ForeignKey('patient.id_patient'), nullable=True)
    hosp_id = db.Column(db.Integer, db.ForeignKey('hospedalization.hospedalization_id'), nullable=True)
    dicoms = db.relationship('Dicom_Image', secondary='medical_dicom', lazy='subquery', backref=db.backref('medicalrecords', lazy=True))
    
class Hospedalization(db.Model):
    __tablename__ = 'hospedalization'
    hospedalization_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    hosp_reason = db.Column(db.Text, nullable=False)
    pat_id = db.Column(db.Integer, db.ForeignKey('patient.id_patient'), nullable=True)
    med_rec = db.relationship('MedicalRecord', backref='mr_connected', lazy=True)
    
patient_group = db.Table('patient_group',
                         db.Column('patient_id', db.Integer, db.ForeignKey('patient.id_patient'), primary_key=True),
                         db.Column('doctor', db.Integer, db.ForeignKey('healthcareworker.id_worker'), primary_key=True))

class HealthcareWorker(db.Model):
    __tablename__ = 'healthcareworker'
    id_worker = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    worker_type = db.Column(db.String, nullable=False)
    medical_speciality = db.Column(db.String, nullable=True)
    nurse_grade = db.Column(db.String, nullable=True)
    dep_rif = db.Column(db.Integer, db.ForeignKey('department.department_id'), nullable=False)
    patient = db.relationship('Patient', secondary='patient_group', lazy='subquery', backref=db.backref('patients', lazy=True))

class Vol_Dicom_Image(db.Model):
    __tablename__ = '3ddicom'
    dicom_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    two_dim_dicom = db.relationship('Dicom_Image', backref='2dim_image')
    num_slice = db.Column(db.Integer, nullable=False, unique=False)


class Dicom_Image(db.Model):
    __tablename__ = 'dicom'
    dicom_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    filename = db.Column('filename', db.String(120))
    date = db.Column(db.Date, nullable=False, default=datetime.now().date())
    exame_name = db.Column(db.String, unique=False, nullable=True)
    image_dimension = db.Column(db.Integer, nullable=False)
    vol_dicom_id = db.Column(db.Integer, db.ForeignKey('3ddicom.dicom_id'), nullable=True)
    base64_data = db.Column(db.Text, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id_patient'), nullable=False)

