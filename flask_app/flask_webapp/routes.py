from flask import render_template, url_for, flash, redirect, request, jsonify
from flask_webapp import app
from flask import session
from flask_webapp.forms import LoginForm, SignUpForm, DepartmentForm
from flask_webapp import db
from flask_webapp.models import Department, MedicalRecord, HealthcareWorker, Admin, Appointment
from flask_login import login_user, current_user, logout_user, login_required
from flask_webapp import bcrypt
from flask_webapp.models import Patient, Dicom_Image
from werkzeug.utils import secure_filename
import os
import random
from datetime import datetime, date
import base64

@app.route("/")
@app.route("/index")
def home():
    heashed_password = bcrypt.generate_password_hash(str('admin')).decode('utf-8')
    admin=Admin(id_admin=12345, email='admin@admin.it', password=heashed_password)
    if Admin.query.filter_by(id_admin=admin.id_admin).first() is None:
        db.session.add(admin)
        db.session.commit()
    return render_template('init_page/index.html', title='Start page')

@app.route("/login.html", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    ref = None
    if form.validate_on_submit():
        username = form.email.data
        password = form.password.data
        patient = Patient.query.filter_by(email = username).first()
        healthcare_worker = HealthcareWorker.query.filter_by(email = username).first()
        admin = Admin.query.filter_by(email = username).first()
        role = None
        if patient and (healthcare_worker and admin) is None:
            role = patient
            if bcrypt.check_password_hash(role.password_patient, password):
                flash('You have been logged in!', 'success')
                session['name'] = "patient"
                session['utent'] = patient.first_name
                return redirect(url_for('home'))
            print(form.password.data)
        elif admin and (patient and healthcare_worker) is None:
            role = admin
            if bcrypt.check_password_hash(role.password, password):
                flash('You have been logged in!', 'success')
                session['name'] = "admin"
                session['utent'] = admin.id_admin
                return redirect(url_for('home'))
        elif healthcare_worker and (patient and admin) is None:
            role=healthcare_worker
            if role.role=='doctor' and role.is_active and bcrypt.check_password_hash(role.password, password):
                flash('You have been logged in!', 'success')
                session['name'] = role.role
                session['utent'] = healthcare_worker.name
                session['ID'] = healthcare_worker.id_worker
                return redirect(url_for('home'))
            else:
                flash('Your account must be activate by admin!', 'danger')
        else:
            flash('Login Unsuccessful. Please check username and password!', 'danger')
    return render_template('init_page/login.html', title='Login', form=form, name=session.get('name'), utent=session.get('utent'))

@app.route("/signup.html", methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        utent = request.form['select_utent']
        heashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        if utent == '1':
            patient = Patient.query.filter_by(CF=form.CF.data).first()
            print(patient.birth_date)
            if patient and patient.CF==form.CF.data and patient.registered==False:
                #patient = Patient(id_patient=random.randint(1000, 1057895), password_patient=heashed_password, email=form.email.data, 
                                #first_name=form.first_name.data, surname=form.surname.data,
                                #CF=form.CF.data, city=form.city.data,
                                #birth_date=form.birth_date.data)
                patient.password_patient=heashed_password
                patient.email=form.email.data
                patient.registered=True
                db.session.commit()
            else: 
                flash("You are not in db system or you're already sign-up! Please Login")
                return redirect(url_for('login'))
        elif utent == '2':
            doctor = HealthcareWorker(id_worker=random.randint(1000, 1637640), password = heashed_password,
                                      name = form.first_name.data, 
                                      surname = form.surname.data,
                                      CF = form.CF.data, 
                                      email = form.email.data,
                                      role='doctor',
                                      birth_date=form.birth_date.data)
            if HealthcareWorker.query.filter_by(id_worker=doctor.id_worker).first():
                flash("Account already exists!", "error")
            else:
                db.session.add(doctor)
                db.session.commit()
                flash('You have been signup as doctor!', 'success')
                return redirect(url_for('login'))
        elif utent=='3':
            healthcareworkwer = HealthcareWorker(id_worker=random.randint(1000, 1637640),
                                      password = heashed_password,
                                      name = form.first_name.data, 
                                      surname = form.surname.data,
                                      email = form.email.data,
                                      CF = form.CF.data, 
                                      role='healthcareworker')
            if HealthcareWorker.query.filter_by(id_worker=healthcareworkwer.id_worker).first():
                flash("Account already exists!", "error")
            else:
                db.session.add(healthcareworkwer)
                db.session.commit()
                flash('You have been signup as healthcare worker!', 'success')
                return redirect(url_for('login'))
    return render_template('init_page/signup.html', title='Sign_up', form=form)

@app.route("/dashboard/add_patient", methods=['POST'])
def add_patient():
    if request.method=='POST':
        name = request.form['patient_name']
        surname = request.form['patient_surname']
        CF = request.form['cf']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        print(session.get('ID'))
        patient = Patient(id_patient=random.randint(1000, 376436543), 
                        first_name=name, surname=surname,
                        birth_date=date,
                        CF=CF)
        doctor = HealthcareWorker.query.filter_by(id_worker=session.get('ID')).first()
        db.session.add(patient)
        doctor.patient.append(patient)
        db.session.commit()
        flash('Patient added successfully', 'success')
        return redirect(url_for('dicom_visualizer'))

@app.route("/sign_out")
def logout():
    session.pop('name')
    return redirect(url_for('home'))

@app.route("/dashboard")
def dicom_visualizer():
    patients = Patient.query.all()

    appointments = Appointment.query.filter_by(date=date.today()).all()
    all_appointment = Appointment.query.all()

    busy_schedule = {}
    for appointment in appointments:
        appointment_date = appointment.date
        appointment_time = appointment.time
        if appointment_date not in busy_schedule:
            busy_schedule[appointment_date] = []
        busy_schedule[appointment_date].append(appointment_time)
    
    current_date = datetime.now().strftime('%Y-%m-%d')

    return render_template('doctor_templates/dash_home.html', page="visualizer", patients=patients, appointments=appointments, busy_schedule=busy_schedule, current_date=current_date, 
                           all_appointment=all_appointment)

@app.route("/dashboard/patient")
def doctor_patient():
    doctor = session.get('name')
    patients = Patient.query.all()
    return render_template("doctor_templates/doctor_patients.html", page='patient', patients=patients)

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

@app.route("/dashboard/selected_image/<patient>", methods=['GET', 'POST'])
def view_selected_image(patient):
    if request.method == 'POST':
        image_selected = request.form['images']
    if (image_selected is None):
        flash('No image in selected')
    else:
        dicom = Dicom_Image.query.filter_by(base64_data=image_selected).first()
        dicom_id = dicom.dicom_id
        return render_template('doctor_templates/view_image.html', image_data = image_selected, patient=patient, dicom_id=dicom_id)

@app.route("/dashboard/selected_image/<int:dicom>/<int:patient>")
def redirect_view_selected_image(dicom, patient):
    dicom = Dicom_Image.query.filter_by(dicom_id=dicom).first()
    return render_template('doctor_templates/view_image.html', image_data = dicom.base64_data, patient=patient, dicom_id=dicom.dicom_id)

@app.route("/dashboard/dicom_analyzer")
def image_analyzer():
    return render_template("doctor_templates/image_analyzer.html", page="analyzer")

@app.route("/dashboard/add_annotation/<int:patient>/<int:dicom>",  methods=['GET', 'POST'])
def add_medical_record(patient, dicom):
    if request.method=='POST':
        medical_record = MedicalRecord(record_id=random.randint(1000, 5382264),
                                    terapy=request.form["userInput"], 
                                    pat_id=patient)
        db.session.add(medical_record)
        dicom = Dicom_Image.query.filter_by(dicom_id=dicom).first()
        medical_record.dicoms.append(dicom)
        db.session.commit()
        flash('Annotazione inserita con successo!', 'success')
        return redirect(url_for('dicom_visualizer'))

@app.route("/dashboard/add_image", methods=['GET', 'POST'])
def add_image():
    if request.method=='POST':
        name = request.form['name']
        files = request.files.getlist('file')
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        patient_id = int(request.form['patient'])

        if not all([name, files, date, patient_id]):
            flash('All fields are required.')
            return redirect(url_for('add_image'))
        
        for file in files:
            data = file.read()
            filename = secure_filename(file.filename)
            base64_data = base64.b64encode(data).decode('utf-8')
            dicom = Dicom_Image(dicom_id=random.randint(1000, 1876364), filename=file.filename,
                                patient_id=patient_id, date=date, 
                                base64_data=base64_data, image_dimension=2)
            db.session.add(dicom)
            db.session.commit()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Images added successfully.')
    patients = Patient.query.all()
    return render_template('doctor_templates/add_image.html', patients=patients, page='add')

@app.route("/dashboard/biosignals_visualizer")
def biosignals_visualizer():
    return render_template("doctor_templates/biosignals_visualizer.html", page="visualize_biosignals")

@app.route("/dashboard/biosignals_analyzer")
def biosignals_analyzer():
    return render_template("doctor_templates/biosignals_analyzer.html", page="analyze_biosignals")

@app.route("/admin/")
def admin_page():
    return render_template("admin_template/layout_admin.html", page=None)

@app.route("/admin/list_patients")
def list_patients():
    patients = Patient.query.all()
    return render_template("admin_template/list_patients.html", page="patient", patients=patients)

@app.route("/admin/list_doctors")
def list_doctors():
    doctors = HealthcareWorker.query.filter_by(role='doctor').all()
    departments = Department.query.all()
    return render_template("admin_template/list_doctors.html", page="doctor", doctors=doctors, departments=departments)

@app.route("/admin/list_healthcareworker")
def list_workers():
    worker = HealthcareWorker.query.filter_by(role='healthcareworker').all()
    return render_template("admin_template/list_worker.html", page="worker", workers=worker)

@app.route("/admin/active_account/<int:doctor_id>")
def activate_account(doctor_id):
    doctor = HealthcareWorker.query.filter_by(id_worker=doctor_id).first()
    doctor.is_active=True
    return redirect(url_for('list_doctors'))

@app.route("/admin/assign_doctor_to_dep/<int:doctor_id>", methods=['POST'])
def assign_doctor_department(doctor_id):
    department_id = request.form.get('department')
    doctor = HealthcareWorker.query.get(doctor_id)
    if doctor:
        doctor.dep_rif = department_id
        db.session.commit()
    return redirect(url_for('list_doctors'))

@app.route("/admin/manage_department", methods=['POST', 'GET'])
def manage_department():
    form = DepartmentForm()
    form.head_of_department.choices = [(doctor.id_worker, doctor.name) for doctor in HealthcareWorker.query.filter_by(role='doctor')]
    if form.validate_on_submit():
        department = Department(department_id=random.randint(1000, 4826484), department_name=form.name.data, department_email = form.email.data)
        head_of_department_id = form.head_of_department.data
        head_of_department = HealthcareWorker.query.get(head_of_department_id)
        department.head_of_department = head_of_department
        db.session.add(department)
        db.session.commit()
        return redirect(url_for('manage_department'))
    departments = Department.query.all()
    return render_template('admin_template/manage_department.html', page='department', departments=departments, form=form)

@app.route("/doctor/remove_followed_patient", methods=['POST', 'GET'])
def remove_patient():
    doctor_id = session.get('ID')
    patient_id = request.form.get('patient_select')
    doctor = HealthcareWorker.query.filter_by(id_worker=doctor_id).first()
    patient = Patient.query.filter_by(id_patient=patient_id).first()
    doctor.patient.remove(patient)
    db.session.commit()
    return redirect(url_for('dicom_visualizer'))

@app.route("/take_appointment", methods=['POST'])
def take_appointment():
    doctor_id = session.get('ID')
    patient_id = request.form.get('patient_select')
    appointment_date = request.form.get('appointment_date')
    appointment_time = request.form.get('appointment_time')
    appointment_reason = request.form.get('appointment_reason')
    doctor = HealthcareWorker.query.get(doctor_id)
    patient = Patient.query.get(patient_id)

    if doctor and patient:
        date_obj = datetime.strptime(appointment_date, '%Y-%m-%d').date()
        time_obj = datetime.strptime(appointment_time, '%H:%M').time()

        appointment = Appointment(doctor=doctor, patient=patient, date=date_obj, time=time_obj, reason=appointment_reason)
        db.session.add(appointment)
        db.session.commit()
        flash('Appointment taken successfully.', 'success')
    else:
        flash('Failed to take appointment.', 'error')

    return redirect(url_for('dicom_visualizer'))


@app.route('/delete_appointment/', methods=['POST'])
def delete_appointment():
    appointment_id = request.form.get('appointment_id')
    appointment = Appointment.query.get(appointment_id)

    if appointment:
        # Elimina l'appuntamento dal database
        db.session.delete(appointment)
        db.session.commit()

        flash('L\'appuntamento è stato eliminato con successo.', 'success')
    else:
        flash('Impossibile trovare l\'appuntamento specificato.', 'error')

    return redirect(url_for('dicom_visualizer'))

    