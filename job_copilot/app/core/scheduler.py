"""APScheduler setup for follow-up cadence + daily job pulls."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from app.core.logging import get_logger

log = get_logger(__name__)

_scheduler: BackgroundScheduler | None = None


def get_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler()
        _scheduler.start()
        log.info("scheduler_started")
    return _scheduler


def schedule_daily_job_pull(func, hour: int = 12, minute: int = 0):
    """Schedule daily job discovery at the specified UTC hour (8 AM ET = 12 UTC)."""
    scheduler = get_scheduler()
    job_id = "daily_job_pull"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
    scheduler.add_job(
        func,
        trigger=CronTrigger(hour=hour, minute=minute),
        id=job_id,
        name="Daily Job Discovery",
        replace_existing=True,
    )
    log.info("scheduled_daily_pull", hour=hour, minute=minute)


def schedule_followup(func, job_id: str, delay_days: int, followup_num: int, **kwargs):
    """Schedule a follow-up email."""
    scheduler = get_scheduler()
    run_date = datetime.now(timezone.utc) + timedelta(days=delay_days)
    sched_id = f"followup_{job_id}_{followup_num}"

    if scheduler.get_job(sched_id):
        scheduler.remove_job(sched_id)

    scheduler.add_job(
        func,
        trigger=DateTrigger(run_date=run_date),
        id=sched_id,
        name=f"Follow-up {followup_num} for {job_id}",
        kwargs=kwargs,
        replace_existing=True,
    )
    log.info("scheduled_followup", job_id=job_id, followup=followup_num, run_date=run_date.isoformat())
    return sched_id


def cancel_followups(job_id: str):
    """Cancel all follow-ups for a given job."""
    scheduler = get_scheduler()
    for num in [1, 2]:
        sched_id = f"followup_{job_id}_{num}"
        if scheduler.get_job(sched_id):
            scheduler.remove_job(sched_id)
            log.info("cancelled_followup", sched_id=sched_id)


def schedule_reply_checker(func, interval_minutes: int = 30):
    """Schedule periodic reply checking."""
    scheduler = get_scheduler()
    job_id = "reply_checker"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
    scheduler.add_job(
        func,
        trigger=CronTrigger(minute=f"*/{interval_minutes}"),
        id=job_id,
        name="Reply Checker",
        replace_existing=True,
    )
    log.info("scheduled_reply_checker", interval_minutes=interval_minutes)


def get_scheduled_jobs() -> list[dict]:
    scheduler = get_scheduler()
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time) if job.next_run_time else "N/A",
        })
    return jobs
