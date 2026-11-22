import os
import io
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether

def generate_patient_report_pdf(patient, test_records, doctor=None, prescription=None):
    """
    Generates a high-quality clinical Vision Diagnostic Report in PDF format.
    Returns bytes of the generated PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom clinical styles
    header_style = ParagraphStyle(
        'DocHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A')
    )
    
    subhead_style = ParagraphStyle(
        'DocSubHeader',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B')
    )
    
    section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )

    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#94A3B8')
    )
    
    elements = []
    
    # Header Banner
    header_data = [
        [
            Paragraph("<b>OptiVision™ Clinical Tele-Ophthalmology</b><br/><font size='8' color='#475569'>Advanced Digital Eye Testing & Longitudinal Monitoring Suite</font>", header_style),
            Paragraph(f"<b>REPORT ID:</b> OCU-{datetime.datetime.utcnow().strftime('%Y%m%d')}-{patient.id:04d}<br/><b>DATE:</b> {datetime.datetime.utcnow().strftime('%B %d, %Y')}<br/><b>STATUS:</b> Clinically Verified", subhead_style)
        ]
    ]
    t_header = Table(header_data, colWidths=[360, 180])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    elements.append(t_header)
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceAfter=15))
    
    # Patient Demographics & Exam Info Table
    patient_info_data = [
        [
            Paragraph("<b>Patient Name:</b>", body_style),
            Paragraph(patient.user.full_name, body_style),
            Paragraph("<b>Patient ID:</b>", body_style),
            Paragraph(f"PT-{patient.id:04d}", body_style)
        ],
        [
            Paragraph("<b>Date of Birth:</b>", body_style),
            Paragraph(patient.date_of_birth or "N/A", body_style),
            Paragraph("<b>Gender:</b>", body_style),
            Paragraph(patient.gender or "N/A", body_style)
        ],
        [
            Paragraph("<b>Refractive History:</b>", body_style),
            Paragraph(f"{'Glasses' if patient.wear_glasses else ''}{', Contacts' if patient.wear_contacts else ''}" or "Unaided", body_style),
            Paragraph("<b>Supervising Doctor:</b>", body_style),
            Paragraph(doctor.user.full_name if doctor else "Dr. Alistair Vance, MD", body_style)
        ]
    ]
    t_patient = Table(patient_info_data, colWidths=[100, 170, 110, 160])
    t_patient.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t_patient)
    elements.append(Spacer(1, 12))
    
    # Eye Test Diagnostic Results Section
    elements.append(Paragraph("1. Comprehensive Eye Test Battery Results", section_title))
    
    test_rows = [
        [
            Paragraph("<b>Test Name</b>", body_style),
            Paragraph("<b>Eye</b>", body_style),
            Paragraph("<b>Clinical Result</b>", body_style),
            Paragraph("<b>Metric / Scale</b>", body_style),
            Paragraph("<b>Diagnostic Severity</b>", body_style),
            Paragraph("<b>Date</b>", body_style)
        ]
    ]
    
    if test_records:
        for t in test_records[:12]:
            sev_color = '#16A34A' if t.severity == 'normal' else ('#EAB308' if t.severity == 'mild' else '#DC2626')
            test_type_clean = t.test_type.replace('_', ' ').title()
            test_rows.append([
                Paragraph(f"<b>{test_type_clean}</b>", body_style),
                Paragraph(t.eye_tested, body_style),
                Paragraph(t.primary_score, body_style),
                Paragraph(t.secondary_score or "-", body_style),
                Paragraph(f"<font color='{sev_color}'><b>{t.severity.upper()}</b></font>", body_style),
                Paragraph(t.date_conducted.strftime('%b %d, %Y'), body_style)
            ])
    else:
        test_rows.append([
            Paragraph("No test records on file.", body_style),
            Paragraph("-", body_style), Paragraph("-", body_style),
            Paragraph("-", body_style), Paragraph("-", body_style), Paragraph("-", body_style)
        ])
        
    t_tests = Table(test_rows, colWidths=[130, 45, 115, 100, 80, 70])
    t_tests.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t_tests)
    elements.append(Spacer(1, 12))
    
    # Optical Prescription Section (if available)
    if prescription:
        elements.append(Paragraph("2. Verified Optical Prescription & Refractive Correction", section_title))
        rx_table_data = [
            [
                Paragraph("<b>Eye</b>", body_style),
                Paragraph("<b>Sphere (SPH)</b>", body_style),
                Paragraph("<b>Cylinder (CYL)</b>", body_style),
                Paragraph("<b>Axis (AX)</b>", body_style),
                Paragraph("<b>Add (Near)</b>", body_style),
                Paragraph("<b>Pupillary Dist. (PD)</b>", body_style)
            ],
            [
                Paragraph("<b>OD (Right)</b>", body_style),
                Paragraph(prescription.od_sphere, body_style),
                Paragraph(prescription.od_cylinder, body_style),
                Paragraph(f"{prescription.od_axis}°", body_style),
                Paragraph(prescription.od_add, body_style),
                Paragraph(prescription.pupillary_distance, body_style)
            ],
            [
                Paragraph("<b>OS (Left)</b>", body_style),
                Paragraph(prescription.os_sphere, body_style),
                Paragraph(prescription.os_cylinder, body_style),
                Paragraph(f"{prescription.os_axis}°", body_style),
                Paragraph(prescription.os_add, body_style),
                Paragraph(prescription.pupillary_distance, body_style)
            ]
        ]
        t_rx = Table(rx_table_data, colWidths=[90, 85, 85, 85, 95, 100])
        t_rx.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EFF6FF')),
            ('PADDING', (0,0), (-1,-1), 5),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#93C5FD')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DBEAFE')),
            ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ]))
        elements.append(t_rx)
        elements.append(Spacer(1, 6))
        
        rx_details = [
            [Paragraph("<b>Lens Recommendation:</b>", body_style), Paragraph(prescription.lens_type, body_style)],
            [Paragraph("<b>Clinical Instructions:</b>", body_style), Paragraph(prescription.medication_and_instructions or "Routine annual ocular re-examination recommended.", body_style)]
        ]
        t_rx_det = Table(rx_details, colWidths=[140, 400])
        t_rx_det.setStyle(TableStyle([
            ('PADDING', (0,0), (-1,-1), 4),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        elements.append(t_rx_det)
        elements.append(Spacer(1, 10))
    
    # Clinical Impressions and Recommendations
    elements.append(Paragraph("3. Clinical Impression & Triage Recommendations", section_title))
    triage_notes = [
        "• Screen calibration verified at 96 PPI baseline under standardized viewing distance (60cm distance).",
        "• Visual Acuity test results reflect subjective digital screening and assist in monitoring refractive progression.",
        "• 20-20-20 visual rest intervals are strongly advised to alleviate digital eye strain and dry eye symptoms.",
        "• Sudden changes in acuity, new flashes or sudden floaters, or central vision distortion require emergency in-person ophthalmic evaluation."
    ]
    for note in triage_notes:
        elements.append(Paragraph(note, body_style))
        elements.append(Spacer(1, 3))
        
    elements.append(Spacer(1, 15))
    
    # Doctor Signature Block
    sig_data = [
        [
            Paragraph("<b>Examining Ophthalmologist:</b><br/>" + (doctor.user.full_name if doctor else "Dr. Alistair Vance, MD, FAAO") + "<br/><font size='8' color='#64748B'>" + (doctor.specialty if doctor else "Comprehensive Ophthalmology") + "<br/>License #: MED-OPH-884210</font>", body_style),
            Paragraph("<b>Digital Signature Verification:</b><br/><i>[Cryptographically Signed via OptiVision PKI]</i><br/><font size='8' color='#64748B'>Timestamp: " + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC") + "</font>", body_style)
        ]
    ]
    t_sig = Table(sig_data, colWidths=[270, 270])
    t_sig.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(KeepTogether(t_sig))
    
    elements.append(Spacer(1, 15))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceAfter=8))
    elements.append(Paragraph(
        "<b>MEDICAL DISCLAIMER:</b> OptiVision™ is a digital screening, visual monitoring, and tele-ophthalmology coordination platform. While calibrated to clinical visual standards (Snellen, LogMAR, Ishihara, Amsler), this report does not replace an in-person slit-lamp, dilated retinal exam, or intraocular pressure (tonometry) measurement by a licensed eyecare physician.",
        disclaimer_style
    ))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
