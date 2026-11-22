import os
import io
import json
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, PatientProfile, DoctorProfile, EyeTestRecord, SymptomLog, Prescription, Appointment, AssignedTest
from seed_data import seed_database
from report_generator import generate_patient_report_pdf

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ocucare-secure-key-2026-ophthalmology')

# Database configuration: support Vercel /tmp directory, PostgreSQL, or local SQLite
if os.environ.get('VERCEL'):
    default_db = f"sqlite:///{os.path.join('/tmp', 'ocucare.db')}"
else:
    default_db = f"sqlite:///{os.path.join(BASE_DIR, 'ocucare.db')}"

db_url = os.environ.get('DATABASE_URL', default_db)
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database
with app.app_context():
    db.create_all()
    seed_database(app)

# ----------------- Navigation Context Processor -----------------
@app.context_processor
def inject_globals():
    return {
        'now': datetime.datetime.utcnow(),
        'all_doctors': DoctorProfile.query.all() if current_user.is_authenticated else [],
        'EyeTestRecord': EyeTestRecord,
        'Appointment': Appointment,
        'Prescription': Prescription,
        'SymptomLog': SymptomLog
    }

# ----------------- Public & Auth Routes -----------------
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        else:
            return redirect(url_for('patient_dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.full_name}!', 'success')
            if user.role == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            return redirect(url_for('patient_dashboard'))
        else:
            flash('Invalid username or password. Please try again or use a demo account.', 'error')
            
    return render_template('login.html')

@app.route('/switch-user/<username>')
def switch_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        login_user(user)
        flash(f'Switched session to {user.full_name} ({user.role.capitalize()})', 'info')
        if user.role == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        return redirect(url_for('patient_dashboard'))
    flash('User account not found', 'error')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        role = request.form.get('role', 'patient')
        phone = request.form.get('phone', '')

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or email already registered.', 'error')
            return render_template('register.html')

        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            role=role,
            phone=phone
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()

        if role == 'patient':
            pat_profile = PatientProfile(
                user_id=new_user.id,
                date_of_birth=request.form.get('date_of_birth', '1995-01-01'),
                gender=request.form.get('gender', 'Not Specified'),
                wear_glasses='wear_glasses' in request.form,
                wear_contacts='wear_contacts' in request.form,
                medical_history=request.form.get('medical_history', '')
            )
            db.session.add(pat_profile)
        else:
            doc_profile = DoctorProfile(
                user_id=new_user.id,
                title=request.form.get('title', 'MD, Ophthalmologist'),
                specialty=request.form.get('specialty', 'Comprehensive Eye Care'),
                clinic_name=request.form.get('clinic_name', 'OptiVision Clinic'),
                clinic_address=request.form.get('clinic_address', 'Medical District'),
                consultation_fee=float(request.form.get('consultation_fee', 80.0)),
                bio=request.form.get('bio', '')
            )
            db.session.add(doc_profile)

        db.session.commit()
        login_user(new_user)
        flash('Account registered successfully! Welcome to OptiVision.', 'success')
        return redirect(url_for('doctor_dashboard' if role == 'doctor' else 'patient_dashboard'))

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('index'))

# ----------------- Patient Routes -----------------
@app.route('/patient/dashboard')
@login_required
def patient_dashboard():
    if current_user.role != 'patient':
        return redirect(url_for('doctor_dashboard'))
        
    profile = current_user.patient_profile
    recent_tests = profile.test_records.order_by(EyeTestRecord.date_conducted.desc()).limit(5).all()
    active_rx = profile.prescriptions.filter_by(status='active').order_by(Prescription.created_at.desc()).first()
    pending_tasks = profile.assigned_tests.filter_by(status='pending').all()
    upcoming_apts = profile.appointments.filter(Appointment.status == 'scheduled', Appointment.scheduled_time >= datetime.datetime.utcnow()).order_by(Appointment.scheduled_time.asc()).all()
    recent_symptoms = profile.symptom_logs.order_by(SymptomLog.timestamp.desc()).limit(7).all()
    
    # Calculate a composite "Eye Health Index" (0 - 100)
    health_index = 88
    if recent_symptoms:
        avg_strain = sum(s.eye_strain for s in recent_symptoms) / len(recent_symptoms)
        health_index = max(40, int(100 - (avg_strain * 6)))

    return render_template(
        'patient/dashboard.html',
        profile=profile,
        recent_tests=recent_tests,
        active_rx=active_rx,
        pending_tasks=pending_tasks,
        upcoming_apts=upcoming_apts,
        recent_symptoms=recent_symptoms,
        health_index=health_index
    )

@app.route('/patient/tests')
@login_required
def patient_tests_hub():
    if current_user.role != 'patient':
        return redirect(url_for('doctor_dashboard'))
    pending_tasks = current_user.patient_profile.assigned_tests.filter_by(status='pending').all()
    return render_template('patient/tests_hub.html', pending_tasks=pending_tasks)

@app.route('/patient/test/<test_name>')
@login_required
def patient_take_test(test_name):
    if current_user.role != 'patient':
        return redirect(url_for('doctor_dashboard'))
        
    valid_tests = {
        'acuity': 'patient/test_acuity.html',
        'color': 'patient/test_color.html',
        'astigmatism': 'patient/test_astigmatism.html',
        'contrast': 'patient/test_contrast.html',
        'amsler': 'patient/test_amsler.html',
        'dryeye': 'patient/test_dryeye.html'
    }
    
    if test_name not in valid_tests:
        flash('Invalid eye test requested.', 'error')
        return redirect(url_for('patient_tests_hub'))
        
    return render_template(valid_tests[test_name], test_name=test_name, patient=current_user.patient_profile)

@app.route('/patient/test-result/<int:record_id>')
@login_required
def patient_test_result(record_id):
    record = EyeTestRecord.query.get_or_404(record_id)
    # Ensure patient or doctor access
    if current_user.role == 'patient' and record.patient_id != current_user.patient_profile.id:
        abort(403)
        
    return render_template('patient/test_report.html', record=record)

@app.route('/patient/monitor')
@login_required
def patient_monitor():
    if current_user.role != 'patient':
        return redirect(url_for('doctor_dashboard'))
        
    profile = current_user.patient_profile
    symptoms = profile.symptom_logs.order_by(SymptomLog.timestamp.asc()).all()
    acuity_tests = profile.test_records.filter_by(test_type='visual_acuity').order_by(EyeTestRecord.date_conducted.asc()).all()
    
    return render_template('patient/monitor.html', profile=profile, symptoms=symptoms, acuity_tests=acuity_tests)

@app.route('/patient/exercises')
@login_required
def patient_exercises():
    return render_template('patient/exercises.html')

@app.route('/patient/prescriptions')
@login_required
def patient_prescriptions():
    if current_user.role != 'patient':
        return redirect(url_for('doctor_dashboard'))
    prescriptions = current_user.patient_profile.prescriptions.order_by(Prescription.created_at.desc()).all()
    return render_template('patient/prescriptions.html', prescriptions=prescriptions)

@app.route('/patient/appointments', methods=['GET', 'POST'])
@login_required
def patient_appointments():
    if current_user.role != 'patient':
        return redirect(url_for('doctor_dashboard'))
        
    profile = current_user.patient_profile
    doctors = DoctorProfile.query.all()
    
    if request.method == 'POST':
        doctor_id = int(request.form.get('doctor_id'))
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        reason = request.form.get('reason')
        consultation_type = request.form.get('consultation_type', 'Telehealth Video Review')
        
        try:
            scheduled_dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except:
            scheduled_dt = datetime.datetime.utcnow() + datetime.timedelta(days=2)
            
        new_apt = Appointment(
            patient_id=profile.id,
            doctor_id=doctor_id,
            scheduled_time=scheduled_dt,
            reason=reason,
            consultation_type=consultation_type,
            status='scheduled'
        )
        db.session.add(new_apt)
        db.session.commit()
        flash('Consultation request confirmed! Your physician will review your clinical history.', 'success')
        return redirect(url_for('patient_appointments'))
        
    appointments = profile.appointments.order_by(Appointment.scheduled_time.desc()).all()
    return render_template('patient/appointments.html', appointments=appointments, doctors=doctors)

# ----------------- Doctor Routes -----------------
@app.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor':
        return redirect(url_for('patient_dashboard'))
        
    doc_profile = current_user.doctor_profile
    patients = PatientProfile.query.all()
    urgent_records = EyeTestRecord.query.filter(
        (EyeTestRecord.severity.in_(['moderate', 'severe', 'abnormal'])) |
        (EyeTestRecord.flagged_for_attention == True)
    ).order_by(EyeTestRecord.date_conducted.desc()).limit(8).all()
    
    upcoming_apts = Appointment.query.filter_by(doctor_id=doc_profile.id, status='scheduled').order_by(Appointment.scheduled_time.asc()).limit(6).all()
    all_tests_count = EyeTestRecord.query.count()
    
    return render_template(
        'doctor/dashboard.html',
        doctor=doc_profile,
        patients=patients,
        urgent_records=urgent_records,
        upcoming_apts=upcoming_apts,
        all_tests_count=all_tests_count
    )

@app.route('/doctor/patient/<int:patient_id>')
@login_required
def doctor_patient_detail(patient_id):
    if current_user.role != 'doctor':
        return redirect(url_for('patient_dashboard'))
        
    patient = PatientProfile.query.get_or_404(patient_id)
    tests = patient.test_records.order_by(EyeTestRecord.date_conducted.desc()).all()
    symptoms = patient.symptom_logs.order_by(SymptomLog.timestamp.desc()).limit(14).all()
    prescriptions = patient.prescriptions.order_by(Prescription.created_at.desc()).all()
    assigned = patient.assigned_tests.order_by(AssignedTest.created_at.desc()).all()
    
    return render_template(
        'doctor/patient_detail.html',
        patient=patient,
        tests=tests,
        symptoms=symptoms,
        prescriptions=prescriptions,
        assigned=assigned
    )

@app.route('/doctor/prescription/new/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def doctor_new_prescription(patient_id):
    if current_user.role != 'doctor':
        return redirect(url_for('patient_dashboard'))
        
    patient = PatientProfile.query.get_or_404(patient_id)
    doc_profile = current_user.doctor_profile
    
    if request.method == 'POST':
        rx = Prescription(
            patient_id=patient.id,
            doctor_id=doc_profile.id,
            valid_until=datetime.datetime.utcnow() + datetime.timedelta(days=365),
            od_sphere=request.form.get('od_sphere', '0.00'),
            od_cylinder=request.form.get('od_cylinder', '0.00'),
            od_axis=request.form.get('od_axis', '0'),
            od_add=request.form.get('od_add', '+0.00'),
            os_sphere=request.form.get('os_sphere', '0.00'),
            os_cylinder=request.form.get('os_cylinder', '0.00'),
            os_axis=request.form.get('os_axis', '0'),
            os_add=request.form.get('os_add', '+0.00'),
            pupillary_distance=request.form.get('pupillary_distance', '62 mm'),
            lens_type=request.form.get('lens_type', 'Single Vision'),
            medication_and_instructions=request.form.get('medication_and_instructions', ''),
            status='active'
        )
        db.session.add(rx)
        db.session.commit()
        flash(f'Optical prescription issued successfully for {patient.user.full_name}!', 'success')
        return redirect(url_for('doctor_patient_detail', patient_id=patient.id))
        
    return render_template('doctor/write_prescription.html', patient=patient, doctor=doc_profile)

@app.route('/doctor/assign-test/<int:patient_id>', methods=['POST'])
@login_required
def doctor_assign_test(patient_id):
    if current_user.role != 'doctor':
        abort(403)
        
    test_type = request.form.get('test_type')
    frequency = request.form.get('frequency', 'Weekly')
    instructions = request.form.get('instructions', '')
    
    assignment = AssignedTest(
        patient_id=patient_id,
        doctor_id=current_user.doctor_profile.id,
        test_type=test_type,
        frequency=frequency,
        clinical_instructions=instructions,
        status='pending',
        due_date=datetime.datetime.utcnow() + datetime.timedelta(days=7)
    )
    db.session.add(assignment)
    db.session.commit()
    flash('Remote eye test assigned to patient successfully.', 'success')
    return redirect(url_for('doctor_patient_detail', patient_id=patient_id))

@app.route('/doctor/review-test/<int:record_id>', methods=['POST'])
@login_required
def doctor_review_test(record_id):
    if current_user.role != 'doctor':
        abort(403)
        
    record = EyeTestRecord.query.get_or_404(record_id)
    notes = request.form.get('notes')
    flagged = 'flagged' in request.form
    
    record.reviewed_by_doctor_id = current_user.doctor_profile.id
    record.doctor_review_notes = notes
    record.doctor_reviewed_at = datetime.datetime.utcnow()
    record.flagged_for_attention = flagged
    
    db.session.commit()
    flash('Clinical review notes saved successfully.', 'success')
    return redirect(url_for('patient_test_result', record_id=record.id))

# ----------------- APIs for Interactive Testing & Monitoring -----------------
@app.route('/api/save-test-result', methods=['POST'])
@login_required
def api_save_test_result():
    if current_user.role != 'patient':
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json() or {}
    test_type = data.get('test_type')
    eye_tested = data.get('eye_tested', 'OU')
    primary_score = data.get('primary_score', 'Completed')
    secondary_score = data.get('secondary_score', '')
    numerical_metric = float(data.get('numerical_metric', 0.0))
    severity = data.get('severity', 'normal')
    test_data = data.get('test_data', {})
    distance_cm = float(data.get('distance_cm', 60.0))
    calibration_ppi = float(data.get('screen_calibration_ppi', 96.0))
    patient_notes = data.get('patient_notes', '')

    record = EyeTestRecord(
        patient_id=current_user.patient_profile.id,
        test_type=test_type,
        eye_tested=eye_tested,
        primary_score=primary_score,
        secondary_score=secondary_score,
        numerical_metric=numerical_metric,
        severity=severity,
        test_data_json=json.dumps(test_data),
        distance_cm=distance_cm,
        screen_calibration_ppi=calibration_ppi,
        patient_notes=patient_notes,
        flagged_for_attention=(severity in ['moderate', 'severe', 'abnormal'])
    )
    db.session.add(record)
    
    # Mark matching assigned task as completed if present
    assigned = AssignedTest.query.filter_by(
        patient_id=current_user.patient_profile.id,
        test_type=test_type,
        status='pending'
    ).first()
    if assigned:
        assigned.status = 'completed'

    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'record_id': record.id,
        'redirect_url': url_for('patient_test_result', record_id=record.id)
    })

@app.route('/api/log-symptoms', methods=['POST'])
@login_required
def api_log_symptoms():
    if current_user.role != 'patient':
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json() or {}
    log = SymptomLog(
        patient_id=current_user.patient_profile.id,
        eye_strain=int(data.get('eye_strain', 1)),
        blurriness=int(data.get('blurriness', 1)),
        dryness=int(data.get('dryness', 1)),
        headache=int(data.get('headache', 1)),
        light_sensitivity=int(data.get('light_sensitivity', 1)),
        screen_hours=float(data.get('screen_hours', 6.0)),
        notes=data.get('notes', '')
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Symptom log updated.'})

# ----------------- PDF Export Route -----------------
@app.route('/download-report/<int:patient_id>')
@login_required
def download_patient_report(patient_id):
    patient = PatientProfile.query.get_or_404(patient_id)
    
    # Permission check
    if current_user.role == 'patient' and patient.id != current_user.patient_profile.id:
        abort(403)
        
    test_records = patient.test_records.order_by(EyeTestRecord.date_conducted.desc()).all()
    doctor = patient.preferred_doctor or DoctorProfile.query.first()
    prescription = patient.prescriptions.filter_by(status='active').order_by(Prescription.created_at.desc()).first()
    
    pdf_bytes = generate_patient_report_pdf(patient, test_records, doctor, prescription)
    
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"OptiVision_Report_{patient.user.full_name.replace(' ', '_')}_{datetime.date.today()}.pdf"
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() in ['true', '1']
    print(f"OptiVision Eye Health Platform running on http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
