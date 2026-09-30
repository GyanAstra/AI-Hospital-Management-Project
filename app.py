"""
app.py — Flask Backend for AI Hospital Management System
Patient Length-of-Stay (LOS) Prediction via Random Forest
"""

import os
import json
import joblib
from flask import Flask, jsonify, render_template, request, send_from_directory
from predict import predict_los, FEATURE_COLS

app = Flask(__name__)

MODEL_PATH  = "model/hospital_rf.pkl"
SCALER_PATH = "model/scaler.pkl"
GRAPH_DIR   = "graphs"


# ────────────────────────────────────────────────────────────
# Routes
# ────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def status():
    model_ready = (
        os.path.exists(MODEL_PATH) and
        os.path.exists(SCALER_PATH)
    )
    metrics = {}
    if os.path.exists("model/metrics.pkl"):
        m = joblib.load("model/metrics.pkl")
        metrics = {
            "accuracy":  f"{m['accuracy']*100:.2f}%",
            "roc_auc":   f"{m['roc_auc']:.4f}",
            "cv_mean":   f"{m['cv_mean']*100:.2f}%",
            "cv_std":    f"±{m['cv_std']*100:.2f}%",
            "n_train":   m['n_train'],
            "n_test":    m['n_test'],
        }
    return jsonify({
        "model_ready":  model_ready,
        "model_type":   "Random Forest Classifier (200 estimators)",
        "task":         "Patient Length-of-Stay Prediction",
        "feature_cols": FEATURE_COLS,
        "metrics":      metrics,
    })


@app.route("/api/predict", methods=["POST"])
def api_predict():
    """
    Expects JSON with patient feature keys matching FEATURE_COLS.
    Returns predicted LOS class with probabilities and descriptions.
    """
    try:
        body = request.get_json(force=True)

        patient = {
            "age":             float(body.get("age",             45)),
            "gender":          float(body.get("gender",           1)),
            "admission_type":  float(body.get("admission_type",   0)),
            "diagnosis_code":  float(body.get("diagnosis_code",   0)),
            "num_diagnoses":   float(body.get("num_diagnoses",    3)),
            "num_procedures":  float(body.get("num_procedures",   2)),
            "hba1c":           float(body.get("hba1c",           6.5)),
            "creatinine":      float(body.get("creatinine",      1.0)),
            "wbc":             float(body.get("wbc",             9.0)),
            "sodium":          float(body.get("sodium",         138.0)),
            "systolic_bp":     float(body.get("systolic_bp",    128)),
            "heart_rate":      float(body.get("heart_rate",      82)),
            "temperature":     float(body.get("temperature",    37.2)),
            "insurance":       float(body.get("insurance",        0)),
            "icu_flag":        float(body.get("icu_flag",         0)),
            "prev_admissions": float(body.get("prev_admissions",  0)),
            "emergency_flag":  float(body.get("emergency_flag",   0)),
        }

        result = predict_los(patient)
        return jsonify({"success": True, "result": result})

    except FileNotFoundError:
        return jsonify({
            "success": False,
            "error": "Model not found. Run train_model.py first.",
        }), 503
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route("/graphs/<path:filename>")
def serve_graphs(filename):
    return send_from_directory(os.path.abspath(GRAPH_DIR), filename)


@app.route("/predict", methods=["POST"])
def predict_alias():
    return api_predict()


@app.route("/health")
def health():
    return status()


if __name__ == "__main__":
    print("\n[*] AI Hospital Management System — LOS Prediction Server")
    print("   Model  : Random Forest Classifier")
    print("   Task   : Patient Length-of-Stay Prediction")
    print("   URL    : http://127.0.0.1:5000")
    print("   Press CTRL+C to quit\n")
    app.run(debug=True, port=5000)
