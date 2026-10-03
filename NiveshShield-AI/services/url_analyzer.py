import re, ipaddress
from urllib.parse import urlparse
OFFICIAL = {"sebi.gov.in","nsdl.co.in","nsdl.com","sbi.co.in","onlinesbi.sbi","pnbindia.in","zerodha.com","groww.in","upstox.com","cybercrime.gov.in","rbi.org.in"}
BRANDS = ["sebi","nsdl","sbi","pnb","zerodha","groww","upstox","angelone","hdfc","icici","kotak"]
SHORT = {"bit.ly","tinyurl.com","t.co","cutt.ly","rb.gy","is.gd","shorturl.at","goo.gl"}
BAD_TLD = {"xyz","top","icu","click","live","shop","site","online","vip","work","cfd","buzz"}

def analyze_url(url):
    u = url if re.match(r"https?://", url, re.I) else "http://" + url
    host = (urlparse(u).hostname or "").lower()
    flags = []
    def add(w, en, hi): flags.append({"weight": w, "en": en, "hi": hi})
    official = any(host == d or host.endswith("." + d) for d in OFFICIAL)
    try:
        ipaddress.ip_address(host); add(0.3, "Link uses a raw IP address.", "लिंक में सीधा IP एड्रेस है।")
    except ValueError: pass
    if not official:
        for b in BRANDS:
            if b in host:
                add(0.40, f"Looks like '{b}' but is not its official domain.", f"'{b}' जैसा दिखता है पर उसका आधिकारिक डोमेन नहीं है।"); break
    if host in SHORT: add(0.2, "URL shortener hides the real destination.", "शॉर्टनर असली गंतव्य छुपाता है।")
    if host.split(".")[-1] in BAD_TLD: add(0.2, "Domain ending is common in throwaway scam sites.", "यह डोमेन एंडिंग स्कैम साइट्स में आम है।")
    if host.startswith("xn--") or ".xn--" in host: add(0.3, "Punycode domain can imitate real letters.", "Punycode डोमेन असली अक्षरों की नकल कर सकता है।")
    if host.count("-") >= 3: add(0.15, "Domain has many hyphens.", "डोमेन में कई हाइफ़न हैं।")
    if u.lower().startswith("http://") and not official: add(0.1, "Link is not HTTPS.", "लिंक HTTPS नहीं है।")
    return {"url": url, "host": host, "official": official, "flags": flags}
