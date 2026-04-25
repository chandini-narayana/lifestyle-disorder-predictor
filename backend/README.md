# 🧠 Life Risk Analyzer Backend

Predicts **Diabetes**, **Heart Disease**, and **Stroke Risk** using Logistic Regression & Random Forest, with lifestyle recommendations.

## 🚀 Setup
```bash
pip install -r requirements.txt
```

## 🧠 Train Models
```bash
python src/train.py
```

## 🧩 Run API
```bash
uvicorn src.api:app --reload
```

## 🧪 Test
```bash
pytest -v
```

Visit Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
