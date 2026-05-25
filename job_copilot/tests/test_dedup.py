"""Tests for job deduplication."""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.dedup import are_duplicates, deduplicate, normalize_company, normalize_title
from app.models.schemas import JobPosting


class TestNormalize:
    def test_normalize_company_strips_inc(self):
        assert normalize_company("Stripe, Inc.") == "stripe"

    def test_normalize_company_strips_llc(self):
        assert normalize_company("Acme LLC") == "acme"

    def test_normalize_company_lowercase(self):
        assert normalize_company("DATABRICKS") == "databricks"

    def test_normalize_title_removes_parens(self):
        assert normalize_title("Data Engineer (Remote)") == "data engineer"

    def test_normalize_title_removes_dash_suffix(self):
        assert normalize_title("Senior Data Engineer - Platform") == "senior data engineer"


class TestDuplicates:
    def _make_job(self, title: str, company: str, source: str = "test") -> JobPosting:
        return JobPosting(
            id=f"{source}_{company}_{title}",
            title=title,
            company=company,
            source=source,
        )

    def test_exact_same_job(self):
        a = self._make_job("Data Engineer", "Stripe", "jsearch")
        b = self._make_job("Data Engineer", "Stripe", "adzuna")
        assert are_duplicates(a, b) is True

    def test_different_company(self):
        a = self._make_job("Data Engineer", "Stripe")
        b = self._make_job("Data Engineer", "Coinbase")
        assert are_duplicates(a, b) is False

    def test_similar_title(self):
        a = self._make_job("Senior Data Engineer", "Stripe Inc.")
        b = self._make_job("Senior Data Engineer (Remote)", "Stripe")
        assert are_duplicates(a, b) is True

    def test_different_title(self):
        a = self._make_job("Data Engineer", "Stripe")
        b = self._make_job("Product Manager", "Stripe")
        assert are_duplicates(a, b) is False


class TestDeduplicate:
    def _make_job(self, title: str, company: str, source: str = "test") -> JobPosting:
        return JobPosting(
            id=f"{source}_{company}_{title}",
            title=title,
            company=company,
            source=source,
        )

    def test_removes_duplicates(self):
        jobs = [
            self._make_job("Data Engineer", "Stripe", "jsearch"),
            self._make_job("Data Engineer", "Stripe", "adzuna"),
            self._make_job("Data Engineer", "Coinbase", "jsearch"),
        ]
        result = deduplicate(jobs)
        assert len(result) == 2

    def test_keeps_first_occurrence(self):
        jobs = [
            self._make_job("Data Engineer", "Stripe", "jsearch"),
            self._make_job("Data Engineer", "Stripe", "adzuna"),
        ]
        result = deduplicate(jobs)
        assert result[0].source == "jsearch"

    def test_empty_list(self):
        assert deduplicate([]) == []

    def test_no_duplicates(self):
        jobs = [
            self._make_job("Data Engineer", "Stripe"),
            self._make_job("ML Engineer", "Google"),
            self._make_job("Backend Engineer", "Meta"),
        ]
        result = deduplicate(jobs)
        assert len(result) == 3
