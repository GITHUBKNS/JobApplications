<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

## Cursor Cloud specific instructions

### Project overview
This is a **Next.js 16 App Router** application in `web/`. It uses **Supabase** (PostgreSQL) as the database and **Anthropic Claude / OpenAI GPT-4o** as LLM providers. See `web/README.md` for the full page list and env var table.

### Running locally
- **Dev server:** `npm run dev` (from `web/`; runs on port 3000)
- **Lint:** `npm run lint`
- **Build:** `npm run build`
- **Database:** Requires a running Supabase instance. For local development, install the Supabase CLI and run `supabase start` from `web/`. Apply `supabase/schema.sql` if not using the migration in `supabase/migrations/`.

### Environment variables
Create `web/.env.local` with at minimum:
- `NEXT_PUBLIC_SUPABASE_URL` — Supabase project URL (e.g. `http://127.0.0.1:54321` for local)
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` — Supabase anon/publishable key
- `SUPABASE_SERVICE_ROLE_KEY` — Supabase service role/secret key

LLM keys (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`) are needed for AI features but the app starts and most pages work without them. Job discovery from public ATS boards (Greenhouse, Lever, Ashby) works without any API keys.

### Gotchas
- The Supabase CLI v2.101+ ships as two binaries (`supabase` + `supabase-go`). When running with `sudo`, set `SUPABASE_GO_BINARY` explicitly or use the full path.
- Docker is required for `supabase start`. The VM needs `fuse-overlayfs` + `iptables-legacy` for nested Docker (see system prompt for details).
- ESLint reports 1 pre-existing error (`react-hooks/immutability` in `src/app/jobs/page.tsx`) and ~13 warnings. These are in the existing codebase and are not blockers for development.
