# src/recommender.py
def get_recommendations(data: dict):
    """
    Simple deterministic recommendations based on lifestyle inputs.
    Expects keys: smoking_level, alcohol_level, diet_type, physical_activity, sleep_hours, stress_level, bmi
    """
    recs = []

    smoking = str(data.get("smoking_level", "")).strip().lower()
    alcohol = str(data.get("alcohol_level", "")).strip().lower()
    diet = str(data.get("diet_type", "")).strip().lower()
    physical_activity = int(data.get("physical_activity", 0))
    sleep_hours = float(data.get("sleep_hours", 0))
    stress_level = int(data.get("stress_level", 0))
    bmi = float(data.get("bmi", 0))

    if "never" not in smoking and smoking != "":
        recs.append("Consider reducing or quitting smoking to lower your risk.")

    if alcohol in ["frequently", "heavy", "moderate", "occasionally", "rarely"] and alcohol != "never":
        if alcohol in ["frequently", "heavy", "moderate"]:
            recs.append("Limit alcohol intake — keep it occasional or avoid for better heart and liver health.")
        else:
            recs.append("Keep alcohol consumption minimal.")

    if diet in ["fast food", "high sugar", "high fat"]:
        recs.append("Switch to a balanced diet rich in vegetables, lean protein, and whole grains.")

    if physical_activity < 3:
        recs.append("Increase physical activity to at least 3–5 days per week (30+ mins/day).")

    if sleep_hours < 6:
        recs.append("Aim for 7–8 hours of sleep per night for better recovery and metabolic health.")
    elif sleep_hours > 10:
        recs.append("Very long sleep hours can be a risk indicator; consider checking sleep quality.")

    if stress_level > 6:
        recs.append("Adopt stress management: mindfulness, breathing exercises, or counseling.")

    if bmi and bmi > 25:
        recs.append("Work on reaching a normal BMI through calorie control and exercise (consult a nutritionist).")

    if not recs:
        recs.append("Maintain your healthy lifestyle — keep tracking and improving gradually.")

    return recs
