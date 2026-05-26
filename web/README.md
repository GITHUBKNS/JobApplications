# Job Application Copilot — Web (Vercel + Supabase)

A production-ready Next.js web app that deploys to **Vercel** with **Supabase** (PostgreSQL) as the database. Rebuilt from the Streamlit prototype for live deployment.

## Deploy to Vercel

### 1. Create a Supabase project

1. Go to [supabase.com](https://supabase.com) and create a new project
2. In the SQL Editor, run the contents of `supabase/schema.sql` to create all tables
3. Copy your project URL and keys from Settings > API

### 2. Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/GITHUBKNS/JobApplications/tree/main/web)

Or manually:

```bash
cd web
npx vercel
```

### 3. Set environment variables

In your Vercel project settings (Settings > Environment Variables), add:

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_SUPABASE_URL` | Yes | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Yes | Supabase anonymous key |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Supabase service role key (server-side only) |
| `ANTHROPIC_API_KEY` | Yes* | Claude API key for AI features |
| `OPENAI_API_KEY` | Yes* | GPT-4o fallback (*at least one LLM key required) |
| `JSEARCH_API_KEY` | No | RapidAPI JSearch for job discovery |
| `ADZUNA_APP_ID` | No | Adzuna job search |
| `ADZUNA_API_KEY` | No | Adzuna job search |
| `HUNTER_API_KEY` | No | Hunter.io email finding |
| `APOLLO_API_KEY` | No | Apollo.io email finding |
| `NEVERBOUNCE_API_KEY` | No | Email verification |
| `TAVILY_API_KEY` | No | Company news search |

## Local Development

```bash
cp .env.local.example .env.local
# Fill in your keys
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Tech Stack

- **Next.js 15** (App Router) + TypeScript
- **Tailwind CSS** + Radix UI primitives
- **Supabase** (PostgreSQL + real-time)
- **Anthropic Claude** / **OpenAI GPT-4o** via direct SDK
- **Vercel** serverless functions (60s timeout for AI calls)

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Dashboard | `/` | Overview + quick-start guide |
| Search Jobs | `/jobs` | Multi-source job discovery with filters |
| Resume Tailoring | `/resume` | ATS scoring + auto-tailor keywords |
| Cover Letter | `/cover-letter` | AI-generated cover letters |
| Apply | `/apply` | Autofill payloads + mark as applied |
| Find Recruiter | `/recruiter` | Hunter.io + Apollo email finding |
| Cold Email | `/email` | A/B subject lines, email generation |
| Analytics | `/analytics` | Funnel, weekly trends, response rates |
| Settings | `/settings` | Resume upload, API key status |

## Database Schema

See `supabase/schema.sql` for the complete schema including:
- `jobs` — discovered job postings
- `resumes` — parsed master resume(s)
- `applications` — application tracking with status enum
- `emails` — sent email records
- `followups` — follow-up schedule
- `errors` — error logging
