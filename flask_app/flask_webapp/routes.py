from flask import render_template, url_for, flash, redirect, request
from flask_webapp import app
from flask import session
from flask_webapp.forms import LoginForm, SignUpForm
from flask_webapp import db
from flask_webapp.models import Department, MedicalRecord
from flask_login import login_user, current_user, logout_user, login_required
from flask_webapp import bcrypt
from flask_webapp.models import Patient
import random

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

@app.route("/dashboard/dicom_image")
def visualize_image():
    return render_template("doctor_templates/image_visualizer.html", page="visualize_image")

@app.route("/dashboard/dicom_analyzer")
def image_analyzer():
    return render_template("doctor_templates/image_analyzer.html", page="analyzer")

@app.route("/dashboard/biosignals_visualizer")
def biosignals_visualizer():
    return render_template("doctor_templates/biosignals_visualizer.html", page="visualize_biosignals")

@app.route("/dashboard/biosignals_analyzer")
def biosignals_analyzer():
    return render_template("doctor_templates/biosignals_analyzer.html", page="analyze_biosignals")



