import { NextRequest, NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { generateJSON } from "@/lib/llm";
import type { MasterResume } from "@/lib/types";

const PARSE_SYSTEM_PROMPT = `You are an expert resume parser. Extract structured data from the resume text below.
Return a JSON object with these exact keys:
{
  "contact": {"name","email","phone","location","linkedin","github","website"},
  "summary": "professional summary string",
  "skills": ["skill1","skill2",...],
  "experience": [{"company","title","location","start_date","end_date","bullets":["..."]}],
  "education": [{"institution","degree","field","start_date","end_date","gpa"}],
  "projects": [{"name","description","technologies":["..."],"url"}],
  "certifications": ["cert1","cert2"]
}
Be thorough. Parse every section. Use empty strings for missing fields, empty arrays for missing lists.`;

export async function POST(req: NextRequest) {
  const { text } = await req.json();
  if (!text) return NextResponse.json({ error: "No text provided" }, { status: 400 });

  try {
    const resume = await generateJSON<MasterResume>(
      PARSE_SYSTEM_PROMPT,
      `Parse this resume:\n\n${text}`
    );

    const supabase = createAdminClient();
    await supabase.from("resumes").update({ is_active: false }).eq("is_active", true);
    const { error } = await supabase.from("resumes").insert({ data: resume, is_active: true });
    if (error) console.error("Resume save error:", error.message);

    return NextResponse.json({ resume });
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
