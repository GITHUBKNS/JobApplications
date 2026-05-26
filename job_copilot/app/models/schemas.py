"""Pydantic models for all domain objects."""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Resume ──────────────────────────────────────────────────────────────────

class ContactInfo(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    github: str = ""
    website: str = ""


class Experience(BaseModel):
    company: str
    title: str
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    bullets: list[str] = Field(default_factory=list)


class Education(BaseModel):
    institution: str
    degree: str
    field: str = ""
    start_date: str = ""
    end_date: str = ""
    gpa: str = ""


class Project(BaseModel):
    name: str
    description: str = ""
    technologies: list[str] = Field(default_factory=list)
    url: str = ""


class MasterResume(BaseModel):
    contact: ContactInfo = Field(default_factory=ContactInfo)
    summary: str = ""
    skills: list[str] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)


# ── Job Posting ─────────────────────────────────────────────────────────────

class JobPosting(BaseModel):
    id: str
    title: str
    company: str
    location: str = ""
    remote: bool = False
    posted_at: Optional[datetime] = None
    source: str = ""
    url: str = ""
    jd_text: str = ""
    salary: str = ""
    visa_sponsorship_signal: Optional[str] = None
    company_domain: str = ""
    raw_data: dict = Field(default_factory=dict)


# ── ATS Analysis ────────────────────────────────────────────────────────────

class ATSAnalysis(BaseModel):
    score: int = 0
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    jd_skills: list[str] = Field(default_factory=list)
    jd_tools: list[str] = Field(default_factory=list)
    jd_yoe_signals: list[str] = Field(default_factory=list)


# ── Application Status ──────────────────────────────────────────────────────

class ApplicationStatus(str, enum.Enum):
    SAVED = "Saved"
    APPLIED = "Applied"
    EMAIL_SENT = "Email Sent"
    FOLLOWUP1_SENT = "Followup1 Sent"
    FOLLOWUP2_SENT = "Followup2 Sent"
    RECRUITER_REPLIED = "Recruiter Replied"
    INTERVIEW = "Interview"
    OFFER = "Offer"
    REJECTED = "Rejected"
    GHOSTED = "Ghosted"


class Application(BaseModel):
    job_id: str
    company: str
    title: str
    status: ApplicationStatus = ApplicationStatus.SAVED
    applied_at: Optional[datetime] = None
    resume_path: str = ""
    cover_letter_path: str = ""
    recruiter_name: str = ""
    recruiter_email: str = ""
    thread_id: str = ""
    last_email_at: Optional[datetime] = None
    notes: str = ""


# ── Email ────────────────────────────────────────────────────────────────────

class EmailRecord(BaseModel):
    job_id: str
    to_email: str
    to_name: str = ""
    subject: str
    body: str
    sent_at: Optional[datetime] = None
    gmail_thread_id: str = ""
    gmail_message_id: str = ""
    email_type: str = "cold"  # cold | followup1 | followup2
    status: str = "sent"


# ── Recruiter Candidate ─────────────────────────────────────────────────────

class RecruiterCandidate(BaseModel):
    name: str
    email: str = ""
    title: str = ""
    company: str = ""
    linkedin_url: str = ""
    source: str = ""
    confidence: float = 0.0
    verified: bool = False
    verification_result: str = ""


# ── Autofill Payload ────────────────────────────────────────────────────────

class AutofillPayload(BaseModel):
    full_name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    website: str = ""
    years_experience: dict[str, int] = Field(default_factory=dict)
    work_authorization: str = "Require sponsorship"
    sponsorship_needed: str = "Yes"
    willing_to_relocate: str = "Yes"
    salary_expectation: str = ""
    start_date: str = "2 weeks notice"
    cover_letter_text: str = ""
