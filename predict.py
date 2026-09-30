"""
predict.py — Prediction helper for the AI Hospital Management System
"""
import numpy as np
import joblib
import os

MODEL_PATH   = "model/hospital_rf.pkl"
SCALER_PATH  = "model/scaler.pkl"
FEATURE_COLS = [
    'age', 'gender', 'admission_type', 'diagnosis_code',
    'num_diagnoses', 'num_procedures', 'hba1c', 'creatinine',
    'wbc', 'sodium', 'systolic_bp', 'heart_rate', 'temperature',
    'insurance', 'icu_flag', 'prev_admissions', 'emergency_flag',
]

CLASS_INFO = {
    0: {
        "label":       "Short Stay",
        "days":        "1 – 3 Days",
        "color":       "success",
        "icon":        "fa-circle-check",
        "description": "Patient expected to be discharged within 1–3 days. Routine monitoring recommended.",
    },
    1: {
        "label":       "Medium Stay",
        "days":        "4 – 7 Days",
        "color":       "warning",
        "icon":        "fa-clock",
        "description": "Patient requires moderate inpatient care, 4–7 days. Ensure bed allocation and follow-up planning.",
    },
    2: {
        "label":       "Long Stay",
        "days":        "8+ Days",
        "color":       "danger",
        "icon":        "fa-triangle-exclamation",
        "description": "Extended hospitalisation expected (8+ days). Consider specialist review and resource planning.",
    },
}


def predict_los(patient_data: dict) -> dict:
    """
    Predict LOS class for a single patient record.
    patient_data: dict with keys matching FEATURE_COLS
    Returns dict with prediction details.
    """
    if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
        raise FileNotFoundError("Model not found. Run train_model.py first.")

    model  = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)

    # Build feature vector
    row = np.array([[float(patient_data.get(col, 0)) for col in FEATURE_COLS]],
                   dtype=np.float32)
    row_scaled = scaler.transform(row)

    pred_class   = int(model.predict(row_scaled)[0])
    probabilities = model.predict_proba(row_scaled)[0]

    info = CLASS_INFO[pred_class]

    return {
        "predicted_class":   pred_class,
        "label":             info["label"],
        "days":              info["days"],
        "color":             info["color"],
        "icon":              info["icon"],
        "description":       info["description"],
        "confidence":        round(float(probabilities[pred_class]) * 100, 1),
        "probabilities": {
            "Short":  round(float(probabilities[0]) * 100, 1),
            "Medium": round(float(probabilities[1]) * 100, 1),
            "Long":   round(float(probabilities[2]) * 100, 1),
        },
    }
