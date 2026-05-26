import { NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";

export async function GET() {
  const supabase = createAdminClient();

  const [jobsRes, appsRes, emailsRes] = await Promise.all([
    supabase.from("jobs").select("id, source, company, created_at"),
    supabase.from("applications").select("*, jobs(title, company)").order("created_at", { ascending: false }),
    supabase.from("emails").select("*").order("created_at", { ascending: false }),
  ]);

  return NextResponse.json({
    jobs: jobsRes.data || [],
    applications: appsRes.data || [],
    emails: emailsRes.data || [],
  });
}
