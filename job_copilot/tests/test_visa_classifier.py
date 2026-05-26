"""Tests for visa sponsorship classification."""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.visa_classifier import classify_visa_signal, should_filter_out


class TestVisaClassifier:
    def test_reject_us_citizens_only(self):
        assert classify_visa_signal("Must be a US citizen") == "reject"

    def test_reject_no_sponsorship(self):
        assert classify_visa_signal("No visa sponsorship available") == "reject"

    def test_reject_will_not_sponsor(self):
        assert classify_visa_signal("We will not sponsor visas") == "reject"

    def test_reject_security_clearance(self):
        assert classify_visa_signal("Security clearance required") == "reject"

    def test_reject_without_sponsorship(self):
        jd = "Must be authorized to work in the US without sponsorship"
        assert classify_visa_signal(jd) == "reject"

    def test_reject_cannot_sponsor(self):
        assert classify_visa_signal("We cannot sponsor work visas") == "reject"

    def test_positive_h1b_sponsorship(self):
        assert classify_visa_signal("H1B sponsorship available") == "positive"

    def test_positive_willing_to_sponsor(self):
        assert classify_visa_signal("We are willing to sponsor qualified candidates") == "positive"

    def test_positive_sponsorship_available(self):
        assert classify_visa_signal("Visa sponsorship is available for this role") == "positive"

    def test_unknown_no_signal(self):
        jd = "We are looking for a Data Engineer with 3+ years of experience in Python and SQL."
        assert classify_visa_signal(jd) == "unknown"

    def test_unknown_empty(self):
        assert classify_visa_signal("") == "unknown"

    def test_should_filter_reject(self):
        assert should_filter_out("Must be US citizen", require_sponsorship=True) is True

    def test_should_not_filter_positive(self):
        assert should_filter_out("H1B sponsorship available", require_sponsorship=True) is False

    def test_should_not_filter_when_not_required(self):
        assert should_filter_out("Must be US citizen", require_sponsorship=False) is False

    def test_should_not_filter_unknown(self):
        assert should_filter_out("Looking for a Data Engineer", require_sponsorship=True) is False
