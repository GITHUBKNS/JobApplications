-- Job Application Copilot — Supabase schema

-- Jobs discovered from various sources
create table if not exists jobs (
  id text primary key,
  title text not null,
  company text not null,
  location text default '',
  remote boolean default false,
  posted_at timestamptz,
  source text default '',
  url text default '',
  jd_text text default '',
  salary text default '',
  visa_signal text default 'unknown',
  company_domain text default '',
  raw_data jsonb default '{}',
  created_at timestamptz default now()
);

create index if not exists idx_jobs_company on jobs(company);
create index if not exists idx_jobs_source on jobs(source);
create index if not exists idx_jobs_created on jobs(created_at desc);

-- Master resume (single-user, one active row)
create table if not exists resumes (
  id uuid primary key default gen_random_uuid(),
  data jsonb not null,
  pdf_url text default '',
  is_active boolean default true,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Applications tracking
create type application_status as enum (
  'Saved', 'Applied', 'Email Sent', 'Followup1 Sent', 'Followup2 Sent',
  'Recruiter Replied', 'Interview', 'Offer', 'Rejected', 'Ghosted'
);

create table if not exists applications (
  id uuid primary key default gen_random_uuid(),
  job_id text references jobs(id) on delete cascade,
  status application_status default 'Saved',
  applied_at timestamptz,
  resume_url text default '',
  cover_letter_url text default '',
  cover_letter_text text default '',
  tailored_resume jsonb,
  recruiter_name text default '',
  recruiter_email text default '',
  thread_id text default '',
  last_email_at timestamptz,
  notes text default '',
  autofill_payload jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  unique(job_id)
);

create index if not exists idx_applications_status on applications(status);
create index if not exists idx_applications_job on applications(job_id);

-- Emails sent
create table if not exists emails (
  id uuid primary key default gen_random_uuid(),
  job_id text references jobs(id) on delete cascade,
  application_id uuid references applications(id) on delete cascade,
  to_email text not null,
  to_name text default '',
  subject text not null,
  body text not null,
  sent_at timestamptz default now(),
  gmail_thread_id text default '',
  gmail_message_id text default '',
  email_type text default 'cold' check (email_type in ('cold', 'followup1', 'followup2')),
  status text default 'sent',
  created_at timestamptz default now()
);

create index if not exists idx_emails_job on emails(job_id);
create index if not exists idx_emails_type on emails(email_type);

-- Follow-up schedule
create table if not exists followups (
  id uuid primary key default gen_random_uuid(),
  job_id text references jobs(id) on delete cascade,
  email_type text not null,
  scheduled_at timestamptz not null,
  sent_at timestamptz,
  cancelled boolean default false,
  cancel_reason text default '',
  created_at timestamptz default now()
);

-- Errors log
create table if not exists errors (
  id uuid primary key default gen_random_uuid(),
  component text not null,
  error text not null,
  details text default '',
  created_at timestamptz default now()
);

-- Analytics cache (materialized metrics)
create table if not exists analytics_cache (
  metric text primary key,
  value jsonb not null,
  updated_at timestamptz default now()
);

-- Enable Row Level Security (disabled for single-user; enable if adding auth)
-- alter table jobs enable row level security;
-- alter table applications enable row level security;
-- alter table emails enable row level security;
