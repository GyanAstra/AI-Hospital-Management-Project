"""
AI Hospital Management System
==============================
generate_dataset.py — Generates a realistic synthetic hospital dataset
based on real-world distributions (MIMIC-III / CMS Inpatient datasets).

Run this FIRST before train_model.py.
"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)

N = 10000  # 10,000 patient records

print("=" * 60)
print("  AI Hospital Management System")
print("  Generating Realistic Patient Dataset...")
print("=" * 60)

# ── Age distribution (realistic hospital population) ──────────
age = np.concatenate([
    np.random.normal(loc=35, scale=10, size=int(N * 0.25)).clip(18, 55),
    np.random.normal(loc=62, scale=12, size=int(N * 0.50)).clip(50, 90),
    np.random.normal(loc=78, scale=8,  size=int(N * 0.25)).clip(60, 99),
])
np.random.shuffle(age)
age = age[:N].astype(int)

# ── Gender ────────────────────────────────────────────────────
gender = np.random.choice([0, 1], size=N, p=[0.47, 0.53])   # 0=Female, 1=Male

# ── Admission type ────────────────────────────────────────────
# 0=Emergency, 1=Urgent, 2=Elective
admission_type = np.random.choice([0, 1, 2], size=N, p=[0.45, 0.30, 0.25])

# ── Primary Diagnosis (ICD grouped) ──────────────────────────
# 0=Cardiac, 1=Respiratory, 2=Orthopedic, 3=GI, 4=Neurological, 5=Infection
diagnosis = np.random.choice([0, 1, 2, 3, 4, 5], size=N,
                              p=[0.22, 0.18, 0.15, 0.17, 0.14, 0.14])

# ── Number of diagnoses (comorbidities) ──────────────────────
num_diagnoses = np.random.poisson(lam=3, size=N).clip(1, 12)

# ── Number of procedures ─────────────────────────────────────
num_procedures = np.random.poisson(lam=2, size=N).clip(0, 10)

# ── Lab values (on admission) ─────────────────────────────────
# HBA1C (glycated haemoglobin, %)
hba1c = np.random.normal(loc=6.5, scale=1.8, size=N).clip(4.0, 14.0).round(1)

# Creatinine (kidney function, mg/dL)
creatinine = np.random.lognormal(mean=0.15, sigma=0.45, size=N).clip(0.4, 8.0).round(2)

# White Blood Cell count (x10^9/L)
wbc = np.random.normal(loc=9.0, scale=3.5, size=N).clip(1.5, 30.0).round(1)

# Sodium (mEq/L)
sodium = np.random.normal(loc=138, scale=4, size=N).clip(120, 158).round(1)

# ── Vital signs on admission ──────────────────────────────────
# Systolic BP (mmHg)
systolic_bp = np.random.normal(loc=128, scale=20, size=N).clip(80, 200).round(0).astype(int)

# Heart rate (bpm)
heart_rate = np.random.normal(loc=82, scale=15, size=N).clip(40, 160).round(0).astype(int)

# Temperature (°C)
temperature = np.random.normal(loc=37.2, scale=0.8, size=N).clip(35.0, 40.5).round(1)

# ── Insurance / Payer ─────────────────────────────────────────
# 0=Medicare, 1=Medicaid, 2=Private, 3=Self-pay
insurance = np.random.choice([0, 1, 2, 3], size=N, p=[0.38, 0.22, 0.32, 0.08])

# ── ICU Flag ─────────────────────────────────────────────────
icu_flag = np.random.choice([0, 1], size=N, p=[0.75, 0.25])

# ── Previous admissions (in last 1 year) ─────────────────────
prev_admissions = np.random.poisson(lam=1.2, size=N).clip(0, 8)

# ── Emergency flag ────────────────────────────────────────────
emergency_flag = (admission_type == 0).astype(int)

# ════════════════════════════════════════════════════════════
# TARGET: Length of Stay (LOS) in days  — clinically realistic
# Based on: AHRQ HCUP mean LOS distributions per diagnosis
# ════════════════════════════════════════════════════════════
base_los = {
    0: 3.5,   # Cardiac       — national mean ~3.5d
    1: 2.8,   # Respiratory   — national mean ~2.8d
    2: 2.4,   # Orthopedic    — national mean ~2.4d
    3: 2.6,   # GI            — national mean ~2.6d
    4: 3.8,   # Neurological  — national mean ~3.8d
    5: 4.2,   # Infection     — national mean ~4.2d
}

los = np.array([base_los[d] for d in diagnosis], dtype=float)

# Adjust for clinical factors (smaller coefficients for realistic LOS range)
los += (age - 50) * 0.012                 # deviation from median age
los += icu_flag * 2.2                     # ICU → longer
los += emergency_flag * 0.5              # emergency → slightly longer
los += (admission_type == 2) * (-0.6)    # elective → shorter
los += num_diagnoses * 0.18              # comorbidities → longer
los += num_procedures * 0.12            # more procedures → longer
los += (creatinine > 2.0) * 0.9         # kidney issues → longer
los += (wbc > 12.0) * 0.5               # infection marker
los += prev_admissions * 0.10           # frequent flyer
los += np.random.normal(0, 1.2, N)       # random noise

los = los.clip(1, 25).round(1)

# ── LOS Classification (3-class) ─────────────────────────────
# Short   : 1–3  days
# Medium  : 4–7  days
# Long    : 8+   days
def classify_los(l):
    if l <= 3:   return 0   # Short
    if l <= 7:   return 1   # Medium
    return 2                # Long

los_class = np.array([classify_los(l) for l in los])

# ════════════════════════════════════════════════════════════
# Build DataFrame
# ════════════════════════════════════════════════════════════
DIAG_MAP = {0:'Cardiac', 1:'Respiratory', 2:'Orthopedic', 3:'GI', 4:'Neurological', 5:'Infection'}
INS_MAP  = {0:'Medicare', 1:'Medicaid', 2:'Private', 3:'Self-Pay'}
ADM_MAP  = {0:'Emergency', 1:'Urgent', 2:'Elective'}

df = pd.DataFrame({
    'age':               age,
    'gender':            gender,
    'admission_type':    admission_type,
    'admission_type_label': [ADM_MAP[a] for a in admission_type],
    'diagnosis_code':    diagnosis,
    'diagnosis_label':   [DIAG_MAP[d] for d in diagnosis],
    'num_diagnoses':     num_diagnoses,
    'num_procedures':    num_procedures,
    'hba1c':             hba1c,
    'creatinine':        creatinine,
    'wbc':               wbc,
    'sodium':            sodium,
    'systolic_bp':       systolic_bp,
    'heart_rate':        heart_rate,
    'temperature':       temperature,
    'insurance':         insurance,
    'insurance_label':   [INS_MAP[i] for i in insurance],
    'icu_flag':          icu_flag,
    'prev_admissions':   prev_admissions,
    'emergency_flag':    emergency_flag,
    'los_days':          los,
    'los_class':         los_class,
})

os.makedirs('dataset', exist_ok=True)
df.to_csv('dataset/hospital_patients.csv', index=False)

print(f"\n[OK] Generated {N:,} patient records.")
print(f"\n   LOS Class Distribution:")
labels = {0:'Short (1-3 days)', 1:'Medium (4-7 days)', 2:'Long (8+ days)'}
for k, v in df['los_class'].value_counts().sort_index().items():
    print(f"   {labels[k]:25s}: {v:,}  ({v/N*100:.1f}%)")
print(f"\n   Mean LOS: {los.mean():.2f} days | Median: {np.median(los):.2f} days")
print(f"\n   Saved -> dataset/hospital_patients.csv")
print("=" * 60)
