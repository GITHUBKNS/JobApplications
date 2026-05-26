export interface ContactInfo {
  name: string;
  email: string;
  phone: string;
  location: string;
  linkedin: string;
  github: string;
  website: string;
}

export interface Experience {
  company: string;
  title: string;
  location: string;
  start_date: string;
  end_date: string;
  bullets: string[];
}

export interface Education {
  institution: string;
  degree: string;
  field: string;
  start_date: string;
  end_date: string;
  gpa: string;
}

export interface Project {
  name: string;
  description: string;
  technologies: string[];
  url: string;
}

export interface MasterResume {
  contact: ContactInfo;
  summary: string;
  skills: string[];
  experience: Experience[];
  education: Education[];
  projects: Project[];
  certifications: string[];
}

export interface JobPosting {
  id: string;
  title: string;
  company: string;
  location: string;
  remote: boolean;
  posted_at: string | null;
  source: string;
  url: string;
  jd_text: string;
  salary: string;
  visa_signal: string;
  company_domain: string;
  raw_data: Record<string, unknown>;
  created_at?: string;
}

export interface ATSAnalysis {
  score: number;
  matched_keywords: string[];
  missing_keywords: string[];
  suggestions: string[];
  jd_skills: string[];
  jd_tools: string[];
  jd_yoe_signals: string[];
}

export type ApplicationStatus =
  | "Saved"
  | "Applied"
  | "Email Sent"
  | "Followup1 Sent"
  | "Followup2 Sent"
  | "Recruiter Replied"
  | "Interview"
  | "Offer"
  | "Rejected"
  | "Ghosted";

export interface Application {
  id: string;
  job_id: string;
  status: ApplicationStatus;
  applied_at: string | null;
  resume_url: string;
  cover_letter_url: string;
  cover_letter_text: string;
  tailored_resume: MasterResume | null;
  recruiter_name: string;
  recruiter_email: string;
  thread_id: string;
  last_email_at: string | null;
  notes: string;
  autofill_payload: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
  jobs?: JobPosting;
}

export interface EmailRecord {
  id: string;
  job_id: string;
  application_id: string;
  to_email: string;
  to_name: string;
  subject: string;
  body: string;
  sent_at: string;
  gmail_thread_id: string;
  gmail_message_id: string;
  email_type: "cold" | "followup1" | "followup2";
  status: string;
}

export interface RecruiterCandidate {
  name: string;
  email: string;
  title: string;
  company: string;
  linkedin_url: string;
  source: string;
  confidence: number;
  verified: boolean;
  verification_result: string;
}

export interface AutofillPayload {
  full_name: string;
  email: string;
  phone: string;
  linkedin: string;
  website: string;
  years_experience: Record<string, number>;
  work_authorization: string;
  sponsorship_needed: string;
  willing_to_relocate: string;
  salary_expectation: string;
  start_date: string;
}
