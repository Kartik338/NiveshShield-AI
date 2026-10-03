import os, io
def ocr_image(data: bytes) -> str:
    try:
        import pytesseract; from PIL import Image
        return pytesseract.image_to_string(Image.open(io.BytesIO(data)), lang="eng+hin")
    except Exception:
        return ""
def explain(text, result, lang="en"):
    """Optional LLM explanation; falls back to rule reasons so the demo never breaks."""
    reasons = " ".join(f[lang] for f in result["flags"])
    if not os.getenv("ANTHROPIC_API_KEY") or not result["flags"]: return reasons
    try:
        import anthropic
        r = anthropic.Anthropic().messages.create(model="claude-sonnet-4-6", max_tokens=300,
            messages=[{"role": "user", "content": f"In simple {'Hindi' if lang=='hi' else 'English'}, in 3 short sentences, explain to a first-time investor why this message is risky. Use ONLY these findings: {reasons}. No investment advice, no stock tips, do not say 'definitely a scam'.\n\nMessage:\n{text[:800]}"}])
        return r.content[0].text
    except Exception:
        return reasons
