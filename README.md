# OptiVision™ Eye Testing & Longitudinal Monitoring Platform

OptiVision is a full-featured clinical tele-ophthalmology web application designed for both **patients** and **eyecare physicians (optometrists & ophthalmologists)**. Built with Python Flask, SQLite, Tailwind CSS, HTML5 Canvas, Chart.js, and ReportLab PDF Generation.

---

## 🌟 Key Features

### 1. For Patients
* **Screen PPI Optical Calibration**: Physical reference slider (using standard credit card width: 85.6 mm / 3.37 inches) to guarantee millimetric visual angle accuracy (5 arcminutes) on any desktop, laptop, or tablet.
* **Full Diagnostic Eye Testing Suite**:
  1. **Visual Acuity Screening (Snellen Chart & Tumbling E)**:
     - Calibrated for 1m, 1.5m, 2m, 3m, or 40cm near vision.
     - Monocular isolation (OD: Right Eye, OS: Left Eye, OU: Both Eyes).
     - Text-to-speech voice guidance (`SpeechSynthesis`) for hands-free audio testing from across the room.
     - Keyboard arrow keys & on-screen controllers.
     - Computes LogMAR and standard 20/200 down to 20/15 Snellen fractions.
  2. **Ishihara Pseudoisochromatic Color Plates**:
     - 10 randomized pseudo-isochromatic canvas dot plates.
     - Screens and classifies Protanopia (red deficiency), Deuteranopia (green deficiency), and Tritanopia.
  3. **Astigmatism Clock Dial & Fan Test**:
     - 360-degree high-definition radial line wheel.
     - Detects corneal refractive asymmetry, cylinder axis (Rule of 30), with-the-rule (WTR) vs against-the-rule (ATR).
  4. **Pelli-Robson Contrast Sensitivity Test**:
     - Progressively degrades letter contrast from 100% down to 1.5% to detect subclinical glaucoma, cataract, and retinal changes.
  5. **Amsler Grid Retina / Macular Map**:
     - Interactive drawing canvas for detecting Age-Related Macular Degeneration (AMD) and central serous retinopathy.
     - Patients can mark blind spots (scotomas) or wavy distorted lines (metamorphopsia) directly on the grid.
  6. **Dry Eye & Computer Vision Syndrome (OSDI)**:
     - Standardized 12-item clinical Ocular Surface Disease Index (OSDI) calculating 0–100 score and risk classification.
* **Longitudinal Vision Tracker & Symptom Journal**:
  - Interactive daily logger: Eye strain (1-10), blurriness, dryness, headache, light sensitivity, and screen hours.
  - Interactive Chart.js charts: Visual Acuity stability curve over time and Screen Exposure vs Strain correlation graph.
* **Digital Ergonomics & 20-20-20 Rule Coach**:
  - 20-minute countdown work timer with audible bell and guided 20-second 20-foot relaxation intervals.
  - Blinking trainer and ocular muscle exercises.
* **Verified Optical Prescriptions**:
  - View official digital prescriptions issued by doctors (Sphere, Cylinder, Axis, Add, PD, lens coatings).
* **Telehealth Consultation Booking**:
  - Book video reviews or in-clinic dilated examinations with certified ophthalmologists.
* **Downloadable Medical PDF Reports**:
  - Formal clinical reports generated on the fly via ReportLab.

### 2. For Doctors (Ophthalmologists & Optometrists)
* **Clinical Triage Dashboard**:
  - Triage feed identifying abnormal test results (e.g. marked macular scotomas, acuity drops >2 lines, elevated CVS index).
  - Upcoming telehealth consultations and patient roster.
* **Comprehensive Patient Dossiers**:
  - Full longitudinal examination history, visual acuity curves, symptom progression.
  - Interactive inspection of patient-drawn Amsler grid scotoma maps.
* **Remote Eye Test Assignment**:
  - Assign specific home monitoring tests (e.g., "Take Amsler grid every 3 days" or "Weekly OSDI").
* **Digital Optical Prescription Writer**:
  - Issue formal digital optical Rx (OD/OS Sphere, Cylinder, Axis, Add, PD, lens recommendations, medication drops).
* **Physician Test Review & Clinical Impressions**:
  - Append official doctor review notes and urgent attention flags to any exam record.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+ (Tested and verified with Python 3.14)
- Packages installed: `Flask`, `Flask-SQLAlchemy`, `Flask-Login`, `reportlab`, `pillow`

### Running the Platform
Navigate to the project folder:
```powershell
cd C:\Users\virup\.gemini\antigravity\scratch\ocucare-vision-platform
python app.py
```
Open your browser at:
```
http://127.0.0.1:5000
```

---

## 👥 Demo Accounts (1-Click Switcher Available in Navigation)

The platform comes pre-seeded with realistic clinical data:

| Role | Username | Password | Notes |
|------|----------|----------|-------|
| **Doctor** | `doctor_vance` | `password123` | Dr. Alistair Vance, MD (Chief Ophthalmologist) |
| **Doctor** | `doctor_rostova` | `password123` | Dr. Elena Rostova, OD (Optometry & Retina) |
| **Patient** | `patient_jane` | `password123` | Jane Doe (Myopia, Dry Eye, 9 hrs daily screen) |
| **Patient** | `patient_robert` | `password123` | Robert Martinez (Early AMD, Amsler Scotoma Anomaly) |
| **Patient** | `patient_maya` | `password123` | Maya Lin (Deuteranopia Color Blindness) |

*You can also switch instantaneously between any demo account using the "Switch Demo Role" dropdown in the top-right navbar!*

---

## 🛡️ Medical Disclaimer
OptiVision is a screening, longitudinal monitoring, and tele-ophthalmology coordination platform calibrated to ISO 8596 standards. It assists doctors and patients in tracking vision between clinic visits, but does not substitute an in-person dilated fundus exam, slit-lamp biomicroscopy, or intraocular pressure measurement.
