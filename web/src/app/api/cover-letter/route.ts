import { NextRequest, NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { generate } from "@/lib/llm";
import type { MasterResume } from "@/lib/types";

const COVER_LETTER_PROMPT = `You are an expert career coach writing a cover letter.
Requirements:
- Professional, concise tone
- Exactly 3 short paragraphs, approximately 250 words total
- Paragraph 1: Hook — mention the specific role and one reason you're excited
- Paragraph 2: Value — connect 2-3 experiences/skills from resume to JD
- Paragraph 3: Close — express enthusiasm, soft CTA
- If a personalization hook is provided, weave it into paragraph 1
- Do NOT use clichés like "I am writing to express my interest"
- Sign off with the candidate's name
Return ONLY the cover letter text.`;

export async function POST(req: NextRequest) {
  const { resume, jdText, company, jobTitle, companyNews, recruiterName, jobId } =
    await req.json() as {
      resume: MasterResume; jdText: string; company: string;
      jobTitle: string; companyNews?: string; recruiterName?: string;
      jobId?: string;
    };

  try {
    const userMsg = `Generate a cover letter for:
Company: ${company}
Role: ${jobTitle}
${recruiterName ? `Addressed to: ${recruiterName}` : ""}
${companyNews ? `Company News: ${companyNews}` : ""}

Job Description:\n${jdText.slice(0, 3000)}

Candidate Resume:\n${JSON.stringify(resume).slice(0, 3000)}`;

    const letter = await generate(COVER_LETTER_PROMPT, userMsg, 1500, 0.5);

    if (jobId) {
      const supabase = createAdminClient();
      await supabase
        .from("applications")
        .upsert({
          job_id: jobId,
          cover_letter_text: letter,
          updated_at: new Date().toISOString(),
        }, { onConflict: "job_id" });
    }

    return NextResponse.json({ letter });
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
