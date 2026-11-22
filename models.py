import datetime
import json
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='patient') # 'patient' or 'doctor'
    full_name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    phone = db.Column(db.String(30), nullable=True)

    # Relationships
    patient_profile = db.relationship('PatientProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    doctor_profile = db.relationship('DoctorProfile', backref='user', uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class PatientProfile(db.Model):
    __tablename__ = 'patient_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    date_of_birth = db.Column(db.String(20), nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    wear_glasses = db.Column(db.Boolean, default=False)
    wear_contacts = db.Column(db.Boolean, default=False)
    medical_history = db.Column(db.Text, nullable=True)
    preferred_doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_profiles.id'), nullable=True)

    # Relationships
    test_records = db.relationship('EyeTestRecord', backref='patient', cascade="all, delete-orphan", lazy='dynamic')
    symptom_logs = db.relationship('SymptomLog', backref='patient', cascade="all, delete-orphan", lazy='dynamic')
    prescriptions = db.relationship('Prescription', backref='patient', cascade="all, delete-orphan", lazy='dynamic')
    appointments = db.relationship('Appointment', backref='patient', cascade="all, delete-orphan", lazy='dynamic')
    assigned_tests = db.relationship('AssignedTest', backref='patient', cascade="all, delete-orphan", lazy='dynamic')

class DoctorProfile(db.Model):
    __tablename__ = 'doctor_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    title = db.Column(db.String(50), default="MD, Ophthalmologist")
    specialty = db.Column(db.String(100), default="Comprehensive Ophthalmology & Refractive Care")
    license_number = db.Column(db.String(50), nullable=True)
    clinic_name = db.Column(db.String(150), default="St. Jude Eye & Vision Institute")
    clinic_address = db.Column(db.String(255), default="Suite 400, Medical Plaza, Metro Health District")
    consultation_fee = db.Column(db.Float, default=75.0)
    bio = db.Column(db.Text, nullable=True)
    is_accepting_patients = db.Column(db.Boolean, default=True)

    # Relationships
    prescriptions_issued = db.relationship('Prescription', backref='doctor', lazy='dynamic')
    appointments = db.relationship('Appointment', backref='doctor', lazy='dynamic')
    assigned_tests = db.relationship('AssignedTest', backref='doctor', lazy='dynamic')
    preferred_patients = db.relationship('PatientProfile', backref='preferred_doctor', lazy='dynamic')

class EyeTestRecord(db.Model):
    __tablename__ = 'eye_test_records'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient_profiles.id'), nullable=False)
    test_type = db.Column(db.String(50), nullable=False) 
    # Types: 'visual_acuity', 'color_vision', 'astigmatism', 'contrast_sensitivity', 'amsler_grid', 'dry_eye_cvs'
    
    eye_tested = db.Column(db.String(10), default='OU') # 'OD' (Right), 'OS' (Left), 'OU' (Both)
    primary_score = db.Column(db.String(100), nullable=False) # e.g. "20/20", "13/14 Correct", "Astigmatism at 90°"
    secondary_score = db.Column(db.String(100), nullable=True) # e.g. "LogMAR 0.00", "OSDI Score: 36"
    numerical_metric = db.Column(db.Float, nullable=True) # For graphing trends (e.g. LogMAR value or OSDI index)
    
    severity = db.Column(db.String(30), default='normal') # 'normal', 'mild', 'moderate', 'severe', 'abnormal'
    test_data_json = db.Column(db.Text, nullable=True) # JSON with details (Amsler scotomas, letter matrix, etc)
    
    distance_cm = db.Column(db.Float, default=60.0) # Viewing distance used
    screen_calibration_ppi = db.Column(db.Float, default=96.0) # Calibration PPI
    
    date_conducted = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    patient_notes = db.Column(db.Text, nullable=True)
    
    # Doctor clinical review
    reviewed_by_doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_profiles.id'), nullable=True)
    doctor_review_notes = db.Column(db.Text, nullable=True)
    doctor_reviewed_at = db.Column(db.DateTime, nullable=True)
    flagged_for_attention = db.Column(db.Boolean, default=False)

    @property
    def test_data(self):
        if self.test_data_json:
            try:
                return json.loads(self.test_data_json)
            except:
                return {}
        return {}

    @test_data.setter
    def test_data(self, value):
        self.test_data_json = json.dumps(value)

class SymptomLog(db.Model):
    __tablename__ = 'symptom_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient_profiles.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    eye_strain = db.Column(db.Integer, default=1)      # 1-10
    blurriness = db.Column(db.Integer, default=1)      # 1-10
    dryness = db.Column(db.Integer, default=1)         # 1-10
    headache = db.Column(db.Integer, default=1)        # 1-10
    light_sensitivity = db.Column(db.Integer, default=1)# 1-10
    screen_hours = db.Column(db.Float, default=6.0)    # Hours of digital screen exposure
    notes = db.Column(db.String(255), nullable=True)

class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient_profiles.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_profiles.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    valid_until = db.Column(db.DateTime, nullable=True)
    
    # Right Eye (OD - Oculus Dexter)
    od_sphere = db.Column(db.String(20), default="-1.25")
    od_cylinder = db.Column(db.String(20), default="-0.50")
    od_axis = db.Column(db.String(20), default="85")
    od_add = db.Column(db.String(20), default="+0.00")
    
    # Left Eye (OS - Oculus Sinister)
    os_sphere = db.Column(db.String(20), default="-1.50")
    os_cylinder = db.Column(db.String(20), default="-0.75")
    os_axis = db.Column(db.String(20), default="95")
    os_add = db.Column(db.String(20), default="+0.00")
    
    pupillary_distance = db.Column(db.String(20), default="63 mm")
    lens_type = db.Column(db.String(50), default="Single Vision (Anti-Reflective & Blue Filter)")
    medication_and_instructions = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="active") # 'active', 'expired', 'archived'

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient_profiles.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_profiles.id'), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    consultation_type = db.Column(db.String(50), default="Telehealth Video Review") # or 'In-Clinic Comprehensive'
    status = db.Column(db.String(20), default="scheduled") # 'scheduled', 'completed', 'cancelled'
    doctor_notes = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class AssignedTest(db.Model):
    __tablename__ = 'assigned_tests'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient_profiles.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_profiles.id'), nullable=False)
    test_type = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String(50), default="Weekly") # Daily, Weekly, Bi-weekly, Pre-Visit
    status = db.Column(db.String(20), default="pending") # 'pending', 'completed'
    due_date = db.Column(db.DateTime, nullable=True)
    clinical_instructions = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
