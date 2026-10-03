"""Explainable rule engine. Final score is deterministic; AI only explains."""
import json, re, pathlib
from .url_analyzer import analyze_url

RULES = json.loads((pathlib.Path(__file__).parent.parent / "data" / "rules.json").read_text(encoding="utf-8"))
URL_RE = re.compile(r"https?://[^\s<>\"']+|(?:www\.)[^\s<>\"']+", re.I)
SEBI_NO = re.compile(r"\bIN[HAZBP]\d{9}\b", re.I)  # format check only
SAFE_CTX = re.compile(r"(never|do not|don't|कभी नहीं|न करें)[^.\n]{0,25}(share|बताएं|साझा)[^.\n]{0,15}(otp|pin|cvv|password)", re.I)

def level(score):
    return "HIGH" if score >= 65 else "MEDIUM" if score >= 35 else "LOW"

def combine(weights):
    p = 1.0
    for w in weights: p *= (1 - w)
    return round((1 - p) * 100)

def scan_text(text):
    text = text or ""
    safe = bool(SAFE_CTX.search(text))  # a bank warning about OTP is not a threat
    flags = []
    for r in RULES:
        if r["id"] == "otp_share" and safe: continue
        m = re.search(r["re"], text, re.I)
        if m: flags.append({"id": r["id"], "weight": r["w"], "match": m.group(0)[:60], "en": r["en"], "hi": r["hi"]})
    urls = [u.rstrip(".,)") for u in URL_RE.findall(text)]
    url_results = [analyze_url(u) for u in urls[:5]]
    ws = [f["weight"] for f in flags] + [f["weight"] for u in url_results for f in u["flags"]]
    score = combine(ws)
    claims_sebi = any(f["id"] == "sebi_claim" for f in flags)
    note = None
    if claims_sebi and not SEBI_NO.search(text):
        note = {"en": "SEBI registration is claimed but no registration number is given.", "hi": "SEBI रजिस्ट्रेशन का दावा है, पर नंबर नहीं दिया गया।"}
    elif SEBI_NO.search(text):
        note = {"en": "A SEBI-style number is present. Only its format is checked here; verify it on sebi.gov.in.", "hi": "SEBI जैसा नंबर मिला। यहाँ सिर्फ़ फ़ॉर्मेट जाँचा गया है; sebi.gov.in पर ज़रूर सत्यापित करें।"}
    return {"score": score, "level": level(score), "flags": flags, "urls": url_results, "sebi_note": note,
            "uncertainty": {"en": "This is a risk indicator, not proof. It is not investment or legal advice.", "hi": "यह जोखिम का संकेत है, प्रमाण नहीं। यह निवेश या कानूनी सलाह नहीं है।"},
            "next_steps": next_steps(level(score))}

def next_steps(lv):
    base = [{"en": "Check any SEBI claim at sebi.gov.in before sending money.", "hi": "पैसे भेजने से पहले sebi.gov.in पर SEBI दावे की जाँच करें."}]
    if lv != "LOW":
        base = [{"en": "Do not pay, click, or share OTP/PIN.", "hi": "पैसे न भेजें, लिंक न खोलें, OTP/PIN साझा न करें."},
                {"en": "If money is lost: call 1930, report at cybercrime.gov.in, and inform your bank.", "hi": "पैसे गए हों तो तुरंत 1930 पर कॉल करें, cybercrime.gov.in पर रिपोर्ट करें और बैंक को बताएं."},
                {"en": "Complain to SEBI at scores.sebi.gov.in.", "hi": "scores.sebi.gov.in पर SEBI में शिकायत करें."}] + base
    return base
