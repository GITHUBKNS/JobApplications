import { NextRequest, NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { discoverJobs, type DiscoveryParams } from "@/lib/job-sources";

export const maxDuration = 60;

export async function GET() {
  const supabase = createAdminClient();
  const { data, error } = await supabase
    .from("jobs")
    .select("*")
    .order("created_at", { ascending: false })
    .limit(200);

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json({ jobs: data });
}

export async function POST(req: NextRequest) {
  const body = await req.json() as DiscoveryParams;
  const supabase = createAdminClient();

  try {
    const jobs = await discoverJobs(body);

    if (jobs.length > 0) {
      const rows = jobs.map((j) => ({
        id: j.id,
        title: j.title,
        company: j.company,
        location: j.location,
        remote: j.remote,
        posted_at: j.posted_at,
        source: j.source,
        url: j.url,
        jd_text: j.jd_text,
        salary: j.salary,
        visa_signal: j.visa_signal,
        company_domain: j.company_domain,
        raw_data: j.raw_data,
      }));

      const { error } = await supabase.from("jobs").upsert(rows, { onConflict: "id" });
      if (error) console.error("Jobs upsert error:", error.message);
    }

    return NextResponse.json({ jobs, count: jobs.length });
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
