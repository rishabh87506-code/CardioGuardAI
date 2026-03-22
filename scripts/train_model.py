"""
CardioGuard AI — Production Model Training Script
==================================================
Trains the Antigravity-22 cardiac risk classifier using
sklearn's GradientBoostingClassifier (SHAP TreeExplainer compatible).

Dataset: 10,000 synthetic patients with medically-informed distributions
based on Framingham Heart Study, WHO CVD risk factors, AHA guidelines.

Features (22):
  Continuous : age, cholesterol, blood_pressure, heart_rate, bmi,
               triglycerides, blood_sugar, exercise_hours_per_week,
               sedentary_hours_per_day, physical_activity_days_per_week,
               sleep_hours_per_day
  Binary     : sex, diabetes, family_history, smoking, obesity,
               alcohol_consumption, previous_heart_problems,
               medication_use, chest_pain
  Ordinal    : diet (0=Unhealthy,1=Average,2=Healthy),
               stress_level (1-10)

Output : model/antigravity_model.pkl
"""

import os
import pickle
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.metrics import roc_auc_score, classification_report

ROOT       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR  = os.path.join(ROOT, 'model')
MODEL_PATH = os.path.join(MODEL_DIR, 'antigravity_model.pkl')

FEATURES = [
    "age", "sex", "cholesterol", "blood_pressure", "heart_rate",
    "diabetes", "family_history", "smoking", "obesity", "alcohol_consumption",
    "exercise_hours_per_week", "diet", "previous_heart_problems",
    "medication_use", "stress_level", "sedentary_hours_per_day", "bmi",
    "triglycerides", "physical_activity_days_per_week", "sleep_hours_per_day",
    "chest_pain", "blood_sugar"
]

SEED      = 42
N_SAMPLES = 10_000


def generate_data(n: int, seed: int):
    """
    Synthetic cardiac dataset with realistic epidemiological distributions.
    Outcome is derived from a calibrated logistic risk function (~25% prevalence).
    """
    rng = np.random.default_rng(seed)

    age             = rng.normal(54, 12, n).clip(25, 85).astype(int)
    cholesterol     = rng.normal(210, 40, n).clip(120, 350)
    blood_pressure  = rng.normal(128, 18, n).clip(70, 210)
    heart_rate      = rng.normal(74, 12, n).clip(45, 130)
    bmi             = rng.normal(27.5, 5.5, n).clip(15, 50)
    triglycerides   = rng.normal(160, 65, n).clip(40, 500)
    blood_sugar     = rng.normal(105, 28, n).clip(60, 350)
    exercise_hours  = rng.exponential(2.5, n).clip(0, 14)
    sedentary_hours = rng.normal(7, 3, n).clip(0, 18)
    activity_days   = rng.choice(range(8), n, p=[0.15,0.10,0.12,0.15,0.18,0.15,0.10,0.05])
    sleep_hours     = rng.normal(7.0, 1.2, n).clip(4, 12)

    sex          = rng.binomial(1, 0.52, n)
    diabetes     = rng.binomial(1, 0.11, n)
    family_hist  = rng.binomial(1, 0.28, n)
    smoking      = rng.binomial(1, 0.20, n)
    obesity      = (bmi >= 30).astype(int)
    alcohol      = rng.binomial(1, 0.35, n)
    prev_heart   = rng.binomial(1, 0.08, n)
    medication   = rng.binomial(1, 0.32, n)
    chest_pain   = rng.binomial(1, 0.14, n)
    diet         = rng.choice([0, 1, 2], n, p=[0.30, 0.45, 0.25])
    stress_level = rng.integers(1, 11, n)

    # Logistic risk model calibrated to ~25% cardiac event rate
    # Intercept calibrated so that an average-risk patient yields ~30% event probability
    # (sum of expected terms for average patient ~12.3; target log-odds ~-1.1 => intercept ~-13.5)
    log_odds = (
        -13.5
        + 0.055 * age
        + 0.40  * sex
        + 0.012 * cholesterol
        + 0.022 * blood_pressure
        + 0.010 * heart_rate
        + 1.00  * diabetes
        + 0.70  * family_hist
        + 1.10  * smoking
        + 0.50  * obesity
        + 0.20  * alcohol
        - 0.12  * exercise_hours
        - 0.30  * diet
        + 1.80  * prev_heart
        + 0.40  * medication
        + 0.08  * stress_level
        + 0.06  * sedentary_hours
        + 0.04  * bmi
        + 0.003 * triglycerides
        - 0.10  * activity_days
        + 0.08  * np.abs(sleep_hours - 7.5)
        + 1.50  * chest_pain
        + 0.005 * blood_sugar
    )
    prob         = 1 / (1 + np.exp(-log_odds))
    heart_attack = (prob > rng.uniform(size=n)).astype(int)

    X = np.column_stack([
        age, sex, cholesterol, blood_pressure, heart_rate,
        diabetes, family_hist, smoking, obesity, alcohol,
        exercise_hours.round(1), diet, prev_heart,
        medication, stress_level, sedentary_hours.round(1),
        bmi.round(1), triglycerides.round(0),
        activity_days, sleep_hours.round(1),
        chest_pain, blood_sugar.round(1)
    ])
    return X, heart_attack


def train():
    print("=" * 62)
    print("  CardioGuard AI — Antigravity Model Training Pipeline v1.0")
    print("=" * 62)

    # 1. Generate synthetic training data
    print(f"\n[1/5] Generating {N_SAMPLES:,} synthetic patient records ...")
    X, y = generate_data(N_SAMPLES, SEED)
    prevalence = y.mean() * 100
    print(f"      Class 1 (cardiac event) prevalence: {prevalence:.1f}%")
    print(f"      Feature matrix shape: {X.shape}")

    # 2. Configure GradientBoostingClassifier
    print("\n[2/5] Configuring GradientBoostingClassifier ...")
    clf = GradientBoostingClassifier(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        max_features='sqrt',
        min_samples_leaf=20,
        random_state=SEED
    )

    # 3. 5-fold stratified cross-validation
    print("\n[3/5] Running 5-fold stratified cross-validation ...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    cv_scores = cross_val_score(clf, X, y, cv=cv, scoring='roc_auc', n_jobs=-1)
    print(f"      Per-fold AUC : {[round(s, 4) for s in cv_scores]}")
    print(f"      Mean AUC     : {cv_scores.mean():.4f}  ±  {cv_scores.std():.4f}")

    # 4. Train final model + holdout evaluation
    print("\n[4/5] Training final model on full dataset ...")
    clf.fit(X, y)

    # Holdout evaluation (80/20 split for reporting)
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=SEED
    )
    clf_eval = GradientBoostingClassifier(
        n_estimators=300, max_depth=4, learning_rate=0.05,
        subsample=0.8, max_features='sqrt', min_samples_leaf=20,
        random_state=SEED
    )
    clf_eval.fit(X_tr, y_tr)
    y_prob = clf_eval.predict_proba(X_te)[:, 1]
    y_pred = clf_eval.predict(X_te)
    test_auc = roc_auc_score(y_te, y_prob)
    print(f"\n      Holdout Test AUC : {test_auc:.4f}")
    print("\n      Classification Report (threshold=0.5) :")
    print(classification_report(y_te, y_pred,
          target_names=['No Event', 'Cardiac Event']))

    # Top feature importances
    importances = clf.feature_importances_
    top_idx = np.argsort(importances)[::-1][:5]
    print("      Top 5 predictors by importance:")
    for i in top_idx:
        print(f"        {FEATURES[i]:42s}  {importances[i]:.4f}")

    # Store feature names for downstream compatibility
    clf.feature_names_in_ = np.array(FEATURES)

    # 5. Save
    print(f"\n[5/5] Saving model to {MODEL_PATH} ...")
    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(clf, f, protocol=4)
    size_kb = os.path.getsize(MODEL_PATH) / 1024
    print(f"      Saved successfully ({size_kb:.1f} KB)")

    print("\n" + "=" * 62)
    print(f"  DONE.  Final CV AUC: {cv_scores.mean():.4f}")
    print("=" * 62)


if __name__ == '__main__':
    train()
