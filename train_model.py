"""
AI Hospital Management System
==============================
train_model.py — Trains Random Forest model to predict Patient Length of Stay (LOS)
Dataset: Synthetic hospital patient data (10,000 records, real-world distributions)

Run: python generate_dataset.py FIRST, then python train_model.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (classification_report, confusion_matrix,
                              accuracy_score, roc_auc_score)
from sklearn.inspection import permutation_importance

# ── Reproducibility ───────────────────────────────────────────
np.random.seed(42)

FEATURE_COLS = [
    'age', 'gender', 'admission_type', 'diagnosis_code',
    'num_diagnoses', 'num_procedures', 'hba1c', 'creatinine',
    'wbc', 'sodium', 'systolic_bp', 'heart_rate', 'temperature',
    'insurance', 'icu_flag', 'prev_admissions', 'emergency_flag',
]

CLASS_NAMES = ['Short\n(1-3d)', 'Medium\n(4-7d)', 'Long\n(8+d)']
CLASS_LABELS = ['Short', 'Medium', 'Long']

print("=" * 60)
print("  AI Hospital Management System")
print("  Model Training: Patient LOS Prediction")
print("=" * 60)

# ════════════════════════════════════════════════════════════
# 1. Load Dataset
# ════════════════════════════════════════════════════════════
print("\n[1/6] Loading dataset ...")

CSV_PATH = "dataset/hospital_patients.csv"
if not os.path.exists(CSV_PATH):
    print("   [ERROR] Dataset not found. Run generate_dataset.py first!")
    exit(1)

df = pd.read_csv(CSV_PATH)
print(f"   Loaded: {df.shape[0]:,} rows x {df.shape[1]} columns")

X = df[FEATURE_COLS].values.astype(np.float32)
y = df['los_class'].values.astype(int)

print(f"\n   Class distribution:")
labels = {0:'Short (1-3d)', 1:'Medium (4-7d)', 2:'Long (8+d)'}
for k in [0, 1, 2]:
    count = (y == k).sum()
    print(f"   {labels[k]:18s}: {count:,}  ({count/len(y)*100:.1f}%)")

# ════════════════════════════════════════════════════════════
# 2. Scale Features
# ════════════════════════════════════════════════════════════
print("\n[2/6] Scaling features ...")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

os.makedirs("model", exist_ok=True)
joblib.dump(scaler, "model/scaler.pkl")
joblib.dump(FEATURE_COLS, "model/feature_cols.pkl")
print("   Scaler saved -> model/scaler.pkl")

# ════════════════════════════════════════════════════════════
# 3. Train / Test Split
# ════════════════════════════════════════════════════════════
print("\n[3/6] Splitting data ...")

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.20, random_state=42, stratify=y
)
print(f"   Train: {X_train.shape[0]:,}  |  Test: {X_test.shape[0]:,}")

# ════════════════════════════════════════════════════════════
# 4. Build & Train Random Forest
# ════════════════════════════════════════════════════════════
print("\n[4/6] Training Random Forest model ...")

rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=12,
    min_samples_split=4,
    min_samples_leaf=2,
    max_features='sqrt',
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)

rf.fit(X_train, y_train)
print("   Training complete!")

# Cross-validation
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(rf, X_scaled, y, cv=cv, scoring='accuracy', n_jobs=-1)
print(f"   5-Fold CV Accuracy: {cv_scores.mean()*100:.2f}% ± {cv_scores.std()*100:.2f}%")

# Save model
joblib.dump(rf, "model/hospital_rf.pkl")
print("   Model saved -> model/hospital_rf.pkl")

# ════════════════════════════════════════════════════════════
# 5. Evaluate
# ════════════════════════════════════════════════════════════
print("\n[5/6] Evaluating ...")

y_pred      = rf.predict(X_test)
y_pred_prob = rf.predict_proba(X_test)
acc         = accuracy_score(y_test, y_pred)
auc         = roc_auc_score(y_test, y_pred_prob, multi_class='ovr', average='macro')

print(f"\n   Test Accuracy  : {acc*100:.2f}%")
print(f"   Macro ROC-AUC  : {auc:.4f}")
print("\n   Classification Report:")
print(classification_report(y_test, y_pred,
      labels=[0,1,2], target_names=CLASS_LABELS, zero_division=0))

# Save metrics
metrics = {
    'accuracy': round(acc, 4),
    'roc_auc':  round(auc, 4),
    'cv_mean':  round(cv_scores.mean(), 4),
    'cv_std':   round(cv_scores.std(), 4),
    'n_train':  X_train.shape[0],
    'n_test':   X_test.shape[0],
}
joblib.dump(metrics, "model/metrics.pkl")

# ════════════════════════════════════════════════════════════
# 6. Evaluation Graphs
# ════════════════════════════════════════════════════════════
print("\n[6/6] Generating evaluation graphs ...")

os.makedirs("graphs", exist_ok=True)
DARK_BG = "#0f172a"
plt.style.use("dark_background")

# ── Confusion Matrix ─────────────────────────────────────────
cm = confusion_matrix(y_test, y_pred)
fig, ax = plt.subplots(figsize=(8, 6), facecolor=DARK_BG)
ax.set_facecolor(DARK_BG)
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=CLASS_LABELS, yticklabels=CLASS_LABELS,
            ax=ax, linewidths=0.5, linecolor="#1e293b",
            annot_kws={"size": 15, "color": "white"}, cbar_kws={"shrink": 0.8})
ax.set_title("Confusion Matrix — LOS Prediction", fontsize=15, color="white", pad=12)
ax.set_xlabel("Predicted Class", color="#94a3b8", fontsize=12)
ax.set_ylabel("Actual Class",    color="#94a3b8", fontsize=12)
ax.tick_params(colors="#94a3b8")
plt.tight_layout()
plt.savefig("graphs/confusion_matrix.png", dpi=150, bbox_inches="tight")
plt.close()

# ── Feature Importance ────────────────────────────────────────
importances = rf.feature_importances_
feat_df = pd.DataFrame({'feature': FEATURE_COLS, 'importance': importances})
feat_df = feat_df.sort_values('importance', ascending=True).tail(15)

FEATURE_DISPLAY = {
    'age': 'Age', 'gender': 'Gender', 'admission_type': 'Admission Type',
    'diagnosis_code': 'Diagnosis Code', 'num_diagnoses': 'No. of Diagnoses',
    'num_procedures': 'No. of Procedures', 'hba1c': 'HbA1c (%)',
    'creatinine': 'Creatinine', 'wbc': 'WBC Count', 'sodium': 'Sodium',
    'systolic_bp': 'Systolic BP', 'heart_rate': 'Heart Rate',
    'temperature': 'Temperature', 'insurance': 'Insurance Type',
    'icu_flag': 'ICU Admission', 'prev_admissions': 'Prior Admissions',
    'emergency_flag': 'Emergency Flag'
}
feat_df['display'] = feat_df['feature'].map(lambda x: FEATURE_DISPLAY.get(x, x))

fig, ax = plt.subplots(figsize=(10, 7), facecolor=DARK_BG)
ax.set_facecolor(DARK_BG)
colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(feat_df)))
bars = ax.barh(feat_df['display'], feat_df['importance'], color=colors, edgecolor='#1e293b')
ax.set_title("Feature Importance — Random Forest", fontsize=15, color="white", pad=12)
ax.set_xlabel("Mean Decrease in Impurity", color="#94a3b8")
ax.tick_params(colors="#94a3b8", axis='both')
for sp in ax.spines.values(): sp.set_edgecolor("#1e293b")
ax.grid(axis='x', alpha=0.15)
plt.tight_layout()
plt.savefig("graphs/feature_importance.png", dpi=150, bbox_inches="tight")
plt.close()

# ── CV Score Distribution ─────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5), facecolor=DARK_BG)
ax.set_facecolor(DARK_BG)
folds = [f"Fold {i+1}" for i in range(5)]
colors_cv = ['#38bdf8', '#a78bfa', '#34d399', '#f472b6', '#fb923c']
bars = ax.bar(folds, cv_scores * 100, color=colors_cv, edgecolor='#1e293b', width=0.5)
for bar, val in zip(bars, cv_scores):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f"{val*100:.1f}%", ha='center', va='bottom', color='white', fontsize=10)
ax.axhline(cv_scores.mean() * 100, color='#fbbf24', linestyle='--', lw=2, label=f'Mean = {cv_scores.mean()*100:.2f}%')
ax.set_title("5-Fold Cross-Validation Accuracy", fontsize=15, color="white", pad=12)
ax.set_ylabel("Accuracy (%)", color="#94a3b8")
ax.tick_params(colors="#94a3b8")
ax.legend(framealpha=0.15, labelcolor='white')
ax.set_ylim([max(0, cv_scores.min()*100 - 3), min(100, cv_scores.max()*100 + 4)])
for sp in ax.spines.values(): sp.set_edgecolor("#1e293b")
ax.grid(axis='y', alpha=0.15)
plt.tight_layout()
plt.savefig("graphs/cv_scores.png", dpi=150, bbox_inches="tight")
plt.close()

# ── LOS Distribution by Class ─────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(12, 5), facecolor=DARK_BG)
fig.suptitle("Patient LOS Distribution by Class", fontsize=15, color='white', y=1.01)
palette = ['#38bdf8', '#a78bfa', '#f472b6']
class_names_full = ['Short (1–3 days)', 'Medium (4–7 days)', 'Long (8+ days)']
for i, (ax, name, clr) in enumerate(zip(axes, class_names_full, palette)):
    subset = df[df['los_class'] == i]['los_days']
    ax.set_facecolor(DARK_BG)
    ax.hist(subset, bins=20, color=clr, edgecolor='#1e293b', alpha=0.85)
    ax.set_title(name, color='white', fontsize=11, pad=8)
    ax.set_xlabel("LOS (days)", color="#94a3b8", fontsize=9)
    ax.set_ylabel("Count", color="#94a3b8", fontsize=9)
    ax.tick_params(colors="#94a3b8")
    for sp in ax.spines.values(): sp.set_edgecolor("#1e293b")
    ax.grid(alpha=0.12)
    ax.text(0.97, 0.95, f"n={len(subset):,}", transform=ax.transAxes,
            ha='right', va='top', color='white', fontsize=9)
plt.tight_layout()
plt.savefig("graphs/los_distribution.png", dpi=150, bbox_inches="tight")
plt.close()

# ── Diagnosis vs Avg LOS ──────────────────────────────────────
DIAG_NAMES = ['Cardiac', 'Respiratory', 'Orthopedic', 'GI', 'Neurological', 'Infection']
avg_los_diag = [df[df['diagnosis_code'] == i]['los_days'].mean() for i in range(6)]
fig, ax = plt.subplots(figsize=(10, 5), facecolor=DARK_BG)
ax.set_facecolor(DARK_BG)
clrs = plt.cm.cool(np.linspace(0.2, 0.9, 6))
bars = ax.bar(DIAG_NAMES, avg_los_diag, color=clrs, edgecolor='#1e293b', width=0.55)
for bar, val in zip(bars, avg_los_diag):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
            f"{val:.1f}d", ha='center', va='bottom', color='white', fontsize=10)
ax.set_title("Average LOS by Diagnosis Category", fontsize=15, color='white', pad=12)
ax.set_ylabel("Average LOS (days)", color="#94a3b8")
ax.tick_params(colors="#94a3b8")
for sp in ax.spines.values(): sp.set_edgecolor("#1e293b")
ax.grid(axis='y', alpha=0.15)
plt.tight_layout()
plt.savefig("graphs/avg_los_by_diagnosis.png", dpi=150, bbox_inches="tight")
plt.close()

print("   Saved: graphs/confusion_matrix.png")
print("   Saved: graphs/feature_importance.png")
print("   Saved: graphs/cv_scores.png")
print("   Saved: graphs/los_distribution.png")
print("   Saved: graphs/avg_los_by_diagnosis.png")

print("\n" + "=" * 60)
print(f"  [OK] Training complete!")
print(f"       Accuracy : {acc*100:.2f}%  |  AUC : {auc:.4f}")
print(f"       Run: python app.py")
print("=" * 60)
