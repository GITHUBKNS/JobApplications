"""Tests for ATS scoring (mocked LLM calls)."""
import json
import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.ats_scorer import analyze_jd, score_resume, tailor_resume
from app.models.schemas import ATSAnalysis, Experience, MasterResume


@pytest.fixture
def sample_resume():
    return MasterResume(
        summary="Experienced data engineer",
        skills=["Python", "SQL", "Spark", "Airflow", "AWS"],
        experience=[
            Experience(
                company="Acme Corp",
                title="Data Engineer",
                bullets=[
                    "Built ETL pipelines using Python and Airflow",
                    "Managed data warehouse on AWS Redshift",
                ],
            )
        ],
    )


class TestAnalyzeJD:
    @patch("app.core.ats_scorer.LLMClient")
    def test_analyze_jd_returns_dict(self, mock_cls):
        mock_llm = MagicMock()
        mock_cls.return_value = mock_llm
        mock_llm.generate_json.return_value = {
            "hard_skills": ["Python", "SQL", "dbt"],
            "tools": ["Snowflake", "Airflow"],
            "keywords": ["data pipeline", "ETL"],
            "yoe_signals": ["3+ years"],
            "soft_skills": ["communication"],
        }
        result = analyze_jd("Sample JD text")
        assert "hard_skills" in result
        assert "Python" in result["hard_skills"]


class TestScoreResume:
    @patch("app.core.ats_scorer.LLMClient")
    def test_score_resume(self, mock_cls, sample_resume):
        mock_llm = MagicMock()
        mock_cls.return_value = mock_llm
        mock_llm.generate_json.side_effect = [
            {
                "hard_skills": ["Python", "SQL", "dbt"],
                "tools": ["Snowflake", "Airflow"],
                "keywords": ["data pipeline"],
                "yoe_signals": ["3+ years"],
                "soft_skills": [],
            },
            {
                "score": 72,
                "matched_keywords": ["Python", "SQL", "Airflow"],
                "missing_keywords": ["dbt", "Snowflake"],
                "suggestions": ["Add dbt experience"],
            },
        ]
        result = score_resume(sample_resume, "Looking for a Data Engineer with Python, SQL, dbt, Snowflake")
        assert isinstance(result, ATSAnalysis)
        assert result.score == 72
        assert "dbt" in result.missing_keywords


class TestTailorResume:
    @patch("app.core.ats_scorer.LLMClient")
    def test_tailor_resume(self, mock_cls, sample_resume):
        tailored_data = sample_resume.model_dump()
        tailored_data["experience"][0]["bullets"] = [
            "Designed and built scalable ETL/ELT data pipelines using Python, Airflow, and dbt",
            "Managed enterprise data warehouse on AWS Redshift, optimizing query performance",
        ]
        mock_llm = MagicMock()
        mock_cls.return_value = mock_llm
        mock_llm.generate_json.return_value = tailored_data

        result = tailor_resume(sample_resume, "Need dbt and Snowflake experience")
        assert isinstance(result, MasterResume)
        assert "dbt" in result.experience[0].bullets[0]
