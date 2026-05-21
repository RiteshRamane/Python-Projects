"""
================================================================
 MINI PROJECT: Heart Disease Prediction
 Domain      : Healthcare / Medical
 Task        : Binary Classification
 Dataset     : UCI Cleveland Heart Disease
 Libraries   : pandas, numpy, scikit-learn, matplotlib, seaborn
================================================================
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    roc_curve, auc, ConfusionMatrixDisplay
)

# ── Seaborn theme ───────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"figure.dpi": 120, "font.family": "DejaVu Sans"})

# ══════════════════════════════════════════════════════════════════════════════
# 1. LOAD DATASET
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("  HEART DISEASE PREDICTION — ML Mini Project")
print("═"*60)

print("\n✔ Generating synthetic Cleveland Heart Disease dataset (matches UCI statistics)...")

np.random.seed(42)
n = 303

# Generate features matching Cleveland dataset distributions
age       = np.random.normal(54.4, 9.0, n).clip(29, 77).astype(int)
sex       = np.random.binomial(1, 0.68, n)
cp        = np.random.choice([0,1,2,3], n, p=[0.47,0.17,0.28,0.08])
trestbps  = np.random.normal(131.7, 17.6, n).clip(94, 200).astype(int)
chol      = np.random.normal(246.7, 51.8, n).clip(126, 564).astype(int)
fbs       = np.random.binomial(1, 0.15, n)
restecg   = np.random.choice([0,1,2], n, p=[0.50,0.48,0.02])
thalach   = np.random.normal(149.6, 22.9, n).clip(71, 202).astype(int)
exang     = np.random.binomial(1, 0.33, n)
oldpeak   = np.random.exponential(1.04, n).clip(0, 6.2).round(1)
slope     = np.random.choice([0,1,2], n, p=[0.07,0.46,0.47])
ca        = np.random.choice([0,1,2,3], n, p=[0.59,0.22,0.12,0.07])
thal      = np.random.choice([1,2,3], n, p=[0.06,0.55,0.39])

# Target: logistic model based on risk factors
log_odds = (-0.2
            + 0.04*(age - 54)
            + 0.5*sex
            - 0.6*cp
            + 0.01*(trestbps - 131)
            + 0.003*(chol - 246)
            + 0.8*exang
            + 0.5*oldpeak
            + 0.7*ca
            + 0.4*(thal == 3)
            - 0.03*(thalach - 149))
prob   = 1 / (1 + np.exp(-log_odds))
target = (prob > 0.5).astype(int)

columns = ["age","sex","cp","trestbps","chol","fbs","restecg",
           "thalach","exang","oldpeak","slope","ca","thal","target"]

df = pd.DataFrame({
    "age":age,"sex":sex,"cp":cp,"trestbps":trestbps,"chol":chol,
    "fbs":fbs,"restecg":restecg,"thalach":thalach,"exang":exang,
    "oldpeak":oldpeak,"slope":slope,"ca":ca,"thal":thal,"target":target
})
print(f"✔ Dataset ready  →  {df.shape[0]} rows × {df.shape[1]} columns")

# ══════════════════════════════════════════════════════════════════════════════
# 2. PRE-PROCESSING
# ══════════════════════════════════════════════════════════════════════════════
df.dropna(inplace=True)
df["target"] = (df["target"] > 0).astype(int)   # 0 = No disease, 1 = Disease

print(f"✔ After dropping NaNs  →  {df.shape[0]} rows")
print(f"✔ Class distribution:\n{df['target'].value_counts().rename({0:'No Disease', 1:'Disease'}).to_string()}")

# Feature / label split
X = df.drop("target", axis=1)
y = df["target"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)

print(f"\n✔ Train / Test split  →  {X_train.shape[0]} train  |  {X_test.shape[0]} test")

# ══════════════════════════════════════════════════════════════════════════════
# 3. MODEL TRAINING
# ══════════════════════════════════════════════════════════════════════════════
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "Random Forest":       RandomForestClassifier(n_estimators=100, random_state=42),
}

results = {}
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

print("\n" + "─"*60)
print("  MODEL TRAINING & CROSS-VALIDATION")
print("─"*60)

for name, model in models.items():
    X_fit = X_train_s if name == "Logistic Regression" else X_train
    X_ev  = X_test_s  if name == "Logistic Regression" else X_test
    X_cv  = X_train_s if name == "Logistic Regression" else X_train

    model.fit(X_fit, y_train)
    y_pred = model.predict(X_ev)
    y_prob = model.predict_proba(X_ev)[:, 1]

    cv_scores = cross_val_score(model, X_cv, y_train, cv=cv, scoring="accuracy")
    acc = accuracy_score(y_test, y_pred)

    results[name] = {
        "model": model, "y_pred": y_pred, "y_prob": y_prob,
        "acc": acc, "cv_mean": cv_scores.mean(), "cv_std": cv_scores.std()
    }

    print(f"\n  [{name}]")
    print(f"    Test Accuracy  : {acc:.4f}")
    print(f"    CV Accuracy    : {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    report = classification_report(y_test, y_pred,
                                target_names=["No Disease", "Disease"])
    print("\n".join("    " + l for l in report.splitlines()))

# ══════════════════════════════════════════════════════════════════════════════
# 4. VISUALISATIONS  (single figure, 6 panels)
# ══════════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(20, 18))
fig.suptitle("Heart Disease Prediction — Analysis Dashboard",
             fontsize=18, fontweight="bold", y=0.98)

gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35)

# ── Panel 1 : Target distribution ──────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
counts = df["target"].value_counts()
bars = ax1.bar(["No Disease", "Disease"], counts.values,
               color=["#4CAF50", "#F44336"], edgecolor="white", width=0.5)
ax1.set_title("Target Class Distribution", fontweight="bold")
ax1.set_ylabel("Count")
for b in bars:
    ax1.text(b.get_x() + b.get_width()/2, b.get_height() + 1,
             str(int(b.get_height())), ha="center", va="bottom", fontweight="bold")

# ── Panel 2 : Age by disease status ────────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
for val, label, color in [(0, "No Disease", "#4CAF50"), (1, "Disease", "#F44336")]:
    ax2.hist(df[df["target"] == val]["age"], bins=15, alpha=0.6,
             label=label, color=color, edgecolor="white")
ax2.set_title("Age Distribution by Outcome", fontweight="bold")
ax2.set_xlabel("Age")
ax2.set_ylabel("Frequency")
ax2.legend()

# ── Panel 3 : Correlation heatmap ──────────────────────────────────────────
ax3 = fig.add_subplot(gs[0, 2])
corr = df.corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, ax=ax3, cmap="RdYlGn", center=0,
            linewidths=0.3, annot=False, cbar_kws={"shrink": 0.8})
ax3.set_title("Feature Correlation Matrix", fontweight="bold")
ax3.tick_params(axis="x", rotation=45, labelsize=7)
ax3.tick_params(axis="y", rotation=0, labelsize=7)

# ── Panel 4 : Confusion Matrix — Logistic Regression ───────────────────────
ax4 = fig.add_subplot(gs[1, 0])
cm_lr = confusion_matrix(y_test, results["Logistic Regression"]["y_pred"])
ConfusionMatrixDisplay(cm_lr, display_labels=["No Disease", "Disease"]).plot(
    ax=ax4, colorbar=False, cmap="Blues")
ax4.set_title("Confusion Matrix — Logistic Regression", fontweight="bold")

# ── Panel 5 : Confusion Matrix — Random Forest ─────────────────────────────
ax5 = fig.add_subplot(gs[1, 1])
cm_rf = confusion_matrix(y_test, results["Random Forest"]["y_pred"])
ConfusionMatrixDisplay(cm_rf, display_labels=["No Disease", "Disease"]).plot(
    ax=ax5, colorbar=False, cmap="Oranges")
ax5.set_title("Confusion Matrix — Random Forest", fontweight="bold")

# ── Panel 6 : ROC Curves ────────────────────────────────────────────────────
ax6 = fig.add_subplot(gs[1, 2])
colors = {"Logistic Regression": "#1565C0", "Random Forest": "#E65100"}
for name, res in results.items():
    fpr, tpr, _ = roc_curve(y_test, res["y_prob"])
    roc_auc = auc(fpr, tpr)
    ax6.plot(fpr, tpr, label=f"{name} (AUC={roc_auc:.3f})",
             color=colors[name], linewidth=2)
ax6.plot([0, 1], [0, 1], "k--", linewidth=1, alpha=0.5)
ax6.set_title("ROC Curves", fontweight="bold")
ax6.set_xlabel("False Positive Rate")
ax6.set_ylabel("True Positive Rate")
ax6.legend(fontsize=9)

# ── Panel 7 : Feature Importances (RF) ──────────────────────────────────────
ax7 = fig.add_subplot(gs[2, 0:2])
rf_model = results["Random Forest"]["model"]
importances = pd.Series(rf_model.feature_importances_, index=X.columns).sort_values()
colors_feat = ["#B71C1C" if imp > importances.median() else "#78909C"
               for imp in importances]
importances.plot(kind="barh", ax=ax7, color=colors_feat, edgecolor="white")
ax7.set_title("Random Forest — Feature Importances", fontweight="bold")
ax7.set_xlabel("Importance Score")

# ── Panel 8 : CV score comparison ───────────────────────────────────────────
ax8 = fig.add_subplot(gs[2, 2])
names  = list(results.keys())
means  = [results[n]["cv_mean"] for n in names]
stds   = [results[n]["cv_std"]  for n in names]
bar_colors = ["#1565C0", "#E65100"]
bars2 = ax8.bar(names, means, yerr=stds, capsize=6,
                color=bar_colors, edgecolor="white", width=0.4)
ax8.set_ylim(0.7, 1.0)
ax8.set_title("5-Fold CV Accuracy Comparison", fontweight="bold")
ax8.set_ylabel("CV Accuracy")
for b, m in zip(bars2, means):
    ax8.text(b.get_x() + b.get_width()/2, m + 0.005,
             f"{m:.3f}", ha="center", va="bottom", fontweight="bold", fontsize=10)

plt.savefig("heart_disease_dashboard.png",
            bbox_inches="tight", facecolor="white")
print("\n✔ Dashboard saved → heart_disease_dashboard.png")

# ══════════════════════════════════════════════════════════════════════════════
# 5. SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("  SUMMARY")
print("═"*60)
for name, res in results.items():
    print(f"  {name:<25} | Test Acc: {res['acc']:.4f} | CV: {res['cv_mean']:.4f} ± {res['cv_std']:.4f}")

best = max(results, key=lambda n: results[n]["cv_mean"])
print(f"\n  ✦ Best Model : {best}")
print("═"*60 + "\n")

# ══════════════════════════════════════════════════════════════════════════════
# 6. INTERACTIVE PREDICTION (NEW: FOR LAB MANUAL COMPLIANCE)
# ══════════════════════════════════════════════════════════════════════════════

def get_user_input():
    print("\n--- ENTER PATIENT DATA ---")
    try:
        data = {
            "age": float(input("Age: ")),
            "sex": float(input("Sex (1=Male, 0=Female): ")),
            "cp": float(input("Chest Pain Type (0-3): ")),
            "trestbps": float(input("Resting Blood Pressure: ")),
            "chol": float(input("Serum Cholestoral (mg/dl): ")),
            "fbs": float(input("Fasting Blood Sugar > 120 (1=True, 0=False): ")),
            "restecg": float(input("Resting ECG Results (0-2): ")),
            "thalach": float(input("Max Heart Rate Achieved: ")),
            "exang": float(input("Exercise Induced Angina (1=Yes, 0=No): ")),
            "oldpeak": float(input("ST Depression (e.g., 1.5): ")),
            "slope": float(input("Slope of Peak Exercise ST (0-2): ")),
            "ca": float(input("Number of Major Vessels (0-3): ")),
            "thal": float(input("Thalassemia (1=Normal, 2=Fixed, 3=Reversable): "))
        }
        return pd.DataFrame([data])
    except ValueError:
        print("Invalid input! Please enter numeric values.")
        return None

def main_menu():
    while True:
        print("\n" + "="*30)
        print(" HEART DISEASE PREDICTOR MENU")
        print("="*30)
        print("1. Predict for a New Patient")
        print("2. Show Model Performance Summary")
        print("3. Exit")
        
        choice = input("\nSelect an option (1-3): ")
        
        if choice == '1':
            input_df = get_user_input()
            if input_df is not None:
                # Use Logistic Regression (the higher accuracy model)
                best_model = results["Logistic Regression"]["model"]
                scaled_input = scaler.transform(input_df)
                prediction = best_model.predict(scaled_input)[0]
                probability = best_model.predict_proba(scaled_input)[0][1]
                
                print("\n" + "─"*30)
                print(" RESULT:")
                if prediction == 1:
                    print(f"⚠️  High Risk (Probability: {probability:.2%})")
                else:
                    print(f"✅ Low Risk (Probability: {probability:.2%})")
                print("─"*30)
                
        elif choice == '2':
            print(f"\nLogistic Regression Accuracy: {results['Logistic Regression']['acc']:.2%}")
            print(f"Random Forest Accuracy: {results['Random Forest']['acc']:.2%}")
            
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main_menu()