from flask import render_template, url_for, flash, redirect, request, jsonify
from flask_webapp import app
from flask import session
from flask_webapp.forms import LoginForm, SignUpForm
from flask_webapp import db
from flask_webapp.models import Department, MedicalRecord
from flask_login import login_user, current_user, logout_user, login_required
from flask_webapp import bcrypt
from flask_webapp.models import Patient, Dicom_Image
from werkzeug.utils import secure_filename
import os
import random
from datetime import datetime
import skimage.transform as sktransform
import pydicom
import io

@app.route("/")
@app.route("/index")
def home():
    return render_template('init_page/index.html', title='Start page')

@app.route("/login.html", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            session['name'] = "doctor"
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
            #return redirect(url_for('login'))
    return render_template('init_page/login.html', title='Login', form=form, name=session.get('name'))

@app.route("/signup.html", methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        heashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        patient = Patient(id_patient=random.randint(1000, 1057895), password_patient=heashed_password, email=form.email.data, 
                          first_name=form.first_name.data, surname=form.surname.data,
                          CF=form.CF.data, city=form.city.data)
        if Patient.query.filter_by(CF=patient.CF).first():
            flash("Already exits patient with this CF. Please, login!")
        else:
            db.session.add(patient)
            db.session.commit()
            flash('You have been signup!', 'success')
            return redirect(url_for('login'))
    return render_template('init_page/signup.html', title='Sign_up', form=form)


@app.route("/sign_out")
def logout():
    session.pop('name')
    return redirect(url_for('home'))

@app.route("/dashboard")
def dicom_visualizer():
    return render_template('doctor_templates/dash_home.html', page="visualizer")

@app.route("/dashboard/patient")
def doctor_patient():
    return render_template("doctor_templates/doctor_patients.html", page='patient')

@app.route("/dashboard/dicom_image", methods=['GET', 'POST'])
def visualize_image():
    if request.method=='POST':
        #Patient data from html form
        patient_CF = request.form['CF']
        patient_name = request.form['name']
        patient_surname = request.form['surname']
        image_type = request.form['type']
        patient = Patient.query.filter_by(CF=patient_CF).first()
        if patient is None:
            flash('No patient in database')
        else:
            patient_id = patient.id_patient
            #Execute query
            images = Dicom_Image.query.filter_by(patient_id=patient_id).all()
            return render_template("doctor_templates/image_visualizer.html", page="visualize_image", images=images, patient=patient)
    return render_template("doctor_templates/image_visualizer.html", page="visualize_image")

@app.route("/dashboard/selected_image", methods=['GET', 'POST'])
def view_selected_image():
    if request.method == 'POST':
        image_selected = request.form['images']
    if (image_selected is None):
        flash('No image in selected')
    else:
        image_selected = image_selected.encode('latin-1')
        print(type(image_selected))
        #image_selected = io.BytesIO(image_selected)
        #image_selected_dcm = pydicom.dcmread(image_selected, force=True)
        return render_template('doctor_templates/view_image.html', image_data = "../../static/CT.1.2.246.352.71.3.164087780.2233476.20130213140517.dcm")

@app.route("/dashboard/dicom_analyzer")
def image_analyzer():
    return render_template("doctor_templates/image_analyzer.html", page="analyzer")

@app.route("/dashboard/add_image", methods=['GET', 'POST'])
def add_image():
    if request.method=='POST':
        name = request.form['name']
        file = request.files['file']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        patient_id = int(request.form['patient'])

        if not all([name, file, date, patient_id]):
            flash('All fields are required.')
            return redirect(url_for('add_image'))
        
        data = file.read()
        dicom = Dicom_Image(dicom_id=random.randint(1000, 1876364), filename=name,
                            patient_id=patient_id, date=date, 
                            data_blob=data)
        db.session.add(dicom)
        db.session.commit()
        flash('Image added successfully.')
    patients = Patient.query.all()
    return render_template('doctor_templates/add_image.html', patients=patients, page='add')


@app.route("/dashboard/biosignals_visualizer")
def biosignals_visualizer():
    return render_template("doctor_templates/biosignals_visualizer.html", page="visualize_biosignals")

@app.route("/dashboard/biosignals_analyzer")
def biosignals_analyzer():
    return render_template("doctor_templates/biosignals_analyzer.html", page="analyze_biosignals")



