"""Tests for scheduler logic."""
import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.scheduler import (
    cancel_followups,
    get_scheduled_jobs,
    get_scheduler,
    schedule_followup,
)


@pytest.fixture(autouse=True)
def reset_scheduler():
    import app.core.scheduler as mod
    mod._scheduler = None
    yield
    if mod._scheduler and mod._scheduler.running:
        mod._scheduler.shutdown(wait=False)
    mod._scheduler = None


class TestScheduler:
    def test_get_scheduler_creates_instance(self):
        sched = get_scheduler()
        assert sched is not None
        assert sched.running

    def test_schedule_followup(self):
        dummy_func = MagicMock()
        sched_id = schedule_followup(
            func=dummy_func,
            job_id="test_job_123",
            delay_days=3,
            followup_num=1,
        )
        assert sched_id == "followup_test_job_123_1"
        jobs = get_scheduled_jobs()
        assert any(j["id"] == sched_id for j in jobs)

    def test_cancel_followups(self):
        dummy_func = MagicMock()
        schedule_followup(func=dummy_func, job_id="test_123", delay_days=3, followup_num=1)
        schedule_followup(func=dummy_func, job_id="test_123", delay_days=7, followup_num=2)

        cancel_followups("test_123")
        jobs = get_scheduled_jobs()
        assert not any("test_123" in j["id"] for j in jobs)

    def test_schedule_replaces_existing(self):
        dummy_func = MagicMock()
        schedule_followup(func=dummy_func, job_id="dup_job", delay_days=3, followup_num=1)
        schedule_followup(func=dummy_func, job_id="dup_job", delay_days=5, followup_num=1)

        jobs = get_scheduled_jobs()
        matching = [j for j in jobs if j["id"] == "followup_dup_job_1"]
        assert len(matching) == 1
