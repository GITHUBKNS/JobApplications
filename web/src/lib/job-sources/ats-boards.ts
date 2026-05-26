import type { JobPosting } from "../types";

function keywordMatch(text: string, keyword: string): boolean {
  const lc = keyword.toLowerCase();
  return lc.split(/\s+/).some((part) => text.toLowerCase().includes(part));
}

export async function searchGreenhouse(slug: string, keyword = "data engineer"): Promise<JobPosting[]> {
  try {
    const resp = await fetch(`https://boards-api.greenhouse.io/v1/boards/${slug}/jobs`);
    if (!resp.ok) return [];
    const data = await resp.json();
    return (data.jobs || [])
      .filter((j: Record<string, unknown>) => keywordMatch((j.title as string) || "", keyword))
      .map((j: Record<string, unknown>) => ({
        id: `gh_${slug}_${j.id}`,
        title: (j.title as string) || "",
        company: slug,
        location: (j.location as Record<string, string>)?.name || "",
        remote: ((j.location as Record<string, string>)?.name || "").toLowerCase().includes("remote"),
        posted_at: (j.updated_at as string) || null,
        source: "greenhouse",
        url: (j.absolute_url as string) || "",
        jd_text: (j.content as string) || "",
        salary: "",
        visa_signal: "unknown",
        company_domain: "",
        raw_data: j,
      }));
  } catch {
    return [];
  }
}

export async function searchLever(slug: string, keyword = "data engineer"): Promise<JobPosting[]> {
  try {
    const resp = await fetch(`https://api.lever.co/v0/postings/${slug}`);
    if (!resp.ok) return [];
    const data = await resp.json();
    const items = Array.isArray(data) ? data : data.postings || data.results || [];
    return items
      .filter((j: Record<string, unknown>) => keywordMatch((j.text as string) || "", keyword))
      .map((j: Record<string, unknown>) => {
        const cats = (j.categories as Record<string, string>) || {};
        return {
          id: `lever_${slug}_${j.id || ""}`,
          title: (j.text as string) || "",
          company: slug,
          location: cats.location || "",
          remote: (cats.location || "").toLowerCase().includes("remote"),
          posted_at: j.createdAt ? new Date(j.createdAt as number).toISOString() : null,
          source: "lever",
          url: (j.hostedUrl as string) || "",
          jd_text: (j.descriptionPlain as string) || (j.description as string) || "",
          salary: "",
          visa_signal: "unknown",
          company_domain: "",
          raw_data: j,
        };
      });
  } catch {
    return [];
  }
}

export async function searchAshby(slug: string, keyword = "data engineer"): Promise<JobPosting[]> {
  try {
    const resp = await fetch(`https://api.ashbyhq.com/posting-api/job-board/${slug}`);
    if (!resp.ok) return [];
    const data = await resp.json();
    return (data.jobs || [])
      .filter((j: Record<string, unknown>) => keywordMatch((j.title as string) || "", keyword))
      .map((j: Record<string, unknown>) => ({
        id: `ashby_${slug}_${j.id || ""}`,
        title: (j.title as string) || "",
        company: slug,
        location: (j.location as string) || "",
        remote: ((j.location as string) || "").toLowerCase().includes("remote"),
        posted_at: null,
        source: "ashby",
        url: (j.jobUrl as string) || "",
        jd_text: (j.descriptionPlain as string) || (j.descriptionHtml as string) || "",
        salary: "",
        visa_signal: "unknown",
        company_domain: "",
        raw_data: j,
      }));
  } catch {
    return [];
  }
}
