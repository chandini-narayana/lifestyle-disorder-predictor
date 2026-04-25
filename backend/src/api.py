from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import joblib
import traceback
import os

# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_DIR = os.path.join(BASE_DIR, "models")

# ---------------------------------------------------------
# FASTAPI + CORS
# ---------------------------------------------------------
app = FastAPI(title="Life Risk Analyzer Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # allow frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# REQUEST MODEL
# ---------------------------------------------------------
class UserData(BaseModel):
    age: int
    gender: str
    height: float
    weight: float
    bmi: float
    smoking_level: str
    alcohol_level: str
    diet_type: str
    physical_activity: int
    sleep_hours: float
    stress_level: int

# ---------------------------------------------------------
# Model Loader
# ---------------------------------------------------------
def load(model):
    path = os.path.join(MODEL_DIR, model)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing model file: {path}")
    return joblib.load(path)

# ---------------------------------------------------------
# PREDICTION ENDPOINT
# ---------------------------------------------------------
@app.post("/analyze")
def analyze(data: UserData):
    try:
        diseases = ["diabetes", "stroke", "heart"]
        results = {}

        # -------------------------------
        # BASE 11 features from frontend
        # -------------------------------
        F = np.array([
            data.age,
            1 if data.gender.lower() == "male" else 0,
            data.height,
            data.weight,
            data.bmi,
            1 if data.smoking_level not in ["non-smoker", "never"] else 0,
            1 if data.alcohol_level.lower() not in ["never", "none"] else 0,
            data.physical_activity,
            data.sleep_hours,
            data.stress_level,
            1 if data.diet_type.lower() in ["high fat", "high sugar", "fast food"] else 0
        ])

        # -------------------------------
        # Loop through diseases
        # -------------------------------
        for d in diseases:

            scaler = load(f"{d}_scaler.joblib")
            rf = load(f"{d}_rf.joblib")

            lr_path = os.path.join(MODEL_DIR, f"{d}_lr.joblib")
            lr = joblib.load(lr_path) if os.path.exists(lr_path) else None

            required = scaler.n_features_in_

            # pad with zeros if model expects more features
            if len(F) < required:
                padded = np.pad(F, (0, required - len(F)), 'constant')
            else:
                padded = F[:required]

            X = padded.reshape(1, -1)
            Xs = scaler.transform(X)

            # RF prediction
            rf_pred = int(rf.predict(Xs)[0])
            rf_prob = float(rf.predict_proba(Xs)[0][1])

            # LR prediction
            if lr:
                lr_pred = int(lr.predict(Xs)[0])
                lr_prob = float(lr.predict_proba(Xs)[0][1])
            else:
                lr_pred = None
                lr_prob = None

            results[d] = {
                "RF_prediction": rf_pred,
                "RF_probability": round(rf_prob, 4),
                "LR_prediction": lr_pred,
                "LR_probability": round(lr_prob, 4) if lr_prob is not None else None
            }

        # ---------------------------------------------------------
        #   RECOMMENDATIONS ENGINE
        # ---------------------------------------------------------
        rec_list = []

        # Disease-based recs
        if results["diabetes"]["RF_probability"] > 0.30:
            rec_list.append("Reduce sugar intake and avoid sweetened drinks.")

        if results["stroke"]["RF_probability"] > 0.30:
            rec_list.append("Monitor your blood pressure regularly.")

        if results["heart"]["RF_probability"] > 0.30:
            rec_list.append("Increase physical activity (walking, jogging, cardio).")

        # Lifestyle recs
        if data.sleep_hours < 6:
            rec_list.append("Increase sleep to 7–8 hours daily.")

        if data.physical_activity < 3:
            rec_list.append("Exercise at least 3 times per week.")

        if data.stress_level > 6:
            rec_list.append("Practice deep breathing or meditation to reduce stress.")

        if data.diet_type.lower() in ["fast food", "high fat", "high sugar"]:
            rec_list.append("Shift to a balanced diet with vegetables and whole grains.")

        if data.smoking_level.lower() in ["regular", "heavy"]:
            rec_list.append("Reduce smoking to improve heart and lung health.")

        if data.alcohol_level.lower() == "heavy":
            rec_list.append("Reduce alcohol intake to protect liver & heart health.")

        if not rec_list:
            rec_list.append("You have a healthy profile. Keep maintaining your habits!")

        # ---------------------------------------------------------
        # FINAL RETURN
        # ---------------------------------------------------------
        return {
            "predictions": results,
            "recommendations": rec_list
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
