import type { JobPosting } from "../types";

export async function searchJSearch(
  query = "Data Engineer",
  location = "United States",
  postedWithinDays = 7
): Promise<JobPosting[]> {
  const apiKey = process.env.JSEARCH_API_KEY;
  if (!apiKey) return [];

  const datePosted = postedWithinDays <= 7 ? "week" : "month";
  const params = new URLSearchParams({
    query: `${query} in ${location}`,
    page: "1",
    num_pages: "3",
    date_posted: datePosted,
    remote_jobs_only: "false",
  });

  try {
    const resp = await fetch(`https://jsearch.p.rapidapi.com/search?${params}`, {
      headers: {
        "X-RapidAPI-Key": apiKey,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
      },
    });
    if (!resp.ok) return [];
    const data = await resp.json();
    return (data.data || []).map(normalize);
  } catch {
    return [];
  }
}

function normalize(item: Record<string, unknown>): JobPosting {
  const minSal = item.job_min_salary as number | undefined;
  const maxSal = item.job_max_salary as number | undefined;
  let salary = "";
  if (minSal && maxSal) salary = `$${minSal.toLocaleString()} - $${maxSal.toLocaleString()}`;
  else if (minSal) salary = `$${minSal.toLocaleString()}+`;

  return {
    id: `jsearch_${item.job_id || ""}`,
    title: (item.job_title as string) || "",
    company: (item.employer_name as string) || "",
    location: `${item.job_city || ""}, ${item.job_state || ""}`.replace(/^, |, $/g, ""),
    remote: Boolean(item.job_is_remote),
    posted_at: (item.job_posted_at_datetime_utc as string) || null,
    source: "jsearch",
    url: (item.job_apply_link as string) || (item.job_google_link as string) || "",
    jd_text: (item.job_description as string) || "",
    salary,
    visa_signal: "unknown",
    company_domain: (item.employer_website as string) || "",
    raw_data: item,
  };
}
