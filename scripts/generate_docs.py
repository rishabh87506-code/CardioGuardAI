"""
CardioGuard AI  -  Documentation Generator
=========================================
Generates the official technical documentation PDF.
Run: python3 scripts/generate_docs.py
Output: docs/CardioGuardAI_Technical_Documentation.pdf
"""

import os
import sys
from fpdf import FPDF
from datetime import datetime

ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(ROOT, 'docs')
OUT_PATH = os.path.join(DOCS_DIR, 'CardioGuardAI_Technical_Documentation.pdf')

os.makedirs(DOCS_DIR, exist_ok=True)

# -- Colour palette ---------------------------------------------------------
RED   = (180,  30,  40)
DARK  = ( 20,  20,  40)
MID   = ( 60,  60,  90)
LIGHT = (240, 244, 252)
WHITE = (255, 255, 255)
GREY  = (100, 100, 110)
GREEN = ( 20, 140,  80)


class PDF(FPDF):
    # -- Header -------------------------------------------------------------
    def header(self):
        if self.page_no() == 1:
            return
        self.set_fill_color(*DARK)
        self.rect(0, 0, 210, 12, 'F')
        self.set_text_color(*WHITE)
        self.set_font('Helvetica', 'B', 8)
        self.set_xy(10, 3)
        self.cell(130, 6, 'CardioGuard AI  -  Technical Documentation', align='L')
        self.set_font('Helvetica', '', 8)
        self.set_xy(140, 3)
        self.cell(60, 6, f'Page {self.page_no()}', align='R')
        self.set_text_color(*DARK)
        self.ln(14)

    # -- Footer -------------------------------------------------------------
    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-12)
        self.set_draw_color(*RED)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(*GREY)
        self.set_xy(10, self.get_y() + 2)
        self.cell(190, 5, 'CONFIDENTIAL  -  Non-Diagnostic Wellness Assessment Tool | cardioguardai.in', align='C')

    # -- Section heading ----------------------------------------------------
    def section(self, num: str, title: str):
        self.ln(4)
        self.set_fill_color(*DARK)
        self.set_text_color(*WHITE)
        self.set_font('Helvetica', 'B', 11)
        self.set_x(10)
        self.cell(190, 8, f'  {num}  {title}', fill=True, ln=True)
        self.set_text_color(*DARK)
        self.ln(3)

    # -- Sub-heading --------------------------------------------------------
    def sub(self, title: str):
        self.ln(3)
        self.set_draw_color(*RED)
        self.set_line_width(0.8)
        self.set_x(10)
        self.line(10, self.get_y(), 14, self.get_y())
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*RED)
        self.set_x(16)
        self.cell(170, 6, title, ln=True)
        self.set_text_color(*DARK)
        self.ln(1)

    # -- Body text ----------------------------------------------------------
    def body(self, text: str, indent: int = 14):
        self.set_font('Helvetica', '', 9)
        self.set_text_color(*MID)
        self.set_x(indent)
        self.multi_cell(190 - indent + 10, 5, text)
        self.set_text_color(*DARK)
        self.ln(1)

    # -- Bullet -------------------------------------------------------------
    def bullet(self, text: str, indent: int = 18):
        self.set_font('Helvetica', '', 9)
        self.set_text_color(*MID)
        self.set_x(indent)
        self.cell(4, 5, chr(149))
        self.multi_cell(186 - indent + 10, 5, text)
        self.set_text_color(*DARK)

    # -- Key-value row ------------------------------------------------------
    def kv(self, key: str, value: str, fill=False):
        if fill:
            self.set_fill_color(*LIGHT)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(*DARK)
        self.set_x(14)
        self.cell(60, 6, key, fill=fill)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(*MID)
        self.cell(120, 6, value, fill=fill, ln=True)
        self.set_text_color(*DARK)

    # -- Code block ---------------------------------------------------------
    def code(self, lines: list):
        self.set_fill_color(30, 30, 50)
        self.set_text_color(*WHITE)
        self.set_font('Courier', '', 8)
        self.set_x(14)
        for line in lines:
            self.set_x(14)
            self.cell(182, 5, line, fill=True, ln=True)
        self.set_text_color(*DARK)
        self.ln(2)

    # -- Table header -------------------------------------------------------
    def th(self, cols: list, widths: list):
        self.set_fill_color(*DARK)
        self.set_text_color(*WHITE)
        self.set_font('Helvetica', 'B', 8)
        self.set_x(14)
        for col, w in zip(cols, widths):
            self.cell(w, 6, col, border=0, fill=True)
        self.ln()
        self.set_text_color(*DARK)

    # -- Table row ----------------------------------------------------------
    def tr(self, cols: list, widths: list, fill=False):
        if fill:
            self.set_fill_color(*LIGHT)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(*MID)
        self.set_x(14)
        for col, w in zip(cols, widths):
            self.cell(w, 5.5, str(col), border=0, fill=fill)
        self.ln()
        self.set_text_color(*DARK)


def build_cover(pdf: PDF):
    # Full-page dark background
    pdf.set_fill_color(*DARK)
    pdf.rect(0, 0, 210, 297, 'F')

    # Red accent bar
    pdf.set_fill_color(*RED)
    pdf.rect(0, 105, 210, 2, 'F')
    pdf.rect(0, 192, 210, 2, 'F')

    # Title
    pdf.set_text_color(*WHITE)
    pdf.set_font('Helvetica', 'B', 38)
    pdf.set_xy(0, 30)
    pdf.cell(210, 20, 'CardioGuard AI', align='C', ln=True)

    pdf.set_font('Helvetica', '', 18)
    pdf.set_text_color(*RED)
    pdf.set_xy(0, 55)
    pdf.cell(210, 10, 'Hridai Agent OS  -  Technical Documentation', align='C', ln=True)

    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(180, 190, 210)
    pdf.set_xy(0, 72)
    pdf.cell(210, 8, 'Complete Architecture, Training Pipeline & Deployment Guide', align='C', ln=True)

    # Metadata box
    pdf.set_fill_color(40, 40, 65)
    pdf.rect(30, 115, 150, 70, 'F')
    pdf.set_text_color(*WHITE)
    pdf.set_font('Helvetica', '', 9)
    meta = [
        ('Version',     'v4.8 Production'),
        ('Date',        datetime.now().strftime('%B %d, %Y')),
        ('Platform',    'Railway / Cloud Run'),
        ('Domain',      'cardioguardai.in'),
        ('Model',       'Antigravity-22 GBM Classifier'),
        ('Features',    '22 Cardiac Risk Factors'),
        ('Stack',       'Flask  |  scikit-learn  |  SHAP  |  Claude AI'),
        ('Status',      'LIVE  -  Non-Diagnostic Wellness Tool'),
    ]
    y_start = 122
    for k, v in meta:
        pdf.set_xy(35, y_start)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(*RED)
        pdf.cell(42, 7, k + ':')
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(*WHITE)
        pdf.cell(100, 7, v, ln=True)
        y_start += 7

    pdf.set_text_color(140, 150, 170)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_xy(0, 270)
    pdf.cell(210, 6,
        'DISCLAIMER: CardioGuard AI is a non-diagnostic wellness support tool. '
        'Not a medical device. Consult a qualified physician for clinical decisions.',
        align='C', ln=True)

    pdf.set_xy(0, 282)
    pdf.set_font('Helvetica', '', 8)
    pdf.cell(210, 6, 'Confidential  |  cardioguardai.in', align='C')


def build_toc(pdf: PDF):
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(*DARK)
    pdf.set_xy(10, 20)
    pdf.cell(190, 10, 'Table of Contents', ln=True)
    pdf.set_draw_color(*RED)
    pdf.line(10, 31, 200, 31)
    pdf.ln(5)

    toc = [
        ('1', 'Project Overview & Mission'),
        ('2', 'System Architecture'),
        ('3', 'Feature Engineering  -  22 Cardiac Risk Factors'),
        ('4', 'Machine Learning Pipeline'),
        ('5', 'API Reference  -  All Endpoints'),
        ('6', 'Claude AI Integration (Hridai Brain)'),
        ('7', 'WhatsApp Emergency Broadcast Agent'),
        ('8', 'Frontend  -  Patient Portal'),
        ('9', 'Deployment Guide  -  Railway'),
        ('10', 'Security & Rate Limiting'),
        ('11', 'SHAP Explainability Framework'),
        ('12', 'ASHA Worker Integration'),
        ('13', 'Performance Metrics & Validation'),
        ('14', 'Development Roadmap'),
        ('15', 'Legal & Compliance'),
    ]

    for num, title in toc:
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(*DARK)
        pdf.set_x(14)
        pdf.cell(15, 7, num + '.')
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(*MID)
        pdf.cell(160, 7, title, ln=True)
        pdf.set_draw_color(210, 215, 230)
        pdf.line(14, pdf.get_y(), 196, pdf.get_y())


def build_overview(pdf: PDF):
    pdf.add_page()
    pdf.section('1', 'Project Overview & Mission')

    pdf.sub('What is CardioGuard AI?')
    pdf.body(
        'CardioGuard AI (also known as Hridai  -  the Hindi word for heart) is an AI-powered '
        'cardiovascular wellness assessment platform designed for the Indian healthcare context. '
        'It integrates a machine learning risk classifier, a large language model (Claude Sonnet), '
        'and a WhatsApp emergency broadcast agent to deliver real-time cardiac wellness insights '
        'to patients, ASHA workers, and healthcare coordinators.'
    )

    pdf.sub('Mission')
    pdf.body(
        'To democratise early cardiac risk detection for underserved communities in India '
        'by providing a mobile-first, multilingual (Hindi + English) tool that bridges the gap '
        'between rural patients and urban cardiac care infrastructure.'
    )

    pdf.sub('What the Platform Does')
    items = [
        'Accepts 22 patient health parameters via a web form',
        'Runs a trained gradient boosting classifier to compute a cardiac risk score (0-100%)',
        'Classifies risk into OPTIMAL / MODERATE DEVIATION / CRITICAL DEVIATION tiers',
        'Generates SHAP-based explanations identifying the top driving risk factors',
        'Forwards high-risk cases to Claude Sonnet for personalised wellness guidance',
        'Automatically triggers a WhatsApp alert to ASHA workers for critical cases',
        'Provides a batch API for ASHA workers to assess multiple patients simultaneously',
        'Offers a 7-day trend analysis endpoint for the Memory Agent',
    ]
    for item in items:
        pdf.bullet(item)

    pdf.sub('Target Users')
    pdf.kv('Patients',         'Self-assessment via the web portal (cardioguardai.in)')
    pdf.kv('ASHA Workers',     'Priority queue via the /api/batch endpoint')
    pdf.kv('Clinicians',       'Risk factor analysis + SHAP explanations')
    pdf.kv('Healthcare Admins','Aggregated wellness dashboards')
    pdf.kv('Emergency Teams',  'Automated WhatsApp alerts for critical cases')

    pdf.sub('Key Constraints')
    pdf.body(
        'CardioGuard AI is explicitly a non-diagnostic wellness assessment tool. It is NOT '
        'a medical device, does NOT replace clinical diagnosis, and does NOT prescribe treatment. '
        'All outputs carry a mandatory disclaimer. The platform is designed for wellness screening '
        'and early risk stratification, not clinical decision support.'
    )


def build_architecture(pdf: PDF):
    pdf.add_page()
    pdf.section('2', 'System Architecture')

    pdf.sub('High-Level Architecture')
    pdf.body(
        'CardioGuard AI follows a monolithic Flask backend that serves both the static frontend '
        'and all API endpoints. This simplifies Railway deployment and eliminates CORS complexity '
        'for the production domain.'
    )

    pdf.th(['Layer', 'Component', 'Technology', 'Purpose'],
           [28, 50, 45, 67])
    rows = [
        ('Frontend',   'Patient Portal SPA',    'HTML5 + Tailwind CSS', 'Risk assessment form & results'),
        ('Backend',    'Flask Application',     'Python 3.11 + Flask 3', 'API routing + model inference'),
        ('ML Engine',  'Antigravity-22',        'GradientBoostingClassifier', 'Cardiac risk prediction'),
        ('Explainer',  'SHAP TreeExplainer',    'SHAP 0.44+',           'Feature importance per patient'),
        ('AI Brain',   'Claude Sonnet',         'Anthropic API',         'Personalised wellness guidance'),
        ('Messenger',  'WhatsApp Agent',        'Meta Cloud API',        'Emergency ASHA broadcasts'),
        ('Rate Limiter','Flask-Limiter',        'In-memory',             'Abuse prevention'),
        ('Deployment', 'Railway / Gunicorn',    'Railway.app',           'Cloud hosting, autoscale'),
    ]
    for i, row in enumerate(rows):
        pdf.tr(list(row), [28, 50, 45, 67], fill=(i % 2 == 0))

    pdf.ln(4)
    pdf.sub('Request Flow')
    steps = [
        '1. Browser sends POST /api/predict with 22 JSON fields',
        '2. Flask validates all 22 features are present and numeric',
        '3. NumPy array constructed and passed to GBM classifier',
        '4. predict_proba() returns probability of cardiac event',
        '5. Score thresholded: <30% OPTIMAL, 30-70% MODERATE, >=70% CRITICAL',
        '6. SHAP TreeExplainer computes per-feature impact scores',
        '7. If CRITICAL or emergency=true: WhatsApp agent broadcasts alert',
        '8. JSON response returned with score, category, and SHAP factors',
    ]
    for step in steps:
        pdf.bullet(step)

    pdf.sub('File Structure')
    pdf.code([
        'CardioGuard AI/',
        '|-- app.py                  # Production Flask entry point',
        '|-- index.html              # Frontend SPA (served by Flask)',
        '|-- requirements.txt        # Python dependencies',
        '|-- Procfile                # Railway deployment command',
        '|-- README.md               # Project overview',
        '|-- model/',
        '|   +-- antigravity_model.pkl   # Trained GBM classifier',
        '|-- backend/',
        '|   +-- app/',
        '|       +-- services/',
        '|           +-- whatsapp_service.py',
        '|-- frontend-patient/       # React patient portal (dev)',
        '|-- scripts/',
        '|   |-- train_model.py      # Model training pipeline',
        '|   |-- audit_accuracy.py   # Model accuracy audit',
        '|   +-- generate_docs.py    # This documentation generator',
        '+-- docs/',
        '    +-- CardioGuardAI_Technical_Documentation.pdf',
    ])


def build_features(pdf: PDF):
    pdf.add_page()
    pdf.section('3', 'Feature Engineering  -  22 Cardiac Risk Factors')

    pdf.body(
        'The Antigravity-22 model uses exactly 22 clinical and lifestyle features. '
        'These were selected based on the Framingham Heart Study risk factors, '
        'WHO cardiovascular risk assessment guidelines, and the AHA/ACC 2019 '
        'primary prevention guidelines.'
    )

    pdf.sub('Feature Specification')
    pdf.th(['#', 'Feature Name', 'API Key', 'Type', 'Range / Values'],
           [8, 45, 52, 20, 65])
    features = [
        (1,  'Age',                      'age',                          'Int',   '25 - 85 years'),
        (2,  'Sex',                       'sex',                          'Binary','0=Female, 1=Male'),
        (3,  'Cholesterol',               'cholesterol',                  'Float', '120 - 350 mg/dL'),
        (4,  'Blood Pressure',            'blood_pressure',               'Float', '70 - 210 mmHg (systolic)'),
        (5,  'Heart Rate',                'heart_rate',                   'Float', '45 - 130 bpm'),
        (6,  'Diabetes',                  'diabetes',                     'Binary','0=No, 1=Yes'),
        (7,  'Family History',            'family_history',               'Binary','0=No, 1=Yes'),
        (8,  'Smoking',                   'smoking',                      'Binary','0=No, 1=Yes'),
        (9,  'Obesity',                   'obesity',                      'Binary','0=No, 1=Yes (BMI>=30)'),
        (10, 'Alcohol Consumption',       'alcohol_consumption',          'Binary','0=No, 1=Yes'),
        (11, 'Exercise (hrs/week)',        'exercise_hours_per_week',      'Float', '0 - 14 hours'),
        (12, 'Diet Quality',              'diet',                         'Ordinal','0=Unhealthy, 1=Avg, 2=Healthy'),
        (13, 'Previous Heart Problems',   'previous_heart_problems',      'Binary','0=No, 1=Yes'),
        (14, 'Medication Use',            'medication_use',               'Binary','0=No, 1=Yes'),
        (15, 'Stress Level',             'stress_level',                  'Ordinal','1 (low) - 10 (high)'),
        (16, 'Sedentary Hours/day',       'sedentary_hours_per_day',      'Float', '0 - 18 hours'),
        (17, 'BMI',                       'bmi',                          'Float', '15 - 50 kg/m2'),
        (18, 'Triglycerides',             'triglycerides',                'Float', '40 - 500 mg/dL'),
        (19, 'Physical Activity Days',    'physical_activity_days_per_week','Int', '0 - 7 days'),
        (20, 'Sleep Hours/day',           'sleep_hours_per_day',          'Float', '4 - 12 hours'),
        (21, 'Chest Pain',                'chest_pain',                   'Binary','0=No, 1=Yes'),
        (22, 'Blood Sugar',               'blood_sugar',                  'Float', '60 - 350 mg/dL'),
    ]
    for i, row in enumerate(features):
        pdf.tr([str(row[0]), row[1], row[2], row[3], row[4]],
               [8, 45, 52, 20, 65], fill=(i % 2 == 0))

    pdf.ln(3)
    pdf.sub('Clinical Significance of Top Risk Drivers')
    drivers = [
        ('Previous Heart Problems', 'Strongest predictor. Prior MI or angina multiplies future event risk 4-6x (Framingham).'),
        ('Chest Pain',              'Active symptom burden. Typical angina has 90% sensitivity for obstructive CAD.'),
        ('Smoking',                 'Risk multiplier of ~3x. Doubles atherosclerosis progression rate.'),
        ('Diabetes',                '2-4x cardiac risk. Accelerates endothelial dysfunction and atherosclerosis.'),
        ('Age',                     'Linear risk increase. Every 10 years adds ~65% risk in men, ~100% in women post-menopause.'),
        ('Cholesterol',             '>200 mg/dL threshold. LDL drives plaque formation directly.'),
        ('Blood Pressure',          '>140 mmHg systolic classified hypertensive. Each +20 mmHg doubles risk.'),
    ]
    for feat, desc in drivers:
        pdf.set_x(14)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(*RED)
        pdf.cell(60, 5, feat)
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(*MID)
        pdf.multi_cell(120, 5, desc)
        pdf.set_text_color(*DARK)


def build_ml(pdf: PDF):
    pdf.add_page()
    pdf.section('4', 'Machine Learning Pipeline')

    pdf.sub('Model Selection Rationale')
    pdf.body(
        'GradientBoostingClassifier (sklearn) was selected as the Antigravity-22 classifier for the '
        'following reasons: (1) native SHAP TreeExplainer support for per-patient explanations, '
        '(2) strong performance on mixed continuous/binary tabular data, (3) no external '
        'native library dependencies unlike XGBoost (which requires libomp), '
        '(4) pickle-serialisable for production deployment, '
        '(5) proven AUC >0.82 on synthetic cardiac risk datasets.'
    )

    pdf.sub('Training Data')
    pdf.kv('Dataset size',    '10,000 synthetic patient records')
    pdf.kv('Prevalence',      '~25% cardiac event rate (population calibrated)')
    pdf.kv('Generation seed', '42 (deterministic, reproducible)')
    pdf.kv('Basis',           'Framingham Heart Study + WHO CVD + AHA 2019 guidelines')
    pdf.kv('Validation',      '5-fold stratified cross-validation + 80/20 holdout')

    pdf.sub('Hyperparameters')
    pdf.code([
        'GradientBoostingClassifier(',
        '    n_estimators    = 300,        # number of boosting rounds',
        '    max_depth       = 4,          # tree depth (controls overfitting)',
        '    learning_rate   = 0.05,       # shrinkage (slower = better generalisation)',
        '    subsample       = 0.8,        # stochastic gradient boosting',
        '    max_features    = "sqrt",     # feature subsampling per split',
        '    min_samples_leaf= 20,         # minimum leaf size (regularisation)',
        '    random_state    = 42',
        ')',
    ])

    pdf.sub('Synthetic Data Generation Methodology')
    pdf.body(
        'Synthetic data is generated using medically-informed normal and binomial distributions. '
        'The cardiac event outcome is derived from a calibrated logistic function where '
        'each feature\'s coefficient reflects its relative risk from published literature:'
    )
    coefs = [
        ('previous_heart_problems', '+1.80', 'Prior event  -  strongest predictor'),
        ('chest_pain',              '+1.50', 'Symptom burden'),
        ('smoking',                 '+1.10', 'Atherosclerosis acceleration'),
        ('diabetes',                '+1.00', 'Metabolic risk multiplier'),
        ('family_history',          '+0.70', 'Genetic predisposition'),
        ('medication_use',          '+0.40', 'Proxy for existing disease burden'),
        ('sex (male)',              '+0.40', 'Male sex risk advantage disappears post-menopause'),
        ('exercise_hours',          '-0.12', 'Protective  -  cardiorespiratory fitness'),
        ('diet quality',            '-0.30', 'Protective  -  plant-rich diet'),
        ('physical_activity_days',  '-0.10', 'Protective  -  regular movement'),
    ]
    pdf.th(['Feature', 'Log-Odds Weight', 'Clinical Basis'], [60, 35, 95])
    for i, (f, w, b) in enumerate(coefs):
        pdf.tr([f, w, b], [60, 35, 95], fill=(i % 2 == 0))

    pdf.ln(3)
    pdf.sub('Risk Stratification Thresholds')
    pdf.th(['Category', 'Score Range', 'Colour', 'Action'], [50, 35, 30, 75])
    thresholds = [
        ('OPTIMAL',             '0 - 29%',  'Green', 'Monitor. Healthy lifestyle maintenance.'),
        ('MODERATE DEVIATION',  '30 - 69%', 'Amber', 'Doctor consultation recommended.'),
        ('CRITICAL DEVIATION',  '70 - 100%','Red',   'Immediate care. ASHA alert dispatched.'),
    ]
    for i, row in enumerate(thresholds):
        pdf.tr(list(row), [50, 35, 30, 75], fill=(i % 2 == 0))

    pdf.ln(3)
    pdf.sub('Training & Retraining')
    pdf.body('To retrain the model: ')
    pdf.code([
        '# From project root:',
        'python3 scripts/train_model.py',
        '',
        '# Output: model/antigravity_model.pkl',
        '# Reports cross-validation AUC + classification report',
    ])


def build_api(pdf: PDF):
    pdf.add_page()
    pdf.section('5', 'API Reference  -  All Endpoints')

    endpoints = [
        {
            'method': 'GET',
            'path': '/ or /index.html',
            'desc': 'Serves the patient portal frontend SPA.',
            'request': None,
            'response': 'text/html  -  index.html',
        },
        {
            'method': 'GET',
            'path': '/health  or  /api/health',
            'desc': 'System health check. Returns model status, Claude config, version.',
            'request': None,
            'response': '{ "status": "live", "model_loaded": true, "version": "4.5", ... }',
        },
        {
            'method': 'POST',
            'path': '/api/predict',
            'desc': 'Core risk assessment. Rate limited: 10 per minute per IP.',
            'request': '{ "age": 52, "sex": 1, "cholesterol": 220, ... all 22 features }',
            'response': '{ "wellness_score": 67.3, "insight_category": "MODERATE DEVIATION", '
                        '"factor_analysis": { ... SHAP values ... } }',
        },
        {
            'method': 'POST',
            'path': '/api/batch',
            'desc': 'Batch assessment for ASHA worker priority queues. Up to 100 patients.',
            'request': '[ { "age": 55, "sex": 0, ... }, { "age": 62, ... }, ... ]',
            'response': '{ "count": 3, "results": [ { "wellness_score": 74.1, '
                        '"level": "DEVIATION" }, ... ] }',
        },
        {
            'method': 'POST',
            'path': '/api/chat',
            'desc': 'Secure Claude proxy. Rate limited: 5 per minute per IP.',
            'request': '{ "messages": [...], "system": "...", "model": "claude-sonnet-4-6" }',
            'response': 'Direct Anthropic API response (JSON pass-through)',
        },
    ]

    for ep in endpoints:
        color = GREEN if ep['method'] == 'GET' else RED
        pdf.set_fill_color(*color)
        pdf.set_text_color(*WHITE)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_x(14)
        pdf.cell(18, 6, ep['method'], fill=True)
        pdf.set_fill_color(*DARK)
        pdf.set_font('Courier', 'B', 9)
        pdf.cell(80, 6, '  ' + ep['path'], fill=True)
        pdf.ln()

        pdf.set_text_color(*MID)
        pdf.set_font('Helvetica', '', 9)
        pdf.set_x(18)
        pdf.multi_cell(180, 5, ep['desc'])

        if ep['request']:
            pdf.set_x(18)
            pdf.set_font('Helvetica', 'B', 8)
            pdf.set_text_color(*DARK)
            pdf.cell(20, 5, 'Request:')
            pdf.set_font('Courier', '', 7.5)
            pdf.set_text_color(*MID)
            pdf.multi_cell(160, 5, ep['request'])

        pdf.set_x(18)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_text_color(*DARK)
        pdf.cell(20, 5, 'Response:')
        pdf.set_font('Courier', '', 7.5)
        pdf.set_text_color(*MID)
        pdf.multi_cell(160, 5, ep['response'])
        pdf.set_text_color(*DARK)
        pdf.ln(3)

    pdf.sub('Sample cURL  -  Risk Prediction')
    pdf.code([
        'curl -X POST https://cardioguardai.in/api/predict \\',
        '  -H "Content-Type: application/json" \\',
        '  -d \'{',
        '    "age":52,"sex":1,"cholesterol":240,"blood_pressure":145,',
        '    "heart_rate":88,"diabetes":1,"family_history":1,"smoking":0,',
        '    "obesity":1,"alcohol_consumption":0,"exercise_hours_per_week":1.5,',
        '    "diet":1,"previous_heart_problems":0,"medication_use":1,',
        '    "stress_level":7,"sedentary_hours_per_day":9,"bmi":31.2,',
        '    "triglycerides":190,"physical_activity_days_per_week":2,',
        '    "sleep_hours_per_day":5.5,"chest_pain":0,"blood_sugar":128',
        '  }\'',
    ])


def build_claude(pdf: PDF):
    pdf.add_page()
    pdf.section('6', 'Claude AI Integration (Hridai Brain)')

    pdf.body(
        'CardioGuard AI uses Claude Sonnet as its conversational intelligence layer, '
        'referred to as the Hridai Brain. It provides personalised wellness guidance '
        'based on the patient\'s risk score and top contributing factors.'
    )

    pdf.sub('How the Integration Works')
    steps = [
        'The frontend receives the risk score and SHAP factor analysis from /api/predict',
        'It constructs a structured prompt including the patient\'s risk category and top 3 risk factors',
        'The prompt is sent to /api/chat (the secure Claude proxy on the backend)',
        'The backend forwards the request to Anthropic\'s API with ANTHROPIC_API_KEY',
        'Claude Sonnet generates personalised Hindi + English wellness guidance',
        'The guidance is rendered in the patient\'s results panel',
    ]
    for step in steps:
        pdf.bullet(step)

    pdf.sub('Claude Model Configuration')
    pdf.kv('Default Model', 'claude-sonnet-4-6 (latest Sonnet)')
    pdf.kv('Max Tokens',    '1,024 (configurable per request)')
    pdf.kv('Rate Limit',    '5 requests per minute per IP')
    pdf.kv('Timeout',       '30 seconds')
    pdf.kv('API Version',   'anthropic-version: 2023-06-01')

    pdf.sub('System Prompt Strategy')
    pdf.body(
        'The system prompt instructs Claude to act as a compassionate cardiac wellness advisor '
        'for the Indian context. It emphasises: (1) speaking in simple, empathetic language, '
        '(2) providing bilingual Hindi + English guidance, (3) recommending doctor consultation '
        'for moderate/high risk, (4) never providing specific dosage or diagnostic conclusions.'
    )

    pdf.sub('Environment Variable')
    pdf.code([
        '# Required on Railway (set in Variables dashboard):',
        'ANTHROPIC_API_KEY=sk-ant-api03-...',
        '',
        '# Optional  -  override allowed frontend origins:',
        'ALLOWED_ORIGINS=https://cardioguardai.in,https://www.cardioguardai.in',
    ])


def build_whatsapp(pdf: PDF):
    pdf.add_page()
    pdf.section('7', 'WhatsApp Emergency Broadcast Agent')

    pdf.body(
        'The WhatsApp Agent is triggered automatically when a patient\'s risk score '
        'reaches CRITICAL DEVIATION (>=70%) or when the frontend sends emergency=true. '
        'It alerts the assigned ASHA coordinator (Sunita Devi) with the patient name, '
        'score, and risk category.'
    )

    pdf.sub('Trigger Conditions')
    pdf.bullet('wellness_score >= 70 (CRITICAL DEVIATION)')
    pdf.bullet('Request body contains: "emergency": true (manual override)')
    pdf.bullet('Both conditions are checked in the /api/predict handler')

    pdf.sub('Configuration')
    pdf.kv('API Key Env Var', 'WHATSAPP_API_KEY')
    pdf.kv('Mock Mode',       'Active when WHATSAPP_API_KEY is empty or "MOCK"')
    pdf.kv('Live Mode',       'Active when a valid Meta Cloud API key is provided')
    pdf.kv('Message Template','wellness_broadcast (registered with Meta Business)')

    pdf.sub('ASHA Coordinator Integration')
    pdf.body(
        'In production, the WhatsApp alert is sent to the registered ASHA coordinator\'s '
        'mobile number via the Meta Cloud API. The alert includes: patient name, '
        'risk score percentage, risk category, and timestamp. This enables the ASHA worker '
        'to initiate home visits or arrange transport to a primary health centre.'
    )

    pdf.sub('Setting Up Live WhatsApp')
    pdf.code([
        '1. Register a Meta Business account at developers.facebook.com',
        '2. Create a WhatsApp Business App and get an API key',
        '3. Register the "wellness_broadcast" message template',
        '4. Set WHATSAPP_API_KEY in Railway environment variables',
        '5. Update coordinator_mobile in whatsapp_service.py',
    ])


def build_frontend(pdf: PDF):
    pdf.add_page()
    pdf.section('8', 'Frontend  -  Patient Portal')

    pdf.sub('Technology Stack')
    pdf.kv('Deployment mode',  'Static HTML served by Flask (index.html at root)')
    pdf.kv('Styling',          'Tailwind CSS (CDN) + custom CSS animations')
    pdf.kv('JavaScript',       'Vanilla ES6 (no build step required)')
    pdf.kv('Dev version',      'React + Vite (frontend-patient/ directory)')
    pdf.kv('Charting',         'Chart.js for SHAP factor visualisation')
    pdf.kv('Animations',       'CSS keyframes for heartbeat and loading indicators')

    pdf.sub('User Journey')
    steps = [
        'Patient opens cardioguardai.in -> Flask serves index.html',
        'Enters 22 health parameters into the assessment form',
        'Clicks "Assess My Cardiac Wellness" -> POST /api/predict',
        'Risk gauge animates to the computed score (0-100%)',
        'Colour-coded category displayed (green / amber / red)',
        'Top 5 SHAP risk factors shown as an interactive bar chart',
        'Claude AI panel generates personalised Hindi + English guidance',
        'Emergency alert auto-dispatches to ASHA if score >=70%',
        'Patient can share results or start a new assessment',
    ]
    for step in steps:
        pdf.bullet(step)

    pdf.sub('React Dev Portal (frontend-patient/)')
    pdf.body(
        'The frontend-patient/ directory contains a React + Vite development version '
        'of the patient portal. It is built with npm run build, which outputs to dist/. '
        'For production, the compiled index.html is copied to the project root and served '
        'directly by Flask to eliminate a separate static file server.'
    )
    pdf.code([
        'cd frontend-patient',
        'npm install',
        'npm run build       # outputs to dist/',
        'cp dist/index.html ../index.html   # update Flask-served file',
    ])


def build_deployment(pdf: PDF):
    pdf.add_page()
    pdf.section('9', 'Deployment Guide  -  Railway')

    pdf.sub('Railway One-Click Deploy')
    pdf.body(
        'CardioGuard AI is designed for zero-configuration Railway deployment. '
        'Railway auto-detects the Python application via requirements.txt and Procfile.'
    )

    pdf.sub('Step-by-Step Deployment')
    steps = [
        ('1', 'Push code to GitHub repository'),
        ('2', 'Go to railway.app -> New Project -> Deploy from GitHub repo'),
        ('3', 'Railway auto-detects Python + requirements.txt'),
        ('4', 'Set environment variables in Railway Variables dashboard:'),
        ('',  '  ANTHROPIC_API_KEY=sk-ant-api03-...'),
        ('',  '  WHATSAPP_API_KEY=<meta-api-key or leave empty for mock>'),
        ('',  '  ALLOWED_ORIGINS=https://cardioguardai.in,https://www.cardioguardai.in'),
        ('5', 'Railway runs: gunicorn app:app (from Procfile)'),
        ('6', 'Map custom domain cardioguardai.in in Railway Networking settings'),
        ('7', 'Verify deployment at /api/health -> status: "live"'),
    ]
    for num, step in steps:
        pdf.set_x(14)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(*RED if num else DARK)
        pdf.cell(10, 5.5, num)
        pdf.set_font('Helvetica', '' if num else 'I', 9)
        pdf.set_text_color(*DARK)
        pdf.multi_cell(174, 5.5, step)

    pdf.sub('Procfile')
    pdf.code(['web: gunicorn app:app'])

    pdf.sub('Environment Variables Reference')
    pdf.th(['Variable', 'Required', 'Description'], [60, 22, 108])
    env_vars = [
        ('ANTHROPIC_API_KEY', 'Yes', 'Claude API key for AI wellness guidance'),
        ('WHATSAPP_API_KEY',  'No',  'Meta Cloud API key (leave empty for mock mode)'),
        ('ALLOWED_ORIGINS',   'No',  'CORS origins (default: cardioguardai.in domains)'),
        ('PORT',              'Auto','Railway injects this automatically'),
    ]
    for i, row in enumerate(env_vars):
        pdf.tr(list(row), [60, 22, 108], fill=(i % 2 == 0))

    pdf.ln(3)
    pdf.sub('Local Development')
    pdf.code([
        'cd "CardioGuard AI"',
        'python3 -m venv .venv && source .venv/bin/activate',
        'pip install -r requirements.txt',
        'export ANTHROPIC_API_KEY=sk-ant-...',
        'python3 app.py           # starts on port 5005',
        '# Visit: http://localhost:5005',
    ])


def build_security(pdf: PDF):
    pdf.add_page()
    pdf.section('10', 'Security & Rate Limiting')

    pdf.sub('Rate Limiting')
    pdf.kv('Global default',    '200 requests/day, 50 requests/hour per IP')
    pdf.kv('/api/predict',      '10 requests/minute per IP')
    pdf.kv('/api/chat',         '5 requests/minute per IP')
    pdf.kv('Storage backend',   'In-memory (Railway ephemeral  -  resets on restart)')
    pdf.kv('Library',           'flask-limiter 3.5+')

    pdf.sub('CORS Configuration')
    pdf.body(
        'CORS is restricted to the production domain by default. '
        'The ALLOWED_ORIGINS environment variable controls which origins are permitted. '
        'In local development, this can be set to * for convenience.'
    )
    pdf.code([
        'ALLOWED_ORIGINS=https://cardioguardai.in,https://www.cardioguardai.in',
    ])

    pdf.sub('API Key Security')
    pdf.bullet('ANTHROPIC_API_KEY is stored as a Railway secret (never in code)')
    pdf.bullet('WHATSAPP_API_KEY is stored as a Railway secret')
    pdf.bullet('Neither key is ever returned in API responses')
    pdf.bullet('The Claude proxy strips internal metadata before forwarding responses')

    pdf.sub('Input Validation')
    pdf.bullet('All 22 features are required  -  missing fields return HTTP 400')
    pdf.bullet('All feature values are cast to float()  -  non-numeric input returns HTTP 500')
    pdf.bullet('Batch endpoint caps payload at 100 patients maximum')
    pdf.bullet('No SQL or NoSQL database  -  no injection surface')
    pdf.bullet('No file uploads  -  no path traversal surface')


def build_shap(pdf: PDF):
    pdf.add_page()
    pdf.section('11', 'SHAP Explainability Framework')

    pdf.body(
        'SHAP (SHapley Additive exPlanations) is used to provide per-patient explainability '
        'for every risk prediction. This is critical for regulatory compliance and patient trust  -  '
        'patients and ASHA workers need to understand WHY a high-risk score was assigned.'
    )

    pdf.sub('How SHAP Works in CardioGuard AI')
    steps = [
        '1. A SHAP TreeExplainer is initialised with the trained GBM model at startup',
        '2. For each prediction, explainer.shap_values(feature_array) is called',
        '3. Per-feature SHAP values indicate how much each feature pushed the prediction up or down',
        '4. Values are converted to percentage impact scores and sorted by magnitude',
        '5. The top factors are returned in the API response as factor_analysis',
        '6. The frontend renders these as an interactive bar chart (Chart.js)',
    ]
    for step in steps:
        pdf.bullet(step)

    pdf.sub('factor_analysis Response Format')
    pdf.code([
        '"factor_analysis": {',
        '  "Previous Heart Issues": { "impact": 34.2, "direction": "increases" },',
        '  "Cholesterol":           { "impact": 18.7, "direction": "increases" },',
        '  "Exercise":              { "impact": 12.1, "direction": "decreases" },',
        '  "Stress Level":          { "impact":  9.4, "direction": "increases" },',
        '  "BMI":                   { "impact":  7.2, "direction": "increases" },',
        '  ...',
        '}',
    ])

    pdf.sub('SHAP Graceful Degradation')
    pdf.body(
        'SHAP initialisation is wrapped in a try/except. If SHAP is not installed '
        'or the explainer fails (e.g., model format mismatch), the API returns '
        'an empty factor_analysis dict and continues serving predictions normally. '
        'The system never fails hard due to SHAP unavailability.'
    )


def build_asha(pdf: PDF):
    pdf.add_page()
    pdf.section('12', 'ASHA Worker Integration')

    pdf.body(
        'ASHA (Accredited Social Health Activists) are community health workers deployed '
        'across rural India. CardioGuard AI is specifically designed to support ASHA workers '
        'in identifying high-risk patients during community health camps.'
    )

    pdf.sub('Batch Assessment Workflow')
    steps = [
        'ASHA worker collects vitals from 10-50 patients during a health camp',
        'Data entered into the ASHA dashboard (or exported as JSON)',
        'POST /api/batch with array of patient records',
        'System returns risk scores sorted by severity (highest first)',
        'Priority 1 (CRITICAL) patients are flagged for immediate referral',
        'Priority 2 (MODERATE) patients are scheduled for PHC follow-up',
        'Priority 3 (OPTIMAL) patients receive lifestyle guidance pamphlets',
    ]
    for step in steps:
        pdf.bullet(step)

    pdf.sub('Batch Response Format')
    pdf.code([
        'POST /api/batch',
        'Body: [{"patient_id":"P001","age":62,"sex":1,...}, ...]',
        '',
        'Response:',
        '{',
        '  "count": 3,',
        '  "results": [',
        '    {"wellness_score": 78.4, "level": "DEVIATION", ...},',
        '    {"wellness_score": 34.1, "level": "DEVIATION", ...},',
        '    {"wellness_score": 12.2, "level": "OPTIMAL",   ...}',
        '  ]',
        '}',
    ])

    pdf.sub('ASHA Dispatch Thresholds (v4.8)')
    pdf.kv('CRITICAL DEVIATION', 'Score >= 70%  -  immediate WhatsApp alert + home visit')
    pdf.kv('MODERATE DEVIATION', 'Score 30-69%  -  scheduled PHC consultation')
    pdf.kv('OPTIMAL',            'Score < 30%  -  lifestyle guidance + 6-month follow-up')


def build_metrics(pdf: PDF):
    pdf.add_page()
    pdf.section('13', 'Performance Metrics & Validation')

    pdf.sub('Model Performance (Antigravity-22 GBM)')
    pdf.th(['Metric', 'Value', 'Notes'], [55, 30, 105])
    metrics = [
        ('CV AUC (5-fold)',       '>0.82',  'Stratified k-fold cross-validation'),
        ('Holdout Test AUC',      '>0.83',  '20% held-out test set'),
        ('Sensitivity (recall)',  '~0.78',  'True positive rate for cardiac events'),
        ('Specificity',           '~0.80',  'True negative rate for no-event patients'),
        ('Precision',             '~0.62',  'PPV at 0.5 threshold'),
        ('Dataset size',          '10,000', 'Synthetic patients with 25% prevalence'),
        ('Training features',     '22',     'All features required for inference'),
        ('Model type',            'GBM',    'GradientBoostingClassifier (sklearn 1.3+)'),
    ]
    for i, row in enumerate(metrics):
        pdf.tr(list(row), [55, 30, 105], fill=(i % 2 == 0))

    pdf.ln(3)
    pdf.sub('Important Performance Caveats')
    caveats = [
        'These metrics are on SYNTHETIC data  -  real-world performance may differ significantly',
        'The synthetic data distributions are calibrated but not validated against clinical cohorts',
        'A prospective clinical validation study is required before regulatory submission',
        'The model should NOT be used as a clinical diagnostic tool',
        'Regular retraining is recommended as patient demographics shift',
    ]
    for c in caveats:
        pdf.bullet(c)

    pdf.sub('API Latency Targets')
    pdf.kv('/api/predict (no SHAP)',  '< 50 ms  (model inference only)')
    pdf.kv('/api/predict (with SHAP)','< 200 ms (SHAP adds ~150 ms per prediction)')
    pdf.kv('/api/batch (100 patients)','< 2,000 ms (serial inference loop)')
    pdf.kv('/api/chat',               '< 5,000 ms (Anthropic API latency dependent)')


def build_roadmap(pdf: PDF):
    pdf.add_page()
    pdf.section('14', 'Development Roadmap')

    pdf.sub('Phase 1  -  Completed (v4.8)')
    completed = [
        'Flask monolith backend with risk prediction, batch, and Claude proxy endpoints',
        '22-feature cardiac risk classifier with SHAP explainability',
        'WhatsApp emergency broadcast agent integration',
        'Rate limiting and CORS security',
        'Railway deployment with custom domain (cardioguardai.in)',
        'Patient portal frontend with animated risk gauge and SHAP chart',
        'ASHA worker batch assessment endpoint',
        'Hindi + English bilingual Claude wellness guidance',
    ]
    for item in completed:
        pdf.set_x(18)
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(*GREEN)
        pdf.cell(6, 5, 'v')  # checkmark equivalent
        pdf.set_text_color(*MID)
        pdf.multi_cell(174, 5, item)

    pdf.sub('Phase 2  -  Planned')
    planned = [
        'Real-world clinical dataset training (with IRB-approved data partnership)',
        'Women\'s-specific cardiac risk model (female physiology differences)',
        'ECG waveform integration (via wearable sensor data)',
        'Patient health record memory (7-day trend agent)',
        'ASHA mobile app (React Native)',
        'AIIMS / Apollo hospital API integration for referral management',
        'Regional language support (Tamil, Telugu, Bengali, Punjabi)',
        'CDSCO regulatory filing for Software as a Medical Device (SaMD)',
    ]
    for item in planned:
        pdf.bullet(item)


def build_legal(pdf: PDF):
    pdf.add_page()
    pdf.section('15', 'Legal & Compliance')

    pdf.sub('Non-Diagnostic Disclaimer')
    pdf.set_fill_color(255, 240, 240)
    pdf.set_x(14)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(*RED)
    pdf.cell(182, 7, '  IMPORTANT LEGAL NOTICE', fill=True, ln=True)
    pdf.set_fill_color(255, 248, 248)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(*DARK)
    pdf.set_x(14)
    pdf.multi_cell(182, 6,
        'CardioGuard AI is a WELLNESS SUPPORT TOOL, not a medical device. '
        'It does not diagnose, treat, or prescribe. All risk scores are probabilistic estimates '
        'based on synthetic training data and should not be used as the basis for clinical decisions. '
        'Always consult a qualified medical professional for any health concerns.',
        fill=True
    )

    pdf.ln(3)
    pdf.sub('Regulatory Status')
    pdf.kv('Device Classification', 'Non-regulated wellness tool (current)')
    pdf.kv('Future filing target',  'CDSCO SaMD Class B (India)  -  pending clinical validation')
    pdf.kv('Data residency',        'Railway.app (no PII stored  -  all processing in-memory)')
    pdf.kv('DPDP Act (India 2023)', 'No personal health data stored; inference only')

    pdf.sub('Open Source Components')
    components = [
        ('Flask',              'BSD License',   'flask.palletsprojects.com'),
        ('scikit-learn',       'BSD License',   'scikit-learn.org'),
        ('SHAP',               'MIT License',   'github.com/slundberg/shap'),
        ('Anthropic Claude',   'Commercial',    'anthropic.com'),
        ('fpdf2',              'LGPL License',  'github.com/py-pdf/fpdf2'),
        ('Tailwind CSS',       'MIT License',   'tailwindcss.com'),
        ('Chart.js',           'MIT License',   'chartjs.org'),
    ]
    pdf.th(['Component', 'License', 'Source'], [50, 35, 105])
    for i, row in enumerate(components):
        pdf.tr(list(row), [50, 35, 105], fill=(i % 2 == 0))

    pdf.ln(4)
    pdf.sub('Contact & Support')
    pdf.kv('Platform',   'cardioguardai.in')
    pdf.kv('Issues',     'github.com/cardioguard-ai/issues')
    pdf.kv('Version',    'v4.8 Production  -  ' + datetime.now().strftime('%B %Y'))


def build():
    pdf = PDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(left=0, top=0, right=0)

    # Cover page
    pdf.add_page()
    build_cover(pdf)

    # Contents
    build_toc(pdf)
    build_overview(pdf)
    build_architecture(pdf)
    build_features(pdf)
    build_ml(pdf)
    build_api(pdf)
    build_claude(pdf)
    build_whatsapp(pdf)
    build_frontend(pdf)
    build_deployment(pdf)
    build_security(pdf)
    build_shap(pdf)
    build_asha(pdf)
    build_metrics(pdf)
    build_roadmap(pdf)
    build_legal(pdf)

    pdf.output(OUT_PATH)
    size_kb = os.path.getsize(OUT_PATH) / 1024
    print(f"Documentation generated: {OUT_PATH} ({size_kb:.0f} KB)")
    print(f"Total pages: {pdf.page_no()}")


if __name__ == '__main__':
    build()
