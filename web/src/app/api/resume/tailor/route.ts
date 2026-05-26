import { NextRequest, NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { generateJSON } from "@/lib/llm";
import type { MasterResume } from "@/lib/types";

const TAILOR_PROMPT = `You are an expert resume writer optimizing for ATS systems.
Given the master resume and a target job description, rewrite ONLY the experience bullets
to better match the job requirements.

HARD RULES:
- Only rephrase or re-emphasize existing experience. Never invent employers, dates, or skills not in the master resume.
- Surface relevant keywords naturally in bullet points.
- Keep bullets concise and impact-focused (action verb + result + metric where possible).
- Maintain truthfulness — never fabricate experience.

Return a JSON object with the same structure as the input resume, with modified experience bullets.`;

export async function POST(req: NextRequest) {
  const { resume, jdText, jobId } = await req.json() as {
    resume: MasterResume; jdText: string; jobId: string;
  };

  try {
    const tailored = await generateJSON<MasterResume>(
      TAILOR_PROMPT,
      `Master Resume:\n${JSON.stringify(resume)}\n\nTarget Job Description:\n${jdText}`,
      8192
    );

    if (jobId) {
      const supabase = createAdminClient();
      await supabase
        .from("applications")
        .upsert({
          job_id: jobId,
          tailored_resume: tailored,
          updated_at: new Date().toISOString(),
        }, { onConflict: "job_id" });
    }

    return NextResponse.json({ tailored });
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
