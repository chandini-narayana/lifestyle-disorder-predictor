import React, { useState } from "react";
import "./App.css";

function App() {
  const [showForm, setShowForm] = useState(false);

  const [age, setAge] = useState("");
  const [gender, setGender] = useState("");
  const [height, setHeight] = useState("");
  const [weight, setWeight] = useState("");
  const [bmi, setBmi] = useState("");
  const [smoking, setSmoking] = useState("");
  const [alcohol, setAlcohol] = useState("");
  const [diet, setDiet] = useState("");
  const [physicalActivity, setPhysicalActivity] = useState(3);
  const [sleep, setSleep] = useState(7);
  const [stress, setStress] = useState(5);

  const [results, setResults] = useState(null);

  // -----------------------------------------
  // BMI Calculation
  // -----------------------------------------
  const calculateBMI = (h, w) => {
    if (h > 0 && w > 0) {
      const hMeters = h / 100;
      setBmi((w / (hMeters * hMeters)).toFixed(1));
    }
  };

  const handleHeightChange = (e) => {
    setHeight(e.target.value);
    calculateBMI(e.target.value, weight);
  };

  const handleWeightChange = (e) => {
    setWeight(e.target.value);
    calculateBMI(height, e.target.value);
  };

  // -----------------------------------------
  // API CALL
  // -----------------------------------------
  const handleSubmit = async () => {
    const payload = {
      age: Number(age),
      gender,
      height: Number(height),
      weight: Number(weight),
      bmi: Number(bmi),
      smoking_level: smoking,
      alcohol_level: alcohol,
      diet_type: diet,
      physical_activity: Number(physicalActivity),
      sleep_hours: Number(sleep),
      stress_level: Number(stress)
    };

    try {
      const res = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      console.log("Backend response:", data);
      setResults(data);

    } catch (err) {
      console.error("Error:", err);
    }
  };

  return (
    <div className="app-container-full">

      {/* -------------------- HOME PAGE -------------------- */}
      {!showForm && (
        <div className="welcome-section-full animate-fadeIn" style={{ width: "100%", height: "100%" }}>
          <div className="welcome-card-full" style={{ width: "100%", height: "100%", padding: "40px" }}>
            
            <div className="circle circle1"></div>
            <div className="circle circle2"></div>
            <div className="circle circle3"></div>
            <div className="circle circle4"></div>
            <div className="circle circle5"></div>
            <div className="circle circle6"></div>

            <div className="header-row">
              <img src="/assets/welcome.png" alt="welcome" className="welcome-image animate-popIn" />
              <h1 className="app-title animate-bounceIn">SmartCura</h1>
            </div>

            <p className="app-subtitle animate-slideInRight">
              AI-Powered Lifestyle Risk Assessment
            </p>

            <div className="badges animate-slideInLeft">
              <div className="badge">Science-based</div>
              <div className="badge">AI-driven</div>
              <div className="badge">Early Detection</div>
            </div>

            <div className="ribbon animate-zoomIn">
              Analyze • Track • Improve Your Lifestyle
            </div>

            <p className="intro-text animate-slideInUp">
              SmartCura evaluates your lifestyle habits, identifies health risks,
              and provides actionable recommendations for a healthier life.
            </p>

            <div className="feature-grid-full">
              <div className="feature-box animate-flipInX">Personalized health insights.</div>
              <div className="feature-box animate-flipInX">Early detection alerts.</div>
              <div className="feature-box animate-flipInX">AI-driven lifestyle analysis.</div>
              <div className="feature-box animate-flipInX">Progress tracking.</div>
              <div className="feature-box animate-flipInX">Daily wellness tips.</div>
              <div className="feature-box animate-flipInX">Goal achievements.</div>
            </div>

            <button
              className="start-btn shine animate-zoomIn"
              onClick={() => setShowForm(true)}
            >
              Start Assessment
            </button>
          </div>
        </div>
      )}

      {/* -------------------- FORM PAGE -------------------- */}
      {showForm && (
        <div className="form-section animate-fadeIn" style={{ width: "100%" }}>
          <div className="form-card enhanced-form animate-slideInUp">
            <button
  className="back-btn"
  onClick={() => setShowForm(false)}
>
  ← Back
</button>

            <h2 className="form-title animate-zoomIn">Health Assessment Form</h2>

            <label>Age</label>
            <input type="number" value={age} onChange={(e)=>setAge(e.target.value)} />

            <label>Gender</label>
            <select value={gender} onChange={(e)=>setGender(e.target.value)}>
              <option value="">Select</option>
              <option>Male</option>
              <option>Female</option>
            </select>

            <label>Height (cm)</label>
            <input type="number" value={height} onChange={handleHeightChange} />

            <label>Weight (kg)</label>
            <input type="number" value={weight} onChange={handleWeightChange} />

            <label>Your BMI</label>
            <input type="text" value={bmi} readOnly />

            <label>Smoking Level</label>
            <select value={smoking} onChange={(e)=>setSmoking(e.target.value)}>
              <option value="">Select</option>
              <option>never</option>
              <option>occasional</option>
              <option>regular</option>
              <option>heavy</option>
            </select>

            <label>Alcohol Consumption</label>
            <select value={alcohol} onChange={(e)=>setAlcohol(e.target.value)}>
              <option value="">Select</option>
              <option>none</option>
              <option>moderate</option>
              <option>heavy</option>
            </select>

            <label>Diet Type</label>
            <select value={diet} onChange={(e)=>setDiet(e.target.value)}>
              <option value="">Select</option>
              <option>balanced</option>
              <option>high sugar</option>
              <option>fast food</option>
              <option>high fat</option>
              <option>vegetarian</option>
              <option>non-vegetarian</option>
            </select>

            <label>Physical Activity (days/week)</label>
            <input type="range" min="0" max="7" value={physicalActivity} onChange={(e)=>setPhysicalActivity(e.target.value)} />
            <p className="value-text">{physicalActivity} days/week</p>

            <label>Sleep Hours</label>
            <input type="range" min="0" max="12" value={sleep} onChange={(e)=>setSleep(e.target.value)} />
            <p className="value-text">{sleep} hours/night</p>

            <label>Stress Level</label>
            <input type="range" min="0" max="10" value={stress} onChange={(e)=>setStress(e.target.value)} />
            <p className="value-text">{stress}/10</p>

            <button className="submit-btn" onClick={handleSubmit}>Submit</button>

            {/* -------------------- RESULTS UI -------------------- */}
            {results && (
              <div className="results-container animate-fadeIn">

                <h2 className="results-title">Your Health Risk Analysis</h2>

                {/* --- Disease Cards --- */}
                <div className="risk-cards">

                  <div className="risk-card">
                    <h3>Diabetes Risk</h3>
                    <p className="risk-value">
                      {(results.predictions.diabetes.RF_probability * 100).toFixed(2)}%
                    </p>
                  </div>

                  <div className="risk-card">
                    <h3>Stroke Risk</h3>
                    <p className="risk-value">
                      {(results.predictions.stroke.RF_probability * 100).toFixed(2)}%
                    </p>
                  </div>

                  <div className="risk-card">
                    <h3>Heart Disease Risk</h3>
                    <p className="risk-value">
                      {(results.predictions.heart.RF_probability * 100).toFixed(2)}%
                    </p>
                  </div>

                </div>

                {/* --- Recommendations List --- */}
                <div className="recommendations-box">
                  <h3>Recommendations</h3>
                  <ul>
                    {results.recommendations.map((item, index) => (
                      <li key={index} className="recommendation-item">
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>

              </div>
            )}

          </div>
        </div>
      )}

    </div>
  );
}

export default App;
