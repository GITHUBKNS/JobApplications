"""Tests for Pydantic schemas."""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models.schemas import (
    ApplicationStatus,
    AutofillPayload,
    JobPosting,
    MasterResume,
    RecruiterCandidate,
)


class TestJobPosting:
    def test_minimal_creation(self):
        job = JobPosting(id="test_1", title="Data Engineer", company="Acme")
        assert job.id == "test_1"
        assert job.remote is False

    def test_full_creation(self):
        job = JobPosting(
            id="test_2",
            title="Senior Data Engineer",
            company="Stripe",
            location="San Francisco, CA",
            remote=True,
            source="jsearch",
            url="https://stripe.com/jobs/123",
            jd_text="We need a data engineer...",
            salary="$150,000 - $200,000",
        )
        assert job.remote is True
        assert "stripe" in job.url


class TestMasterResume:
    def test_empty_resume(self):
        resume = MasterResume()
        assert resume.skills == []
        assert resume.experience == []

    def test_serialization(self):
        resume = MasterResume(skills=["Python", "SQL"])
        data = resume.model_dump()
        assert data["skills"] == ["Python", "SQL"]
        loaded = MasterResume.model_validate(data)
        assert loaded.skills == ["Python", "SQL"]


class TestApplicationStatus:
    def test_all_statuses(self):
        expected = [
            "Saved", "Applied", "Email Sent", "Followup1 Sent",
            "Followup2 Sent", "Recruiter Replied", "Interview",
            "Offer", "Rejected", "Ghosted",
        ]
        actual = [s.value for s in ApplicationStatus]
        assert actual == expected


class TestAutofillPayload:
    def test_defaults(self):
        payload = AutofillPayload()
        assert payload.sponsorship_needed == "Yes"
        assert payload.work_authorization == "Require sponsorship"
