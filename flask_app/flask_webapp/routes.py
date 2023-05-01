from flask import render_template, url_for, flash, redirect, request
from flask_webapp import app
from flask import session
from flask_webapp.forms import LoginForm, SignUpForm
from flask_webapp import db
from flask_webapp.models import Department, MedicalRecord

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
        if form.first_name.data == 'Giuseppe' and form.surname.data == 'Timpano':
            flash('You have been signup!', 'success')
    return render_template('signup.html', title='Sign_up', form=form)

@app.route("/sign_out")
def logout():
    session.pop('name')
    return redirect(url_for('home'))

@app.route("/dicom_visualizer")
def dicom_visualizer():
    return render_template('dicom_templates/layout_dicom.html')

@app.route("/doctor/patient")
def doctor_patient():
    return render_template("dicom_templates/doctor_patients.html", page='patient')

