# AI Hospital Management System
### Patient Length-of-Stay Prediction using Random Forest
**GyanAstra Technologies** · AI with Python Programme · September 2026

---

## Overview
An end-to-end Machine Learning system that predicts **Patient Length of Stay (LOS)** at the point of hospital admission using a **Random Forest ensemble classifier** trained on 10,000 realistic clinical patient records.

**LOS Classes:**
| Class | Range | Description |
|-------|-------|-------------|
| 🟢 Short | 1–3 days | Minor procedures, mild acute illness |
| 🟡 Medium | 4–7 days | Standard inpatient admission |
| 🔴 Long | 8+ days | Complex, ICU, multi-organ, post-surgical |

---

## Project Structure
```
AI-Hospital-Management-System/
├── generate_dataset.py         # Step 1: Generate 10,000 patient records
├── train_model.py              # Step 2: Train Random Forest + generate graphs
├── predict.py                  # Inference helper module
├── app.py                      # Step 3: Flask web server
├── build_hospital_report_docx.py  # Generate GyanAstra .docx report
├── requirements.txt
├── dataset/
│   └── hospital_patients.csv   # Generated dataset (10,000 records)
├── model/
│   ├── hospital_rf.pkl         # Trained Random Forest (200 trees)
│   ├── scaler.pkl              # StandardScaler
│   └── metrics.pkl             # Evaluation metrics dict
├── graphs/                     # 5 evaluation graphs (PNG)
├── templates/
│   └── index.html              # Premium web dashboard
└── report/
    └── AI_Hospital_Management_System_Report.docx
```

---

## How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Dataset
```bash
python generate_dataset.py
```
Generates `dataset/hospital_patients.csv` with 10,000 realistic clinical records.

### 3. Train the Model
```bash
python train_model.py
```
Trains Random Forest, runs 5-fold CV, saves model artifacts, generates 5 evaluation graphs.

### 4. Launch Web App
```bash
python app.py
```
Open `http://127.0.0.1:5000` in your browser.

### 5. Generate Report
```bash
python build_hospital_report_docx.py
```
Outputs `report/AI_Hospital_Management_System_Report.docx` — full GyanAstra IEEE report.

---

## Features
- **17 Clinical Features**: Age, Gender, Admission Type, Diagnosis, Comorbidities, HbA1c, Creatinine, WBC, Sodium, BP, Heart Rate, Temperature, Insurance, ICU, Prior Admissions, Emergency Flag
- **Random Forest**: 200 trees, class-balanced, 12-depth, 5-fold Stratified CV
- **Macro ROC-AUC**: ~0.81+
- **REST API**: `POST /api/predict` with JSON patient record
- **Premium UI**: Dark GyanAstra teal theme, animated probability bars, 5 graph tabs

---

## Tech Stack
| Layer | Technology |
|-------|-----------|
| ML | Scikit-learn (Random Forest) |
| Data | Pandas, NumPy |
| Graphs | Matplotlib, Seaborn |
| Backend | Flask 3.0 |
| Frontend | HTML5, CSS3, JavaScript |
| Report | python-docx |

---

*Developed under the mentorship of **GyanAstra Technologies***  
*"Empowering Intelligence, Delivering Innovation"*
