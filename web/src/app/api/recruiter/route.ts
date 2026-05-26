import { NextRequest, NextResponse } from "next/server";
import type { RecruiterCandidate } from "@/lib/types";

async function searchHunter(domain: string): Promise<RecruiterCandidate[]> {
  const key = process.env.HUNTER_API_KEY;
  if (!key || !domain) return [];

  try {
    const params = new URLSearchParams({ domain, api_key: key, limit: "10" });
    const resp = await fetch(`https://api.hunter.io/v2/domain-search?${params}`);
    if (!resp.ok) return [];
    const data = await resp.json();
    const titleKeywords = ["recruiter", "talent", "hr", "hiring", "engineering manager"];
    return (data.data?.emails || [])
      .filter((e: Record<string, string>) => {
        const pos = (e.position || "").toLowerCase();
        return titleKeywords.some((kw) => pos.includes(kw));
      })
      .map((e: Record<string, unknown>) => ({
        name: `${e.first_name || ""} ${e.last_name || ""}`.trim(),
        email: (e.value as string) || "",
        title: (e.position as string) || "",
        company: domain,
        linkedin_url: "",
        source: "hunter",
        confidence: ((e.confidence as number) || 0) / 100,
        verified: false,
        verification_result: "",
      }));
  } catch {
    return [];
  }
}

async function searchApollo(domain: string): Promise<RecruiterCandidate[]> {
  const key = process.env.APOLLO_API_KEY;
  if (!key || !domain) return [];

  try {
    const resp = await fetch("https://api.apollo.io/v1/mixed_people/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        api_key: key,
        q_organization_domains: domain,
        person_titles: ["Recruiter", "Talent Acquisition", "HR", "Hiring Manager"],
        per_page: 5,
      }),
    });
    if (!resp.ok) return [];
    const data = await resp.json();
    return (data.people || []).map((p: Record<string, unknown>) => ({
      name: (p.name as string) || "",
      email: (p.email as string) || "",
      title: (p.title as string) || "",
      company: ((p.organization as Record<string, string>)?.name) || "",
      linkedin_url: (p.linkedin_url as string) || "",
      source: "apollo",
      confidence: p.email ? 0.7 : 0.3,
      verified: false,
      verification_result: "",
    }));
  } catch {
    return [];
  }
}

export async function POST(req: NextRequest) {
  const { companyDomain, company } = await req.json() as { companyDomain: string; company: string };

  try {
    const [hunterResults, apolloResults] = await Promise.all([
      searchHunter(companyDomain),
      searchApollo(companyDomain),
    ]);

    const all = [...hunterResults, ...apolloResults];
    const seen = new Set<string>();
    const unique = all.filter((c) => {
      if (!c.email || seen.has(c.email.toLowerCase())) return false;
      seen.add(c.email.toLowerCase());
      return true;
    });

    unique.sort((a, b) => b.confidence - a.confidence);

    return NextResponse.json({ candidates: unique.slice(0, 10) });
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
