import { NextRequest, NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { generateJSON } from "@/lib/llm";
import type { MasterResume } from "@/lib/types";

const COLD_EMAIL_PROMPT = `You are an expert cold email copywriter for job applications.
Requirements:
- Subject line: create 2 A/B variants, short and compelling
- Body: under 120 words total
- Include ONE specific personalization hook
- Soft CTA
- Professional but human tone
- Do NOT include attachments inline

Return JSON:
{"subject_a":"...","subject_b":"...","body":"email body (use \\n for paragraphs)"}`;

export async function POST(req: NextRequest) {
  const {
    resume, jdText, company, jobTitle,
    recruiterName, companyNews, jobId, action,
    to, subject, body,
  } = await req.json() as {
    resume?: MasterResume; jdText?: string; company: string; jobTitle: string;
    recruiterName?: string; companyNews?: string; jobId: string;
    action: "generate" | "record";
    to?: string; subject?: string; body?: string;
  };

  const supabase = createAdminClient();

  if (action === "generate") {
    try {
      const userMsg = `Generate a cold email for:
Company: ${company}
Role: ${jobTitle}
Recruiter: ${recruiterName || "Hiring Team"}
Candidate: ${resume?.contact?.name || "Candidate"}
Personalization: ${companyNews || "Use role and company details."}
JD excerpt: ${(jdText || "").slice(0, 2000)}
Skills: ${(resume?.skills || []).slice(0, 15).join(", ")}
Recent Role: ${resume?.experience?.[0] ? `${resume.experience[0].title} at ${resume.experience[0].company}` : "N/A"}`;

      const result = await generateJSON<{ subject_a: string; subject_b: string; body: string }>(
        COLD_EMAIL_PROMPT, userMsg, 2048, 0.6
      );
      return NextResponse.json(result);
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      return NextResponse.json({ error: msg }, { status: 500 });
    }
  }

  if (action === "record" && to && subject && body) {
    const { error } = await supabase.from("emails").insert({
      job_id: jobId,
      to_email: to,
      to_name: recruiterName || "",
      subject,
      body,
      email_type: "cold",
      status: "sent",
    });

    if (!error) {
      await supabase
        .from("applications")
        .upsert({
          job_id: jobId,
          status: "Email Sent",
          last_email_at: new Date().toISOString(),
          recruiter_email: to,
          recruiter_name: recruiterName || "",
          updated_at: new Date().toISOString(),
        }, { onConflict: "job_id" });
    }

    return NextResponse.json({ success: !error });
  }

  return NextResponse.json({ error: "Invalid action" }, { status: 400 });
}
