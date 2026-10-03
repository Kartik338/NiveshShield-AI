import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from services.engine import scan_text
def test_scam_high():
    r = scan_text("SEBI registered VIP group! Guaranteed 5% daily profit. Pay registration fee to 98765@ybl, join t.me/xyz. Hurry, last slots!")
    assert r["level"] == "HIGH"
def test_bank_warning_safe():
    assert scan_text("Never share your OTP with anyone. - SBI")["level"] == "LOW"
def test_fake_domain():
    assert scan_text("Login at http://sbi-kyc-update.xyz now")["level"] in ("MEDIUM", "HIGH")
