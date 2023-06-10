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
    registered = db.Column(db.Boolean, nullable=True)
    hosp = db.relationship('Hospedalization', backref='pat_hosp', lazy=True)
    mr = db.relationship('MedicalRecord', backref='pat_mr', lazy=True)
    images = db.relationship('Dicom_Image', backref='images', lazy=True)
    appointments = db.relationship('Appointment', backref='patient_appointment', lazy=True)

class Appointment(db.Model):
    __tablename__ = 'appointment'
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('healthcareworker.id_worker'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id_patient'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    doctor = db.relationship('HealthcareWorker', foreign_keys=[doctor_id], backref='doctor_appointments')
    patient = db.relationship('Patient', foreign_keys=[patient_id], backref='patient_appointments')


class Admin(db.Model):
    __tablename__ = "admin"
    id_admin = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, unique=False, nullable=False)

class Department(db.Model):
    __tablename__ = 'department'
    department_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    department_name = db.Column(db.String, unique=True, nullable=False)
    department_email = db.Column(db.String, unique=True, nullable=False)
    med_rec = db.relationship('MedicalRecord', backref='reference_mr', lazy=False)
    h_work = db.relationship('HealthcareWorker', backref='reference_hw', lazy=True, foreign_keys='HealthcareWorker.dep_rif')
    head_of_department_id = db.Column(db.Integer, db.ForeignKey('healthcareworker.id_worker'), nullable=True)
    head_of_department = db.relationship('HealthcareWorker', backref='department_head', uselist=False, foreign_keys=head_of_department_id)

medicalrecord_has_dicom = db.Table('medical_dicom',
                                   db.Column('id_dicom', db.Integer, db.ForeignKey('dicom.dicom_id')),
                                   db.Column('medical_record_id', db.Integer, db.ForeignKey('medicalrecord.record_id')))


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
    password = db.Column(db.String, unique=False, nullable=True)
    CF = db.Column(db.String, unique=True, nullable=False)
    role = db.Column(db.String, nullable=True)
    birth_date = db.Column(db.String, nullable=True)
    hw_role_not_doctor = db.Column(db.String, nullable=True)
    nurse_grade = db.Column(db.String, nullable=True)
    special_code = db.Column(db.Integer, nullable=True)
    dep_rif = db.Column(db.Integer, db.ForeignKey('department.department_id'), nullable=True)
    is_active = db.Column(db.Boolean, default=False)
    patient = db.relationship('Patient', secondary='patient_group', lazy='subquery', backref=db.backref('patients', lazy=True))
    department_id = db.Column(db.Integer, db.ForeignKey('department.department_id'), nullable=True)
    department = db.relationship('Department', backref='head_dep', foreign_keys=[department_id])
    appointments = db.relationship('Appointment', backref='doctor_appointment', lazy=True)

class Dicom_Image(db.Model):
    __tablename__ = 'dicom'
    dicom_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    filename = db.Column('filename', db.String(120))
    date = db.Column(db.Date, nullable=False, default=datetime.now().date())
    exame_name = db.Column(db.String, unique=False, nullable=True)
    image_dimension = db.Column(db.Integer, nullable=False)
    base64_data = db.Column(db.Text, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id_patient'), nullable=False)
    notified = db.Column(db.Boolean, default=False)
    healthcareworker_id = db.Column(db.Integer, db.ForeignKey('healthcareworker.id_worker'), nullable=True)
    healthcareworker = db.relationship('HealthcareWorker', backref='added_images', lazy=True)

