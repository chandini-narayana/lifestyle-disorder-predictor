# src/train.py
import os
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings("ignore")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# The feature set we expect to feed the models (frontend-compatible)
EXPECTED_FEATURES = [
    "age",
    "gender_bin",               # 1 male, 0 female/other
    "height",                   # cm
    "weight",                   # kg
    "bmi",
    "smoking_encoded",          # 0..3
    "alcohol_encoded",          # 0..3
    "physical_activity",        # days/week 0..7
    "sleep_hours",
    "stress_level",             # 0..10
    "diet_fastfood_flag",       # 1 if fast food or processed, else 0
    # optional extra: weight_height_ratio included too (models can accept fewer features)
    "weight_height_ratio"
]

# Deterministic mappings (frontend recommended)
SMOKING_MAP = {"never": 0, "no info": 0, "no info ": 0, "former smoker": 1, "former": 1,
               "occasional": 2, "current": 2, "regular": 3, "heavy": 3, "current smoker": 2}
ALCOHOL_MAP = {"never": 0, "none": 0, "occasional": 1, "rarely": 1, "moderate": 2, "frequently": 2, "heavy": 3}
DIET_MAP = {"balanced": 0, "vegan": 1, "vegetarian": 2, "high protein": 3, "high carbohydrate": 4,
            "high sugar": 4, "high fat": 4, "fast food": 5, "processed": 5, "fast food or processed": 5}
MED_MAP = {"no new conditions": 0, "none": 0, "heart disease": 1, "diabetes": 2, "multiple conditions": 3}

def read_csv_smart(path):
    """
    Read CSV with delimiter detection. Falls back to ';' if single-column read occurs.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    try:
        df = pd.read_csv(path, sep=None, engine='python')
    except Exception:
        # fallback: try common delimiters
        for sep in [',', ';', '\t']:
            try:
                df = pd.read_csv(path, sep=sep)
                break
            except Exception:
                df = None
        if df is None:
            raise
    # If the file parsed into a single column that contains delimiter-separated content,
    # try re-reading with semicolon.
    if df.shape[1] == 1:
        # try semicolon
        try:
            df2 = pd.read_csv(path, sep=';')
            if df2.shape[1] > 1:
                df = df2
        except Exception:
            pass
    return df

def ensure_columns_lower(df):
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df

def convert_target_series(s):
    """
    Robustly convert a target series to numeric 0/1.
    Accepts numbers, 'Yes'/'No', 'True'/'False' etc.
    """
    # If numeric conversion works for many values, use it
    num = pd.to_numeric(s, errors='coerce')
    if num.notna().sum() / max(1, len(num)) > 0.5:
        # convert non-numeric coerced to NaN -> try mapping text
        mapped = s.astype(str).str.lower().map({
            'yes': 1, 'no': 0, 'true': 1, 'false': 0, 'y': 1, 'n': 0, 'positive': 1, 'negative': 0
        })
        num = num.fillna(mapped)
        num = pd.to_numeric(num, errors='coerce').fillna(0).astype(int)
        return num
    # else try mapping common strings
    mapped = s.astype(str).str.lower().map({
        'yes': 1, 'no': 0, 'true': 1, 'false': 0, 'y': 1, 'n': 0, 'positive': 1, 'negative': 0
    })
    if mapped.notna().sum() > 0:
        return mapped.fillna(0).astype(int)
    # last resort: try numeric coercion and fill NaNs with 0
    return pd.to_numeric(s, errors='coerce').fillna(0).astype(int)

def prepare_features(df):
    """
    Convert a raw dataframe (any dataset) into the expected feature DataFrame.
    Adds sensible defaults for missing fields.
    """
    df = df.copy()
    df = ensure_columns_lower(df)
    # Fill missing columns with defaults
    # string columns
    for col in df.columns:
        if df[col].dtype == "O":
            df[col] = df[col].fillna("unknown")
        else:
            df[col] = df[col].fillna(df[col].median())

    # Common column name variations mapping
    # height/weight might be named differently - try common alternatives
    if "height" not in df.columns:
        for alt in ["height_cm", "stature", "h"]:
            if alt in df.columns:
                df["height"] = pd.to_numeric(df[alt], errors='coerce')
                break

    if "weight" not in df.columns:
        for alt in ["weight_kg", "mass", "w"]:
            if alt in df.columns:
                df["weight"] = pd.to_numeric(df[alt], errors='coerce')
                break

    # Ensure numeric conversions
    for col in ["age", "height", "weight", "bmi", "physical_activity", "sleep_hours", "stress_level"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # BMI: if absent, compute using height (cm) and weight (kg)
    if "bmi" not in df.columns or df["bmi"].isna().all():
        if "height" in df.columns and "weight" in df.columns:
            # avoid zero division
            df["bmi"] = df.apply(lambda r: (r["weight"] / ((r["height"]/100)**2)) if r["height"] and r["height"] > 0 else np.nan, axis=1)
        else:
            df["bmi"] = df.get("bmi", 0)

    # weight/height ratio
    if "weight_height_ratio" not in df.columns:
        df["weight_height_ratio"] = df.apply(lambda r: (r.get("weight", 0) / r.get("height", 1)) if (r.get("height", 0) and r.get("height", 0) > 0) else 0, axis=1)

    # Fill defaults for lifestyle features that may not exist
    df["gender"] = df.get("gender", "unknown")
    # normalize common gender representations
    df["gender"] = df["gender"].astype(str).str.strip().str.lower().map(lambda x: x if isinstance(x, str) else str(x))

    df["smoking_level"] = df.get("smoking_level", df.get("smoking_history", df.get("smoke", "never")))
    df["alcohol_level"] = df.get("alcohol_level", df.get("alco", df.get("alcohol", "never")))
    df["diet_type"] = df.get("diet_type", df.get("diet", "balanced"))
    df["medical_history"] = df.get("medical_history", df.get("medicalhistory", "no new conditions"))
    df["physical_activity"] = df.get("physical_activity", df.get("active", 0))
    df["sleep_hours"] = df.get("sleep_hours", df.get("sleep", np.nan))
    df["stress_level"] = df.get("stress_level", df.get("stress", 0))

    # Convert to str then map
    # smoking
    df["smoking_encoded"] = df["smoking_level"].astype(str).str.lower().map(lambda x: SMOKING_MAP.get(x.strip(), SMOKING_MAP.get(x.split()[0].strip(), 0) if isinstance(x, str) and len(x.split())>0 else 0))
    # alcohol
    df["alcohol_encoded"] = df["alcohol_level"].astype(str).str.lower().map(lambda x: ALCOHOL_MAP.get(x.strip(), 0))
    # diet fast food flag
    df["diet_fastfood_flag"] = df["diet_type"].astype(str).str.lower().map(lambda x: 1 if ("fast" in x or "processed" in x) else 0)
    # medical history encoded
    df["medical_history_encoded"] = df["medical_history"].astype(str).str.lower().map(lambda x: MED_MAP.get(x.strip(), 0))
    # gender bin
    df["gender_bin"] = df["gender"].astype(str).str.lower().map(lambda x: 1 if x in ["male", "m", "man", "1", "true"] else 0)

    # Ensure numeric features exist and fill missing with median/defaults
    defaults = {
        "age": 45, "height": 170, "weight": 70, "bmi": 25.0,
        "physical_activity": 3, "sleep_hours": 7, "stress_level": 5
    }
    for k, v in defaults.items():
        if k not in df.columns:
            df[k] = v
        df[k] = pd.to_numeric(df[k], errors='coerce').fillna(v)

    # Final expected feature DataFrame (keep order)
    # Some models might have been trained with fewer features; we'll later subset as needed.
    X = pd.DataFrame()
    for f in EXPECTED_FEATURES:
        if f in df.columns:
            X[f] = df[f]
        else:
            # Provide default zero when completely missing
            X[f] = 0

    # sanity: ensure numeric dtype
    X = X.apply(pd.to_numeric, errors='coerce').fillna(0)
    return X

def save_encoders(name, encoders):
    joblib.dump(encoders, os.path.join(MODEL_DIR, f"{name}_encoders.joblib"))

def plot_and_save_feature_importance(name, model, feature_names):
    try:
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1]
        plt.figure(figsize=(10, 6))
        plt.title(f"{name.capitalize()} - Feature Importance")
        plt.bar(range(len(importances)), importances[indices])
        plt.xticks(range(len(importances)), np.array(feature_names)[indices], rotation=45, ha='right')
        plt.tight_layout()
        out = os.path.join(RESULTS_DIR, f"{name}_feature_importance.png")
        plt.savefig(out, dpi=150)
        plt.close()
        print(f"✓ Saved feature importance: {out}")
    except Exception as e:
        print("Could not plot feature importance:", e)

def plot_and_save_confusion(name, y_true, y_pred, model_key):
    cm = confusion_matrix(y_true, y_pred)
    try:
        import seaborn as sns
        plt.figure(figsize=(6,5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
        plt.title(f"{name.capitalize()} - {model_key} Confusion Matrix")
        plt.ylabel("True")
        plt.xlabel("Pred")
        out = os.path.join(RESULTS_DIR, f"{name}_{model_key}_confusion.png")
        plt.tight_layout()
        plt.savefig(out, dpi=150)
        plt.close()
        print(f"✓ Saved confusion matrix: {out}")
    except Exception:
        # fallback basic plot-less save by printing cm
        print(f"Confusion matrix ({model_key}):\n{cm}")

def train_for_disease(name, csv_filename, label_candidates):
    print("\n" + "="*60)
    print(f"TRAINING: {name.upper()}")
    print("="*60)
    path = os.path.join(DATA_DIR, csv_filename)
    if not os.path.exists(path):
        print(f"❌ Dataset missing: {path}")
        return

    # Read dataset robustly
    df = read_csv_smart(path)
    print("Dataset shape:", df.shape)

    # detect label column
    df = ensure_columns_lower(df)
    label_col = None
    for cand in label_candidates:
        if cand.lower() in df.columns:
            label_col = cand.lower()
            break
    if label_col is None:
        # choose last column as label
        label_col = df.columns[-1]
    print("Using label column:", label_col)

    # If the CSV read incorrectly as one column containing semicolon-separated header row:
    if df.shape[1] == 1 and isinstance(df.iloc[0,0], str) and ";" in df.iloc[0,0]:
        # try splitting rows into columns
        df = pd.read_csv(path, sep=';')
        df = ensure_columns_lower(df)
        print("Recovered by re-reading with ';' delimiter. New shape:", df.shape)

    # Prepare target
    try:
        y_raw = df[label_col]
    except Exception:
        y_raw = df.iloc[:, -1]
    y = convert_target_series(y_raw)
    print("Target distribution:", dict(y.value_counts()))

    # Prepare features
    X = prepare_features(df)
    print("Prepared features shape:", X.shape)

    # Align X columns to EXPECTED_FEATURES (train uses these columns)
    # Keep order
    X = X[[c for c in EXPECTED_FEATURES if c in X.columns or True][:len(EXPECTED_FEATURES)]]
    # If for some reason columns exceed expected length, keep only first len(EXPECTED_FEATURES)
    X = X.iloc[:, :len(EXPECTED_FEATURES)]

    # If number of rows mismatch between X and y, try align by index
    if len(X) != len(y):
        min_len = min(len(X), len(y))
        X = X.iloc[:min_len].reset_index(drop=True)
        y = y.iloc[:min_len].reset_index(drop=True)
        print("Aligned X and y to min length:", min_len)

    # Handle single class case
    unique_classes = np.unique(y)
    X_train = X.copy()
    y_train = y.copy()
    applied_smote = False

    if len(unique_classes) == 1:
        print("Single-class target detected. Attempting to create a balanced training set.")
        try:
            sm = SMOTE(random_state=42)
            X_train, y_train = sm.fit_resample(X_train, y_train)
            applied_smote = True
            print("✓ SMOTE applied. New distribution:", dict(pd.Series(y_train).value_counts()))
        except Exception as e:
            print("SMOTE failed:", e)
            # fallback simple duplication of dataset (makes tiny pseudo-minority)
            X_train = pd.concat([X_train, X_train], ignore_index=True)
            y_train = pd.concat([y_train, y_train], ignore_index=True)
            print("Duplicated dataset as fallback. New shape:", X_train.shape)
    else:
        # if imbalanced, optionally apply SMOTE (only if minority less than 40% of majority)
        counts = pd.Series(y_train).value_counts()
        if counts.min() / counts.max() < 0.6:
            try:
                sm = SMOTE(random_state=42)
                X_train, y_train = sm.fit_resample(X_train, y_train)
                applied_smote = True
                print("Applied SMOTE for class balance. New distribution:", dict(pd.Series(y_train).value_counts()))
            except Exception as e:
                print("SMOTE skipped/failed:", e)

    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)

    # Train Random Forest
    print("\nTraining Random Forest...")
    rf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    rf.fit(X_scaled, y_train)
    print("Random Forest trained.")

    # Train Logistic Regression if possible
    lr = None
    try:
        if len(np.unique(y_train)) >= 2:
            print("Training Logistic Regression (lbfgs)...")
            lr = LogisticRegression(max_iter=5000, solver='lbfgs', random_state=42)
            lr.fit(X_scaled, y_train)
            print("Logistic Regression (lbfgs) trained.")
        else:
            print("Skipping Logistic Regression: only one class in training set.")
    except Exception as e:
        print("lbfgs failed:", e)
        try:
            print("Trying liblinear solver for LR...")
            lr = LogisticRegression(max_iter=5000, solver='liblinear', random_state=42)
            lr.fit(X_scaled, y_train)
            print("Logistic Regression (liblinear) trained.")
        except Exception as e2:
            print("Logistic Regression failed altogether:", e2)
            lr = None

    # Save models and scaler and encoders
    joblib.dump(rf, os.path.join(MODEL_DIR, f"{name}_rf.joblib"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, f"{name}_scaler.joblib"))
    if lr is not None:
        joblib.dump(lr, os.path.join(MODEL_DIR, f"{name}_lr.joblib"))

    # Save encoders (mappings) for frontend/backends consistency
    encoders = {
        "smoking_map": SMOKING_MAP,
        "alcohol_map": ALCOHOL_MAP,
        "diet_map": DIET_MAP,
        "medical_map": MED_MAP
    }
    save_encoders(name, encoders)
    print(f"Saved RF, scaler, (LR saved? {'yes' if lr is not None else 'no'}) and encoders for {name}")

    # Diagnostics on training set
    y_pred_rf = rf.predict(X_scaled)
    acc_rf = accuracy_score(y_train, y_pred_rf)
    print(f"RF training accuracy: {acc_rf:.4f}")

    if lr is not None:
        y_pred_lr = lr.predict(X_scaled)
        acc_lr = accuracy_score(y_train, y_pred_lr)
        print(f"LR training accuracy: {acc_lr:.4f}")

    # Feature importance plot
    try:
        feature_names = X.columns.tolist()
        plot_and_save_feature_importance(name, rf, feature_names)
    except Exception as e:
        print("Feature importance plotting failed:", e)

    # Save a small example prediction file for quick frontend tests
    try:
        sample = X.head(5)
        sample.to_csv(os.path.join(RESULTS_DIR, f"{name}_sample_features.csv"), index=False)
    except Exception:
        pass

if __name__ == "__main__":
    # Configure dataset filenames and which columns to use as labels
    diseases = {
        "diabetes": ("diabetes_prediction_dataset.csv", ["diabetes", "diabetes_status", "has_diabetes"]),
        "stroke": ("healthcare-dataset-stroke-data.csv", ["stroke", "stroke_outcome", "stroke_status"]),
        # Use cardio_train.csv which includes lifestyle-related fields (semicolon-delimited in many sources)
        "heart": ("cardio_train.csv", ["cardio", "target", "heartdisease", "cardio"])
    }

    print("\n================ TRAINING PIPELINE STARTED ================\n")
    for name, (fname, label_cands) in diseases.items():
        try:
            train_for_disease(name, fname, label_cands)
        except Exception as e:
            import traceback
            print(f"❌ Error training {name}: {e}")
            traceback.print_exc()

    print("\n✓ Training pipeline finished. Models stored in:", MODEL_DIR)
