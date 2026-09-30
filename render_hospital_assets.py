"""
render_hospital_assets.py
==========================
Generates high-resolution publication-quality assets for the AI Hospital Management System:
1. Rendered LaTeX mathematical equations (equations/)
2. End-to-end Architectural Block Diagram (graphs/block_diagram.png)
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ── 1. RENDER MATHEMATICAL EQUATIONS ───────────────────────────────────────────
def render_equation(latex_str, filename, fontsize=18, dpi=300):
    fig = plt.figure(figsize=(0.1, 0.1), dpi=dpi)
    text = fig.text(0, 0, latex_str, fontsize=fontsize, usetex=False,
                    color="#0A3641", fontfamily="sans-serif")
    
    fig.patch.set_alpha(0.0)
    plt.axis("off")
    fig.canvas.draw()
    bbox = text.get_window_extent(fig.canvas.get_renderer())
    bbox_inches = bbox.transformed(fig.dpi_scale_trans.inverted())
    
    pad = 0.08
    bbox_expanded = matplotlib.transforms.Bbox.from_bounds(
        bbox_inches.x0 - pad, bbox_inches.y0 - pad,
        bbox_inches.width + 2*pad, bbox_inches.height + 2*pad
    )
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.savefig(filename, dpi=dpi, bbox_inches=bbox_expanded, transparent=True)
    plt.close()
    print(f"[OK] Rendered Equation -> {filename}")


def generate_all_equations():
    equations = [
        (r"$z = \frac{x - \mu}{\sigma}$", "graphs/equations/eq_zscore.png", 18),
        (r"$I_G(t) = 1 - \sum_{i=1}^{C} p(i \mid t)^2$", "graphs/equations/eq_gini.png", 18),
        (r"$\hat{y} = \arg\max_{c \in \{1,\dots,C\}} \frac{1}{B} \sum_{b=1}^{B} I\left(T_b(x) = c\right)$", "graphs/equations/eq_ensemble.png", 17),
        (r"$P(y = c \mid x) = \frac{1}{B} \sum_{b=1}^{B} P_b(y = c \mid x)$", "graphs/equations/eq_prob.png", 18),
        (r"$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$", "graphs/equations/eq_accuracy.png", 18),
        (r"$\text{Macro F1} = \frac{1}{C} \sum_{c=1}^{C} \frac{2 \cdot P_c \cdot R_c}{P_c + R_c}$", "graphs/equations/eq_f1.png", 18),
        (r"$\text{Macro ROC-AUC} = \frac{1}{C} \sum_{c=1}^{C} \int_{0}^{1} \text{TPR}_c(t) \, d(\text{FPR}_c(t))$", "graphs/equations/eq_roc_auc.png", 17),
    ]
    for latex, path, fs in equations:
        render_equation(latex, path, fontsize=fs)


# ── 2. RENDER ARCHITECTURAL BLOCK DIAGRAM ──────────────────────────────────────
def generate_block_diagram():
    fig, ax = plt.subplots(figsize=(11, 14), dpi=300)
    fig.patch.set_facecolor("#FAFDFD")
    ax.set_facecolor("#FAFDFD")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Colors
    c_navy      = "#0A3641"   # GyanAstra Dark Teal
    c_teal      = "#01AAB1"   # GyanAstra Primary Teal
    c_accent    = "#008C95"   # GyanAstra Accent Teal
    c_card_edge = "#BFE7EA"
    c_shadow    = "#D8EDED"
    c_card_bg   = "#FFFFFF"
    c_text_main = "#1F2937"
    c_text_sub  = "#4B5563"

    # Title Banner
    ax.text(50, 97.2, "AI-POWERED HOSPITAL MANAGEMENT SYSTEM",
            ha="center", va="center", fontsize=15.5, weight="bold", color=c_navy, fontfamily="sans-serif")
    ax.text(50, 95.0, "Clinical Dataflow & Random Forest Patient Length-of-Stay Architecture · GyanAstra Technologies",
            ha="center", va="center", fontsize=9.5, color=c_accent, weight="bold", fontfamily="sans-serif")

    def draw_card(x, y, w, h, title, lines, icon="◈", badge=None, border_color=c_teal, bg_color="#FFFFFF"):
        # Shadow
        shadow = patches.FancyBboxPatch(
            (x + 0.4, y - 0.4), w, h,
            boxstyle="round,pad=0.6,rounding_size=1.2",
            facecolor=c_shadow, edgecolor="none", zorder=1
        )
        ax.add_patch(shadow)

        # Main Box
        card = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.6,rounding_size=1.2",
            facecolor=bg_color, edgecolor=border_color, linewidth=1.5, zorder=2
        )
        ax.add_patch(card)

        # Header Pill
        header_y = y + h - 1.8
        ax.text(x + 2, header_y, f"{icon}  {title}",
                ha="left", va="center", fontsize=10.5, weight="bold", color=c_navy, zorder=3, fontfamily="sans-serif")
        
        if badge:
            badge_box = patches.FancyBboxPatch(
                (x + w - 17, y + h - 2.8), 15, 2.0,
                boxstyle="round,pad=0.2,rounding_size=0.6",
                facecolor="#E8F7F8", edgecolor=c_accent, linewidth=0.8, zorder=3
            )
            ax.add_patch(badge_box)
            ax.text(x + w - 9.5, y + h - 1.8, badge,
                    ha="center", va="center", fontsize=7.5, weight="bold", color=c_navy, zorder=4)

        # Divider line
        ax.plot([x + 1.5, x + w - 1.5], [y + h - 3.2, y + h - 3.2],
                color=c_card_edge, linewidth=0.8, zorder=3)

        # Text Lines
        line_y = y + h - 5.0
        for l in lines:
            ax.text(x + 2.5, line_y, l,
                    ha="left", va="center", fontsize=8.2, color=c_text_sub, zorder=3, fontfamily="sans-serif")
            line_y -= 1.8

    def draw_arrow(x1, y1, x2, y2, label=None):
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle="-|>", color=c_accent, lw=1.8,
                mutation_scale=14, shrinkA=0, shrinkB=0
            ),
            zorder=5
        )
        if label:
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            ax.text(mid_x + 1.5, mid_y, label,
                    ha="left", va="center", fontsize=7.5, color=c_accent,
                    weight="bold", zorder=6,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="#FAFDFD", edgecolor="none"))

    # Tier 1: Clinical Telemetry & Preprocessing (y: 80 - 92)
    draw_card(
        5, 81.5, 90, 11.5,
        "TIER 1: CLINICAL DATA INGESTION & MEDICAL FEATURE EXTRACTION",
        [
            "• Patient Electronic Health Records (EHR): 10,000 synthetic clinical records reflecting diverse inpatient stays",
            "• Demographics & Admission Dynamics: Age (18-95), Gender, Admission Urgency (Emergency, Urgent, Elective)",
            "• Clinical Diagnostics & Comorbidities: Primary Diagnosis Code, Charlson Comorbidity Index (0-8), Vital Risk Score",
            "• Facility Resource Demands: Pre-admission Procedure Count, Department Ward (General, ICU, Surgical, Telemetry)",
            "• Data Cleaning & Preprocessing: Missing value imputation, outlier clipping, standard z-score normalization"
        ],
        icon="[1]", badge="Ingestion Tier", border_color=c_teal
    )

    draw_arrow(50, 81.5, 50, 77.0, "Engineered Clinical Feature Matrix (10000 x 17)")

    # Tier 2: Feature Transformation & Splitting (y: 64 - 77)
    draw_card(
        5, 64.5, 90, 12.0,
        "TIER 2: CLINICAL FEATURE ENGINEERING & STRATIFIED PARTITIONING",
        [
            "• Multi-Modal Feature Standardization: StandardScaler z-score scaling applied to numerical laboratory & vital metrics",
            "• Categorical & Ordinal Encoders: Robust one-hot and label encoding for Admission Type, Diagnosis, & Department Ward",
            "• Target Class Discretization: Patient Length of Stay categorized into Short (< 3d), Medium (3-7d), and Long (> 7d)",
            "• Class Imbalance Regularization: Automated balanced class weight penalties to compensate for Medium LOS dominance",
            "• Train/Test Stratification: 80/20 train-test split (8,000 training samples / 2,000 holdout test evaluations)"
        ],
        icon="[2]", badge="Transformation Tier", border_color=c_accent
    )

    draw_arrow(50, 64.5, 50, 60.0, "Standardized Clinical Train / Validation Tensors")

    # Tier 3: Random Forest Machine Learning (y: 44 - 60)
    draw_card(
        5, 44.5, 90, 15.0,
        "TIER 3: ENSEMBLE RANDOM FOREST CLASSIFICATION ARCHITECTURE",
        [
            "• Ensemble Forest Configuration: 200 de-correlated, deep Decision Trees with Bootstrap Aggregation (Bagging)",
            "• Node Split Optimization: Gini Impurity metric minimizing intra-node misclassification variance across candidate thresholds",
            "• Tree Regularization Parameters: max_depth=16, min_samples_split=5, min_samples_leaf=2 to suppress medical overfit",
            "• Cross-Validation Protocol: 5-Fold Stratified Cross-Validation ensuring generalized performance (65.80% +/- 0.51%)",
            "• Feature Importance Calculation: Mean Decrease in Impurity (MDI) identifying key LOS drivers (Age, CCI, Admission Type)",
            "• Out-of-Bag (OOB) Generalization: Inherent bootstrap validation estimating testing error during forest construction"
        ],
        icon="[3]", badge="Model Tier", border_color=c_navy
    )

    draw_arrow(50, 44.5, 50, 40.0, "Trained Ensemble Artifacts (model.joblib, scaler.joblib, encoder.joblib)")

    # Tier 4: Evaluation & Probability Scoring (y: 26 - 40)
    draw_card(
        5, 25.5, 90, 14.0,
        "TIER 4: CLINICAL TRIAGE, PROBABILITY SCORING & BED ALLOCATION",
        [
            "• Multi-Class Probability Vector: Aggregates decision tree fraction predictions into P(Short), P(Medium), P(Long)",
            "• Performance Benchmarks: 64.85% Test Accuracy, Macro ROC-AUC of 0.8134 demonstrating high discriminative capacity",
            "• Bed Allocation Optimization Engine: Proactive bed reservation algorithms mapping projected discharge timelines",
            "• Staffing & Nursing Logistics: Dynamic staffing allocation tailored to anticipated long-stay patient influx",
            "• Clinical Warning Thresholds: Flags high-risk patients (predicted Long Stay > 7 days) for intensive case management"
        ],
        icon="[4]", badge="Inference Tier", border_color=c_teal
    )

    draw_arrow(50, 25.5, 50, 21.0, "Sub-30ms Microservice Payloads (JSON)")

    # Tier 5: REST API & Web Dashboard (y: 6 - 21)
    draw_card(
        5, 5.5, 90, 15.0,
        "TIER 5: FLASK REST API BACKEND & CLINICAL WEB DASHBOARD",
        [
            "• RESTful Microservice Endpoints: POST /api/predict for instant admission triage; GET /api/status for model health",
            "• High-Throughput Performance: Low latency (< 30ms on standard CPUs), thread-safe Scikit-Learn inference pipeline",
            "• Dark-Mode Clinical Dashboard: Glassmorphism UI built with modern CSS variables, responsive grids, and fluid layout",
            "• Interactive Patient Intake Form: Seamless inputs for clinical parameters, vital indicators, and historical admissions",
            "• Real-Time Visual Triage Diagnosis: Live probability bars, projected discharge dates, and actionable nurse directives"
        ],
        icon="[5]", badge="Presentation Tier", border_color=c_accent
    )

    plt.tight_layout()
    os.makedirs("graphs", exist_ok=True)
    plt.savefig("graphs/block_diagram.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("[OK] Saved -> graphs/block_diagram.png")


if __name__ == "__main__":
    print("[*] Generating Hospital Management System Assets...")
    generate_all_equations()
    generate_block_diagram()
    print("[OK] All assets generated successfully!")
