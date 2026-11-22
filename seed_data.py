import datetime
from models import db, User, PatientProfile, DoctorProfile, EyeTestRecord, SymptomLog, Prescription, Appointment, AssignedTest

def seed_database(app):
    with app.app_context():
        # Check if already seeded
        if User.query.first():
            print("Database already contains data, skipping seed.")
            return

        print("Seeding database with clinical ophthalmic records...")

        # 1. Create Doctors
        doc_user1 = User(
            username='doctor_vance',
            email='dr.vance@optivision.health',
            role='doctor',
            full_name='Dr. Alistair Vance, MD, FAAO',
            phone='+1 (555) 438-9201'
        )
        doc_user1.set_password('password123')
        db.session.add(doc_user1)
        db.session.flush()

        doc_profile1 = DoctorProfile(
            user_id=doc_user1.id,
            title='MD, Board-Certified Ophthalmologist',
            specialty='Comprehensive Ophthalmology & Cornea Specialist',
            license_number='MED-OPH-884210',
            clinic_name='Metro Health Eye & Vision Institute',
            clinic_address='450 Lexington Ave, Suite 700, New York, NY',
            consultation_fee=110.0,
            bio='Specializing in refractive error correction, corneal disorders, and digital tele-ophthalmology monitoring with over 15 years of clinical practice.'
        )
        db.session.add(doc_profile1)

        doc_user2 = User(
            username='doctor_rostova',
            email='dr.rostova@optivision.health',
            role='doctor',
            full_name='Dr. Elena Rostova, OD',
            phone='+1 (555) 872-3341'
        )
        doc_user2.set_password('password123')
        db.session.add(doc_user2)
        db.session.flush()

        doc_profile2 = DoctorProfile(
            user_id=doc_user2.id,
            title='OD, Doctor of Optometry',
            specialty='Computer Vision Syndrome & Retinal Screening',
            license_number='OPT-NYC-49102',
            clinic_name='VisionCare Advanced Center',
            clinic_address='128 5th Ave, Floor 3, New York, NY',
            consultation_fee=85.0,
            bio='Dedicated to treating ocular surface disease, dry eye management, and digital fatigue in office workers.'
        )
        db.session.add(doc_profile2)
        db.session.flush()

        # 2. Create Patients
        # Patient 1: Jane Doe (Software Engineer with CVS and mild myopia)
        pat_user1 = User(
            username='patient_jane',
            email='jane.doe@example.com',
            role='patient',
            full_name='Jane Doe',
            phone='+1 (555) 234-5678'
        )
        pat_user1.set_password('password123')
        db.session.add(pat_user1)
        db.session.flush()

        pat_profile1 = PatientProfile(
            user_id=pat_user1.id,
            date_of_birth='1996-04-12',
            gender='Female',
            wear_glasses=True,
            wear_contacts=True,
            medical_history='Mild seasonal allergies, 9+ hours daily screen exposure. Wears contact lenses during work.',
            preferred_doctor_id=doc_profile1.id
        )
        db.session.add(pat_profile1)
        db.session.flush()

        # Patient 2: Robert Martinez (Senior patient monitoring AMD / Amsler grid)
        pat_user2 = User(
            username='patient_robert',
            email='robert.m@example.com',
            role='patient',
            full_name='Robert Martinez',
            phone='+1 (555) 789-0123'
        )
        pat_user2.set_password('password123')
        db.session.add(pat_user2)
        db.session.flush()

        pat_profile2 = PatientProfile(
            user_id=pat_user2.id,
            date_of_birth='1962-09-24',
            gender='Male',
            wear_glasses=True,
            wear_contacts=False,
            medical_history='Borderline dry age-related macular degeneration (AMD) in left eye. Takes AREDS2 supplements.',
            preferred_doctor_id=doc_profile1.id
        )
        db.session.add(pat_profile2)
        db.session.flush()

        # Patient 3: Maya Lin (Color vision deficiency check)
        pat_user3 = User(
            username='patient_maya',
            email='maya.lin@example.com',
            role='patient',
            full_name='Maya Lin',
            phone='+1 (555) 345-6789'
        )
        pat_user3.set_password('password123')
        db.session.add(pat_user3)
        db.session.flush()

        pat_profile3 = PatientProfile(
            user_id=pat_user3.id,
            date_of_birth='2002-11-05',
            gender='Female',
            wear_glasses=False,
            wear_contacts=False,
            medical_history='Screening for digital design career; suspected subtle red-green color confusion.',
            preferred_doctor_id=doc_profile2.id
        )
        db.session.add(pat_profile3)
        db.session.flush()

        # 3. Add Test Records for Jane Doe
        now = datetime.datetime.utcnow()
        
        # Historical Acuity tests (showing slight fatigue / fluctuations)
        acuity_tests = [
            (now - datetime.timedelta(days=60), 'OU', '20/20', 'LogMAR 0.00', 0.0, 'normal', 'Screen distance 60cm, calibrated at 96 PPI.'),
            (now - datetime.timedelta(days=30), 'OD', '20/25', 'LogMAR 0.10', 0.1, 'mild', 'Right eye unaided testing showed minor blurring on row 8.'),
            (now - datetime.timedelta(days=30), 'OS', '20/30', 'LogMAR 0.18', 0.18, 'mild', 'Left eye unaided testing.'),
            (now - datetime.timedelta(days=2), 'OU', '20/20', 'LogMAR 0.00', 0.0, 'normal', 'Aided with corrective glasses.')
        ]
        for dt, eye, primary, sec, num, sev, note in acuity_tests:
            db.session.add(EyeTestRecord(
                patient_id=pat_profile1.id,
                test_type='visual_acuity',
                eye_tested=eye,
                primary_score=primary,
                secondary_score=sec,
                numerical_metric=num,
                severity=sev,
                distance_cm=60.0,
                screen_calibration_ppi=96.0,
                date_conducted=dt,
                patient_notes=note,
                reviewed_by_doctor_id=doc_profile1.id,
                doctor_review_notes="Refractive acuity stable with current prescription.",
                doctor_reviewed_at=dt + datetime.timedelta(hours=4)
            ))

        # Color Vision Test for Jane
        db.session.add(EyeTestRecord(
            patient_id=pat_profile1.id,
            test_type='color_vision',
            eye_tested='OU',
            primary_score='14/14 Correct (100%)',
            secondary_score='Standard Trichromat',
            numerical_metric=100.0,
            severity='normal',
            distance_cm=50.0,
            screen_calibration_ppi=96.0,
            date_conducted=now - datetime.timedelta(days=14),
            patient_notes='All 14 Ishihara plates identified quickly.'
        ))

        # Astigmatism Test for Jane
        db.session.add(EyeTestRecord(
            patient_id=pat_profile1.id,
            test_type='astigmatism',
            eye_tested='OU',
            primary_score='Mild Distortion at 85°-90°',
            secondary_score='Consistent with WTR Cylinder',
            numerical_metric=85.0,
            severity='mild',
            distance_cm=60.0,
            screen_calibration_ppi=96.0,
            date_conducted=now - datetime.timedelta(days=10),
            patient_notes='Vertical radiating lines appear distinctly darker and bolder.'
        ))

        # Dry Eye / CVS Test for Jane
        db.session.add(EyeTestRecord(
            patient_id=pat_profile1.id,
            test_type='dry_eye_cvs',
            eye_tested='OU',
            primary_score='OSDI Score: 41.6 / 100',
            secondary_score='Moderate Ocular Surface Disease',
            numerical_metric=41.6,
            severity='moderate',
            distance_cm=60.0,
            date_conducted=now - datetime.timedelta(days=3),
            patient_notes='Stinging sensation and grittiness after 4pm at work.',
            reviewed_by_doctor_id=doc_profile1.id,
            doctor_review_notes="Advised preservative-free artificial lubricant drops 4x daily, blue blocker lenses, and active 20-20-20 breaks.",
            doctor_reviewed_at=now - datetime.timedelta(days=2),
            flagged_for_attention=True
        ))

        # Contrast Sensitivity for Jane
        db.session.add(EyeTestRecord(
            patient_id=pat_profile1.id,
            test_type='contrast_sensitivity',
            eye_tested='OU',
            primary_score='1.80 logCS (Normal)',
            secondary_score='Threshold: 1.5% contrast',
            numerical_metric=1.80,
            severity='normal',
            distance_cm=100.0,
            date_conducted=now - datetime.timedelta(days=1)
        ))

        # 4. Add Test Records for Robert Martinez (Amsler Grid anomaly)
        amsler_test = EyeTestRecord(
            patient_id=pat_profile2.id,
            test_type='amsler_grid',
            eye_tested='OS',
            primary_score='Metamorphopsia & Scotoma Detected',
            secondary_score='Paracentral Distortion (~3° inferior-temporal)',
            numerical_metric=2.0,
            severity='moderate',
            distance_cm=35.0,
            screen_calibration_ppi=96.0,
            date_conducted=now - datetime.timedelta(days=5),
            patient_notes='Noticed wavy grid lines near the central red fixation point.',
            test_data_json='{"scotomas": [{"x": 180, "y": 210, "radius": 24}], "distortions": [{"x": 195, "y": 225, "type": "wavy"}]}',
            reviewed_by_doctor_id=doc_profile1.id,
            doctor_review_notes="Flagged for in-clinic OCT (Optical Coherence Tomography) scan to rule out choroidal neovascularization.",
            doctor_reviewed_at=now - datetime.timedelta(days=4),
            flagged_for_attention=True
        )
        db.session.add(amsler_test)

        # 5. Add Color Blindness Test for Maya Lin
        color_test_maya = EyeTestRecord(
            patient_id=pat_profile3.id,
            test_type='color_vision',
            eye_tested='OU',
            primary_score='9/14 Correct (64%)',
            secondary_score='Deuteranopia / Red-Green Deficiency',
            numerical_metric=64.0,
            severity='abnormal',
            distance_cm=50.0,
            date_conducted=now - datetime.timedelta(days=8),
            patient_notes='Plate 6 and Plate 11 appeared as blank dots.',
            reviewed_by_doctor_id=doc_profile2.id,
            doctor_review_notes="Deuteranomalous color deficiency confirmed. Provided digital color-assist palette guidance.",
            doctor_reviewed_at=now - datetime.timedelta(days=7)
        )
        db.session.add(color_test_maya)

        # 6. Symptom Logs for Jane Doe (Past 7 days)
        symptoms_history = [
            (now - datetime.timedelta(days=6), 7, 5, 8, 6, 4, 9.5, "Long coding sprint, gritty dry eyes by evening"),
            (now - datetime.timedelta(days=5), 6, 4, 7, 5, 3, 8.5, "Used artificial tears twice, felt better"),
            (now - datetime.timedelta(days=4), 4, 3, 5, 3, 2, 6.0, "Weekend rest, reduced screen time"),
            (now - datetime.timedelta(days=3), 3, 2, 3, 2, 1, 4.0, "Outdoor walk, no eye strain"),
            (now - datetime.timedelta(days=2), 6, 4, 6, 4, 3, 8.0, "Back at office, fluorescent lights causing glare"),
            (now - datetime.timedelta(days=1), 5, 3, 6, 3, 2, 7.5, "Did 20-20-20 breaks throughout afternoon"),
            (now, 4, 2, 4, 2, 2, 5.0, "Managing well with lubricant drops")
        ]
        for ts, strain, blur, dry, head, light, hrs, nt in symptoms_history:
            db.session.add(SymptomLog(
                patient_id=pat_profile1.id,
                timestamp=ts,
                eye_strain=strain,
                blurriness=blur,
                dryness=dry,
                headache=head,
                light_sensitivity=light,
                screen_hours=hrs,
                notes=nt
            ))

        # 7. Optical Prescription for Jane Doe
        rx1 = Prescription(
            patient_id=pat_profile1.id,
            doctor_id=doc_profile1.id,
            created_at=now - datetime.timedelta(days=20),
            valid_until=now + datetime.timedelta(days=345),
            od_sphere="-1.25",
            od_cylinder="-0.50",
            od_axis="85",
            od_add="+0.00",
            os_sphere="-1.50",
            os_cylinder="-0.75",
            os_axis="95",
            os_add="+0.00",
            pupillary_distance="63 mm",
            lens_type="Single Vision (Anti-Reflective, High-Index 1.60 with Blue Light Guard)",
            medication_and_instructions="Systane Complete / Refresh Optive preservative-free eye drops 3-4 times daily as needed. Use 20-20-20 rule.",
            status="active"
        )
        db.session.add(rx1)

        # 8. Appointments
        apt1 = Appointment(
            patient_id=pat_profile1.id,
            doctor_id=doc_profile1.id,
            scheduled_time=now + datetime.timedelta(days=3, hours=2),
            reason="Follow-up on dry eye syndrome and review computer vision test results",
            consultation_type="Telehealth Video Review",
            status="scheduled",
            notes="Patient reports good response to artificial tears, check OSDI trend."
        )
        db.session.add(apt1)

        apt2 = Appointment(
            patient_id=pat_profile2.id,
            doctor_id=doc_profile1.id,
            scheduled_time=now + datetime.timedelta(days=1, hours=4),
            reason="URGENT: Amsler grid metamorphopsia in OS paracentral region",
            consultation_type="In-Clinic Comprehensive Dilated Exam",
            status="scheduled",
            notes="Prioritize OCT imaging of the macula."
        )
        db.session.add(apt2)

        # 9. Assigned Test Tasks
        task1 = AssignedTest(
            patient_id=pat_profile1.id,
            doctor_id=doc_profile1.id,
            test_type='dry_eye_cvs',
            frequency='Weekly',
            status='pending',
            due_date=now + datetime.timedelta(days=4),
            clinical_instructions="Complete OSDI questionnaire every Friday afternoon after work."
        )
        db.session.add(task1)

        task2 = AssignedTest(
            patient_id=pat_profile2.id,
            doctor_id=doc_profile1.id,
            test_type='amsler_grid',
            frequency='Every 3 Days',
            status='pending',
            due_date=now + datetime.timedelta(days=1),
            clinical_instructions="Check OS (left eye) carefully on the grid. Contact clinic immediately if distortion expands."
        )
        db.session.add(task2)

        db.session.commit()
        print("Database seeded successfully with doctors, patients, tests, prescriptions, and symptoms!")
