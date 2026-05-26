# Job Application Copilot

A personal job-application copilot built as a single-user Streamlit web dashboard. It discovers fresh Data Engineer jobs, tailors your resume, generates cover letters, finds recruiter emails, sends personalized cold outreach, and tracks everything in Google Sheets.

**Important:** This tool does NOT auto-submit applications. It prepares tailored PDFs and opens the application URL for you to submit manually.

## Features

1. **Job Discovery** — Multi-source aggregation from JSearch, Adzuna, Greenhouse, Lever, Ashby, Workable, SmartRecruiters
2. **Resume Tailoring** — ATS scoring (0–100) + keyword-optimized resume via Claude/GPT-4o
3. **Cover Letters** — AI-generated, personalized cover letters with company news hooks
4. **Autofill Payloads** — Pre-filled application answers ready to paste
5. **Recruiter Discovery** — Waterfall email finding via Hunter.io → Apollo → RocketReach with verification
6. **Cold Email Outreach** — Gmail API sending with CAN-SPAM compliance, A/B subject lines
7. **Follow-up Cadence** — Automated Day 3 and Day 7 follow-ups with reply detection
8. **Analytics Dashboard** — Funnel charts, response rates, weekly trends via Plotly

## Tech Stack

- **Language:** Python 3.11+
- **UI:** Streamlit (multipage app)
- **LLMs:** Anthropic Claude (Sonnet 4) primary, OpenAI GPT-4o fallback
- **Storage:** Google Sheets (system of record) + SQLite (local cache)
- **Email:** Gmail API via OAuth2
- **PDF:** WeasyPrint + Jinja2
- **Scheduler:** APScheduler
- **Logging:** structlog

## Quick Start

```bash
# Clone and enter the project
cd job_copilot

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and fill in your API keys
cp .env.example .env
# Edit .env with your keys

# Add Google service account JSON
mkdir -p secrets
# Place service_account.json in secrets/

# Run the app
streamlit run app/streamlit_app.py
```

## Configuration

All secrets are managed via `.env` file. See `.env.example` for all available keys.

### Required for core functionality:
- `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` — at least one LLM provider
- `GOOGLE_SERVICE_ACCOUNT_FILE` — for Google Sheets integration

### Optional (app degrades gracefully without these):
- `JSEARCH_API_KEY` — RapidAPI JSearch for job discovery
- `ADZUNA_APP_ID` / `ADZUNA_API_KEY` — Adzuna job search
- `HUNTER_API_KEY` — Hunter.io email finding
- `APOLLO_API_KEY` — Apollo.io email finding
- `ROCKETREACH_API_KEY` — RocketReach email finding
- `NEVERBOUNCE_API_KEY` — Email verification
- `ZEROBOUNCE_API_KEY` — Email verification fallback
- `TAVILY_API_KEY` — Company news search
- `GMAIL_OAUTH_CLIENT_ID` / `GMAIL_OAUTH_CLIENT_SECRET` — Gmail sending

## Project Structure

```
job_copilot/
  app/
    pages/           # Streamlit pages (8 pages)
    core/            # Business logic
    integrations/    # API clients (one per provider)
    models/          # Pydantic schemas
    templates/       # Jinja2 HTML templates for PDF
    db/              # SQLite cache + Google Sheets adapter
  tests/             # pytest test suite
  output/            # Generated PDFs (gitignored)
  secrets/           # Service account + OAuth tokens (gitignored)
  .env.example       # Template for environment variables
  requirements.txt   # Python dependencies
```

## Running Tests

```bash
cd job_copilot
pytest tests/ -v
```

## Compliance

- Never auto-submits job applications
- All cold emails include CAN-SPAM footer (physical address + unsubscribe)
- Daily email send cap: 20 (configurable, max 40)
- LinkedIn scraping rate-limited (1 req / 8s) using own session
- Honors robots.txt where reasonable

## Changelog

### v0.1.0 — Initial Release
- Full project scaffold with 8-page Streamlit app
- Settings page with resume upload, parsing, and Google Sheets bootstrap
- Job discovery pipeline with multi-source aggregation and visa filtering
- Resume tailoring with ATS scoring and PDF rendering
- Cover letter generation with company news personalization
- Application autofill payload generation
- Recruiter discovery with email verification waterfall
- Cold email generation and Gmail API sending
- Follow-up cadence scheduling with reply detection
- Analytics dashboard with Plotly charts
