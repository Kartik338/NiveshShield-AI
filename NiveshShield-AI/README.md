# NiveshShield AI
Check before you trust: explainable scam-risk checker for first-time retail investors (Hindi + English). Built for SANGYAN, Track A.

Run: `pip install -r requirements.txt && python backend/app.py`, then open http://localhost:5000
Test: `pip install pytest && pytest tests`
OCR needs Tesseract (+ `hin` language data). AI explanation is optional: set `ANTHROPIC_API_KEY`.

## Guardrails
No stock tips or buy/sell advice. Never a bare scam/not-scam verdict: every result shows reasons and uncertainty. Nothing is stored or logged. URLs are never fetched.

## Limitations
Rule-based (weighted regex), not a trained model. SEBI numbers are format-checked only. Small hand-written rule set; OCR quality depends on screenshot clarity.
