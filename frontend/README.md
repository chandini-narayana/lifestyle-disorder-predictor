<<<<<<< HEAD
# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
=======
# Lifestyle Disorder Predictor

## Overview

The Lifestyle Disorder Predictor is a full-stack machine learning application that assesses the risk of lifestyle-related disorders based on user-provided health and behavioral data. The system integrates a web-based frontend with a backend API that serves trained machine learning models for real-time prediction.

---

## Features

* Predicts risks for multiple lifestyle disorders, including diabetes, heart disease, stroke, and sleep disorders
* End-to-end machine learning pipeline covering preprocessing, feature engineering, and inference
* RESTful API for model predictions
* Modular architecture with clearly separated frontend and backend
* Scalable design allowing integration of additional models and datasets

---

## System Architecture

```id="arch1"
User Input (Frontend)
        ↓
Frontend UI (Forms / Inputs)
        ↓
Backend API (Flask / FastAPI)
        ↓
Preprocessing Pipeline
        ↓
Machine Learning Model (Logistic Regression / Random Forest)
        ↓
Prediction Output (Risk Result)
        ↓
Frontend Display
```

---

## Project Structure

```id="struct1"
lifestyle-disorder-predictor/
│
├── frontend/        # User interface
├── backend/         # API and ML pipeline
│   ├── models/      # Excluded from repository (see Model Files section)
│   ├── tests/
│   └── ...
└── README.md
```

---

## Tech Stack

### Frontend

* HTML, CSS, JavaScript

### Backend

* Python
* Flask / FastAPI

### Machine Learning

* Scikit-learn
* Pandas
* NumPy

---

## Machine Learning Details

The system utilizes supervised learning techniques trained on structured health datasets.

**Models used:**

* Logistic Regression (baseline model)
* Random Forest (primary model for improved performance)

**Preprocessing steps:**

* Data cleaning and validation
* Feature encoding
* Feature scaling and normalization

---

## API Endpoints

### 1. Predict Diabetes Risk

**Endpoint:**

```
POST /predict/diabetes
```

**Request (JSON):**

```json id="api1"
{
  "age": 45,
  "bmi": 28.5,
  "glucose_level": 140,
  "physical_activity": "low"
}
```

**Response:**

```json id="api2"
{
  "prediction": "High Risk"
}
```

---

### 2. Predict Heart Disease Risk

**Endpoint:**

```
POST /predict/heart
```

---

### 3. Predict Stroke Risk

**Endpoint:**

```
POST /predict/stroke
```

---

## Setup Instructions

### 1. Clone the Repository

```id="setup1"
git clone https://github.com/chandini-narayana/lifestyle-disorder-predictor.git
cd lifestyle-disorder-predictor
```

---

### 2. Backend Setup

```id="setup2"
cd backend
pip install -r requirements.txt
python app.py
```

---

### 3. Frontend Setup

```id="setup3"
cd frontend
```

If using static files:

```id="setup4"
open index.html
```

If using a framework (e.g., React):

```id="setup5"
npm install
npm start
```

---

## Application Screenshots

### User Interface

<p align="center">
  <img src="assets/ui-homepage.png" width="800"/>
</p>

### System Architecture

<p align="center">
  <img src="assets/system-architecture.png" width="600"/>
</p>

### Model Performance Comparison

<p align="center">
  <img src="assets/model-performance.png" width="700"/>
</p>

### Confusion Matrices

#### Heart Disease Model
<p align="center">
  <img src="assets/heart-confusion-matrix.png" width="500"/>
</p>

#### Diabetes Model
<p align="center">
  <img src="assets/diabetes-confusion-matrix.png" width="500"/>
</p>

#### Stroke Model
<p align="center">
  <img src="assets/stroke-confusion-matrix.png" width="500"/>
</p>
---

## Model Files

Trained model files are not included in this repository due to size limitations.

Download the models from:
https://drive.google.com/drive/folders/1D_I-3SUiHZd9NiolLAco2tAyhCNqC4Us?usp=sharing

After downloading, place all files in:

```id="setup6"
backend/models/
```

---

## Collaboration

* Frontend Development: Bhoomika N
* Backend and Machine Learning: Chandini Narayana

---

## Future Enhancements

* Improve model accuracy and evaluation metrics
* Deploy application using cloud platforms (AWS, Render, Vercel)
* Integrate real-time health monitoring data
* Enhance user interface and user experience

---

## License

This project is intended for academic and demonstration purposes.
>>>>>>> f0954adcfdcad8eb97c001da7fc341a1c0a70611
