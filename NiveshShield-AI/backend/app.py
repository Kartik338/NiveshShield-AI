import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from flask import Flask, request, jsonify, send_from_directory
from services.engine import scan_text, combine, level, next_steps
from services.url_analyzer import analyze_url
from services.ai_service import ocr_image, explain

app = Flask(__name__, static_folder=str(pathlib.Path(__file__).parent.parent / "frontend"), static_url_path="")

@app.get("/")
def home(): return send_from_directory(app.static_folder, "index.html")

@app.post("/scan-message")
def scan_message():
    d = request.get_json(force=True); text = d.get("text", "")[:5000]; lang = d.get("lang", "en")
    r = scan_text(text); r["explanation"] = explain(text, r, lang); return jsonify(r)

@app.post("/scan-url")
def scan_url():
    u = analyze_url(request.get_json(force=True).get("url", "").strip())
    s = combine([f["weight"] for f in u["flags"]])
    return jsonify({"score": s, "level": level(s), "flags": u["flags"], "urls": [u], "next_steps": next_steps(level(s)),
                    "uncertainty": {"en": "Heuristic check only; the page is never opened.", "hi": "यह सिर्फ़ अनुमान आधारित जाँच है; पेज खोला नहीं जाता।"}})

@app.post("/scan-image")
def scan_image():
    f = request.files.get("image")
    if not f: return jsonify({"error": "No image uploaded"}), 400
    text = ocr_image(f.read())
    if not text.strip(): return jsonify({"error": "Could not read text. Install Tesseract or paste the text instead."}), 422
    r = scan_text(text); r["extracted_text"] = text[:1500]; r["explanation"] = explain(text, r, request.form.get("lang", "en")); return jsonify(r)

if __name__ == "__main__": app.run(debug=True, port=5000)
