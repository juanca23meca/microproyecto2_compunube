from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
import os

app = Flask(__name__)

MODEL_FILE = "spam_model.pkl"

# Entrenar modelo si no existe
if not os.path.exists(MODEL_FILE):
    emails = [
        "Congratulations! You've won a $1000 gift card. Click here!",
        "Dear user, your invoice is attached.",
        "Limited offer, buy now and save 50%",
        "Meeting scheduled at 10am tomorrow.",
        "You have been selected for a prize. Claim now!",
        "Please review the attached report."
    ]
    labels = [1, 0, 1, 0, 1, 0]  # 1=spam, 0=ham

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(emails)
    model = MultinomialNB()
    model.fit(X, labels)

    with open(MODEL_FILE, "wb") as f:
        pickle.dump((vectorizer, model), f)

with open(MODEL_FILE, "rb") as f:
    vectorizer, model = pickle.load(f)

@app.get("/healthz")
def healthz():
    return "ok"

@app.post("/predict")
def predict():
    data = request.json
    if not data or "email" not in data:
        return jsonify(error="missing email field"), 400
    
    email_text = data["email"]
    X = vectorizer.transform([email_text])
    pred = model.predict(X)[0]
    prob = model.predict_proba(X)[0][pred]

    return jsonify(label=int(pred), probability=float(prob))

@app.get("/")
def index():
    return """
<!doctype html>
<html>
<head><meta charset="utf-8"><title>Spam Classifier</title></head>
<body style="font-family:sans-serif;max-width:640px;margin:40px auto;">
  <h1>Spam Classifier</h1>
  <form id="f">
    <input type="text" name="email" placeholder="Type email text">
    <button type="submit">Predict</button>
  </form>
  <pre id="out"></pre>
<script>
const f = document.getElementById('f');
const out = document.getElementById('out');
f.addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(f);
  const email = fd.get('email');
  out.textContent = 'Predicting...';
  try {
    const r = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    const j = await r.json();
    out.textContent = JSON.stringify(j, null, 2);
  } catch (err) {
    out.textContent = 'Error: ' + err;
  }
});
</script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
