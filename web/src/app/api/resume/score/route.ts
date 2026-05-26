import { NextRequest, NextResponse } from "next/server";
import { generateJSON } from "@/lib/llm";
import type { ATSAnalysis, MasterResume } from "@/lib/types";

const JD_ANALYSIS_PROMPT = `You are an expert ATS analyst. Analyze the job description and extract:
Return JSON: {"hard_skills":[],"tools":[],"keywords":[],"yoe_signals":[],"soft_skills":[]}`;

const ATS_SCORE_PROMPT = `You are an ATS scoring expert. Compare resume against job requirements.
Return JSON: {"score":0-100,"matched_keywords":[],"missing_keywords":[],"suggestions":[]}`;

export async function POST(req: NextRequest) {
  const { resume, jdText } = await req.json() as { resume: MasterResume; jdText: string };

  try {
    const jdAnalysis = await generateJSON<Record<string, string[]>>(
      JD_ANALYSIS_PROMPT,
      `Analyze this job description:\n\n${jdText}`
    );

    const scoring = await generateJSON<ATSAnalysis>(
      ATS_SCORE_PROMPT,
      `JD Analysis:\n${JSON.stringify(jdAnalysis)}\n\nResume:\n${JSON.stringify(resume)}`
    );

    return NextResponse.json({
      ...scoring,
      jd_skills: jdAnalysis.hard_skills || [],
      jd_tools: jdAnalysis.tools || [],
      jd_yoe_signals: jdAnalysis.yoe_signals || [],
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
