from flask import render_template, url_for, flash, redirect, request, jsonify
from flask_webapp import app
from flask import session
from flask_webapp.forms import LoginForm, SignUpForm, DepartmentForm
from flask_webapp import db
from flask_webapp.models import Department, MedicalRecord, HealthcareWorker, Admin, Appointment, patient_group
from flask_login import login_user, current_user, logout_user, login_required
from flask_webapp import bcrypt
from flask_webapp.models import Patient, Dicom_Image
from werkzeug.utils import secure_filename
from sqlalchemy import and_
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
                session['ID'] = patient.id_patient
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
            print(role.is_active)
            if role.is_active:
                if bcrypt.check_password_hash(role.password, password):
                    flash('You have been logged in!', 'success')
                    session['name'] = role.role
                    session['utent'] = healthcare_worker.name
                    session['ID'] = healthcare_worker.id_worker
                    return redirect(url_for('home'))
                else:
                    flash('Not corret credential! Plaese, try again', 'danger')
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
            #if patient already exitst in db
            if patient and patient.CF==form.CF.data and patient.registered==False:
                patient.password_patient=heashed_password
                patient.email=form.email.data
                patient.city = form.city.data
                patient.registered=True
                db.session.commit()
                flash('You have been sign-up!')
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
                                      role='healthcareworker',
                                      birth_date=form.birth_date.data)
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
                        CF=CF, 
                        registered=False)
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
    #patients = Patient.query.all()
    patients = Patient.query.join(patient_group, Patient.id_patient == patient_group.c.patient_id).filter(patient_group.c.doctor == session.get('ID')).all()

    #appointments = Appointment.query.filter_by(date=date.today()).all()
    appointments = Appointment.query.filter(and_(Appointment.patient_id.in_([patient.id_patient for patient in patients]), Appointment.date == date.today())).all()
    all_appointment =  Appointment.query.filter(Appointment.patient_id.in_([patient.id_patient for patient in patients])).all()

    images = Dicom_Image.query.filter(
    Dicom_Image.patient_id.in_([patient.id_patient for patient in patients]),
    Dicom_Image.notified == False
    ).all()

    busy_schedule = {}
    for appointment in appointments:
        appointment_date = appointment.date
        appointment_time = appointment.time
        if appointment_date not in busy_schedule:
            busy_schedule[appointment_date] = []
        busy_schedule[appointment_date].append(appointment_time)
    
    current_date = datetime.now().strftime('%Y-%m-%d')

    page=None
    if session.get('name')=='doctor':
        page='dash_home.html'
    else:
        page='add_image.html'

    return render_template('doctor_templates/' + str(page), page="visualizer", patients=patients, appointments=appointments, busy_schedule=busy_schedule, current_date=current_date, 
                           all_appointment=all_appointment, images = images)

@app.route("/dashboard/patient")
def doctor_patient():
    doctor = session.get('name')
    patients = Patient.query.join(patient_group, Patient.id_patient == patient_group.c.patient_id).filter(patient_group.c.doctor == session.get('ID')).all()
    return render_template("doctor_templates/doctor_patients.html", page='patient', patients=patients)

@app.route("/dashboard/dicom_image", methods=['GET', 'POST'])
def visualize_image():
    if session.get('name')=='doctor':
        patients = Patient.query.join(patient_group, Patient.id_patient == patient_group.c.patient_id).filter(patient_group.c.doctor == session.get('ID')).all()
        patients_value = db.session.query(Patient).join(patient_group, Patient.id_patient == patient_group.c.patient_id).filter(patient_group.c.doctor == session.get('ID')).values(Patient)
        if request.method=='POST' and (not request.form.get('MedicalRecordID') and not request.form.get('ImageID')
                                        and not request.form.get('cf_id')):
            #Patient data from html form
            patient_CF = request.form['CF']
            patient_name = request.form['name']
            patient_surname = request.form['surname']
            image_type = request.form['type']
            patient = Patient.query.filter_by(CF=patient_CF).first()
            print(type(patients))
            if patient is None or patient.id_patient not in [p.id_patient for p in patients_value]:
                flash('No patient in database or patient followed by this account!', 'danger')
            else:
                patient_id = patient.id_patient
                images = Dicom_Image.query.filter_by(patient_id=patient_id).all()
                return render_template("doctor_templates/image_visualizer.html", page="visualize_image", images=images, patient=patient)
        elif request.method=='POST' and (not request.form.get('CF') and not request.form.get('name')
                                        and not request.form.get('surname') and not request.form.get('type')):
            medicalID = request.form['MedicalRecordID']
            imageID = request.form['ImageID']
            patient_CF = request.form['cf_id']
            patient = Patient.query.filter_by(CF=patient_CF).first()
            print(patient)
            if not imageID and medicalID and patient is not None:
                images = MedicalRecord.query.filter_by(record_id=medicalID).first().dicoms if medicalID else []
            elif imageID and patient is not None:
                images = Dicom_Image.query.filter_by(dicom_id=imageID).all() if imageID else []
            if patient is None:
                flash("Insert correct CF for patient!", "error")
                print("flash")
            else:
                return render_template("doctor_templates/image_visualizer.html", page="visualize_image", images=images, patient=patient)
    elif session.get('name')=='healthcareworker':
        if request.method=='POST':
            patient_CF = request.form['CF']
            patient = Patient.query.filter_by(CF=patient_CF).first()
            images = Dicom_Image.query.filter_by(patient_id=patient.id_patient).all()
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
        dicom.notified=True
        dicom_id = dicom.dicom_id
        return render_template('doctor_templates/view_image.html', image_data = image_selected, patient=patient, dicom_id=dicom_id, page='page_visualizer')

@app.route("/dashboard/selected_image/<int:dicom>/<int:patient>", methods=['POST'])
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

@app.route("/dashboard/add_image/", methods=['GET', 'POST'])
def add_image():
    if request.method=='POST':
        name = request.form['name']
        files = request.files.getlist('file')
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        patient_id = int(request.form['patient'])

        if not all([name, files, date, patient_id]):
            flash('All fields are required.')
            return redirect(url_for('add_image'))
        
        hw = HealthcareWorker.query.filter_by(id_worker=session.get('ID')).first()
        
        for file in files:
            data = file.read()
            filename = secure_filename(file.filename)
            base64_data = base64.b64encode(data).decode('utf-8')
            dicom = Dicom_Image(dicom_id=random.randint(1000, 1876364), filename=file.filename,
                                patient_id=patient_id, date=date, 
                                base64_data=base64_data, image_dimension=2, 
                                healthcareworker=hw,
                                exame_name=name)
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
    db.session.commit()
    flash('Account activated successfully!')
    return redirect(url_for('list_doctors'))

@app.route("/admin/active_account/<int:worker_id>")
def activate_account_hw(worker_id):
    hw = HealthcareWorker.query.filter_by(id_worker=worker_id).first()
    hw.is_active=True
    db.session.commit()
    flash('Account activated successfully!')
    return redirect(url_for('list_workers'))

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

@app.route("/confirm-role/<int:worker_id>", methods=['POST'])
def confirm_role(worker_id):
    worker = HealthcareWorker.query.get(worker_id)
    role = request.form.get('role')
    worker.hw_role_not_doctor = role
    db.session.commit()
    flash('Role confirmed successfully')
    return redirect(url_for('admin_page'))

@app.route("/healthcareworker/images_patients")
def all_images():
    return render_template('doctor_templates/all_images.html', page='visualize_all_images')

@app.route("/patient/home_page")
def patient_page():
    patient = Patient.query.filter_by(id_patient=session.get('ID')).first()
    print(session.get('ID'))
    return render_template("patient_template/list_appointment.html", page='appointment', patient=patient)

@app.route("/patient/list_test")
def list_test():
    return render_template("patient_template/list_test.html", page='list')