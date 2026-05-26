"""Tests for resume parser."""
import json
import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.resume_parser import load_master_resume, save_master_resume
from app.models.schemas import ContactInfo, MasterResume


@pytest.fixture
def sample_resume():
    return MasterResume(
        contact=ContactInfo(
            name="Prasanth Konada",
            email="test@example.com",
            location="Newark, NJ",
        ),
        summary="Experienced Data Engineer",
        skills=["Python", "SQL", "Spark"],
        experience=[],
        education=[],
        projects=[],
    )


class TestSaveLoadResume:
    def test_save_and_load(self, sample_resume, tmp_path):
        path = tmp_path / "test_resume.json"
        save_master_resume(sample_resume, path)
        loaded = load_master_resume(path)
        assert loaded is not None
        assert loaded.contact.name == "Prasanth Konada"
        assert "Python" in loaded.skills

    def test_load_nonexistent(self, tmp_path):
        result = load_master_resume(tmp_path / "nonexistent.json")
        assert result is None

    def test_roundtrip_preserves_data(self, sample_resume, tmp_path):
        path = tmp_path / "test_resume.json"
        save_master_resume(sample_resume, path)
        loaded = load_master_resume(path)
        assert loaded.model_dump() == sample_resume.model_dump()
