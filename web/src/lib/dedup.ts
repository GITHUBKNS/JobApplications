import type { JobPosting } from "./types";

function normalizeCompany(name: string): string {
  return name
    .toLowerCase()
    .trim()
    .replace(/\s*(inc\.?|llc|ltd\.?|corp\.?|co\.?|,?\s*inc)\s*$/i, "")
    .replace(/[^a-z0-9\s]/g, "")
    .trim();
}

function normalizeTitle(title: string): string {
  return title
    .toLowerCase()
    .trim()
    .replace(/\s*[\(\[].*?[\)\]]/, "")
    .replace(/\s*[-–—].*$/, "")
    .replace(/\s+/g, " ")
    .trim();
}

function similarity(a: string, b: string): number {
  if (a === b) return 100;
  if (!a || !b) return 0;

  const longer = a.length > b.length ? a : b;
  const shorter = a.length > b.length ? b : a;

  if (longer.length === 0) return 100;

  const costs: number[] = [];
  for (let i = 0; i <= longer.length; i++) {
    let lastValue = i;
    for (let j = 0; j <= shorter.length; j++) {
      if (i === 0) {
        costs[j] = j;
      } else if (j > 0) {
        let newValue = costs[j - 1];
        if (longer[i - 1] !== shorter[j - 1]) {
          newValue = Math.min(Math.min(newValue, lastValue), costs[j]) + 1;
        }
        costs[j - 1] = lastValue;
        lastValue = newValue;
      }
    }
    if (i > 0) costs[shorter.length] = lastValue;
  }

  return ((longer.length - costs[shorter.length]) / longer.length) * 100;
}

export function areDuplicates(a: JobPosting, b: JobPosting): boolean {
  const companySim = similarity(normalizeCompany(a.company), normalizeCompany(b.company));
  if (companySim < 70) return false;
  const titleSim = similarity(normalizeTitle(a.title), normalizeTitle(b.title));
  return titleSim >= 85;
}

export function deduplicate(jobs: JobPosting[]): JobPosting[] {
  if (!jobs.length) return [];
  const unique: JobPosting[] = [];
  for (const job of jobs) {
    if (!unique.some((existing) => areDuplicates(job, existing))) {
      unique.push(job);
    }
  }
  return unique;
}
