from flask_webapp import db
from flask_uploads import UploadSet
import mudicom
from dicom_handler import create_thumbnail

uploaded_dicoms = UploadSet('dicoms', extensions=('dcm'))

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

class Dicom(db.Model):
    __tablename__ = 'dicom'
    dicom_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    _filename = db.Column('filename', db.String(120))
    exame_type = db.Column(db.String, unique=False, nullable=False)
    exame_name = db.Column(db.String, unique=False, nullable=False)
    data_elements = db.relationship('DicomDataElement', backref='dicom',
                                    lazy='dynamic')

    def __init__(self, filename):
        self._filename = filename
        self.data_elements = self._generate_data_elements(filename)

        fp = uploaded_dicoms.path(self.filename)
        thumbnail_fp = fp.replace('.dcm', '.thumb.jpeg')
        create_thumbnail(str(fp), str(thumbnail_fp))

    @property
    def thumbnail_filename(self):
        return self._filename.replace(".dcm", ".thumb.jpeg")

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename):
        self._filename = filename

    @property
    def filename_url(self):
        return uploaded_dicoms.url(self.filename)

    @property
    def thumbnail_url(self):
        return uploaded_dicoms.url(self.thumbnail_filename)
    
    def _generate_data_elements(self, filename):
        mu = mudicom.load(uploaded_dicoms.path(filename))
        return [DicomDataElement(e) for e in mu.find()]
    
    def _repr_(self):
        return f"Bioimage('{ self.id_bioimage}', '{ self.exame_type}')"
    

class DicomDataElement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    value = db.Column(db.Text())
    dicom_id = db.Column(db.Integer, db.ForeignKey('dicom.dicom_id'))

    def __init__(self, data_element):
        self.name = data_element.name
        self.value = data_element.value

class Biosignal(db.Model):
    __tablename__ = 'biosignal'
    id_Biosignal = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    test_name = db.Column(db.String, nullable=False)
    exame_type = db.Column(db.String, nullable=False)
