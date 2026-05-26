import type { JobPosting } from "../types";
import { classifyVisaSignal, shouldFilterOut } from "../visa-classifier";
import { deduplicate } from "../dedup";
import { searchJSearch } from "./jsearch";
import { searchAdzuna } from "./adzuna";
import { searchGreenhouse, searchLever, searchAshby } from "./ats-boards";

const DEFAULT_ATS_COMPANIES = [
  "stripe", "datadog", "figma", "notion", "plaid", "reddit",
  "coinbase", "ramp", "brex", "dbt-labs", "databricks",
  "snowflake", "confluent", "elastic", "mongodb",
];

export interface DiscoveryParams {
  keywords?: string[];
  locations?: string[];
  postedWithinDays?: number;
  requireVisaSponsorship?: boolean;
  atsCompanies?: string[];
}

export async function discoverJobs(params: DiscoveryParams = {}): Promise<JobPosting[]> {
  const {
    keywords = ["Data Engineer", "Analytics Engineer"],
    locations = ["Newark, NJ", "Remote", "United States"],
    postedWithinDays = 7,
    requireVisaSponsorship = true,
    atsCompanies = DEFAULT_ATS_COMPANIES,
  } = params;

  const tasks: Promise<JobPosting[]>[] = [];

  for (const kw of keywords) {
    for (const loc of locations) {
      tasks.push(searchJSearch(kw, loc, postedWithinDays));
      tasks.push(searchAdzuna(kw, loc, postedWithinDays));
    }
  }

  for (const company of atsCompanies) {
    for (const kw of keywords) {
      tasks.push(searchGreenhouse(company, kw));
      tasks.push(searchLever(company, kw));
      tasks.push(searchAshby(company, kw));
    }
  }

  const results = await Promise.allSettled(tasks);
  let allJobs: JobPosting[] = [];

  for (const r of results) {
    if (r.status === "fulfilled" && Array.isArray(r.value)) {
      allJobs = allJobs.concat(r.value);
    }
  }

  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - postedWithinDays);

  const filtered = allJobs.filter((job) => {
    if (job.posted_at && new Date(job.posted_at) < cutoff) return false;
    if (shouldFilterOut(job.jd_text, requireVisaSponsorship)) return false;
    job.visa_signal = classifyVisaSignal(job.jd_text);
    return true;
  });

  return deduplicate(filtered);
}
