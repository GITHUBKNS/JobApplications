import type { JobPosting } from "../types";

export async function searchAdzuna(
  query = "Data Engineer",
  location = "New Jersey",
  postedWithinDays = 7
): Promise<JobPosting[]> {
  const appId = process.env.ADZUNA_APP_ID;
  const apiKey = process.env.ADZUNA_API_KEY;
  if (!appId || !apiKey) return [];

  const params = new URLSearchParams({
    app_id: appId,
    app_key: apiKey,
    results_per_page: "50",
    what: query,
    where: location,
    max_days_old: String(postedWithinDays),
    sort_by: "date",
    "content-type": "application/json",
  });

  try {
    const resp = await fetch(`https://api.adzuna.com/v1/api/jobs/us/search/1?${params}`);
    if (!resp.ok) return [];
    const data = await resp.json();
    return (data.results || []).map(normalize);
  } catch {
    return [];
  }
}

function normalize(item: Record<string, unknown>): JobPosting {
  const loc = item.location as Record<string, unknown> | undefined;
  const areas = (loc?.area as string[]) || [];
  const locationStr = areas.join(", ");
  const title = (item.title as string) || "";
  const desc = (item.description as string) || "";

  let salary = "";
  const minS = item.salary_min as number | undefined;
  const maxS = item.salary_max as number | undefined;
  if (minS && maxS) salary = `$${minS.toLocaleString()} - $${maxS.toLocaleString()}`;

  return {
    id: `adzuna_${item.id || ""}`,
    title,
    company: ((item.company as Record<string, string>)?.display_name) || "",
    location: locationStr,
    remote: title.toLowerCase().includes("remote") || desc.toLowerCase().includes("remote"),
    posted_at: (item.created as string) || null,
    source: "adzuna",
    url: (item.redirect_url as string) || "",
    jd_text: desc,
    salary,
    visa_signal: "unknown",
    company_domain: "",
    raw_data: item,
  };
}
