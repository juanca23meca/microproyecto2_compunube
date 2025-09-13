from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
import tensorflow as tf

app = Flask(__name__)

# Carga modelo preentrenado (ImageNet)
model  = tf.keras.applications.MobileNetV2(weights="imagenet")
prep   = tf.keras.applications.mobilenet_v2.preprocess_input
decode = tf.keras.applications.mobilenet_v2.decode_predictions

@app.get("/healthz")
def healthz():
    return "ok"

@app.post("/predict")
def predict():
    f = request.files.get("img")
    if not f:
        return jsonify(error="missing img"), 400
    img = Image.open(f.stream).convert("RGB").resize((224, 224))
    x = np.expand_dims(np.array(img), 0)
    x = prep(x)
    y = model.predict(x, verbose=0)
    (_, name, prob) = decode(y, top=1)[0][0]
    return jsonify(label=name, probability=float(prob))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)


@app.get("/")
def index():
    return """
<!doctype html>
<html>
<head><meta charset="utf-8"><title>Image Classifier</title></head>
<body style="font-family:sans-serif;max-width:640px;margin:40px auto;">
  <h1>Classifier</h1>
  <form id="f">
    <input type="file" name="img" accept="image/*">
    <button type="submit">Predict</button>
  </form>
  <pre id="out"></pre>
<script>
const f = document.getElementById('f');
const out = document.getElementById('out');
f.addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(f);
  out.textContent = 'Predicting...';
  try {
    const r = await fetch('/predict', { method:'POST', body: fd });
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
