"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { Search, ExternalLink, MapPin, Building2, Bookmark } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import type { JobPosting } from "@/lib/types";

const VISA_BADGE: Record<string, { label: string; variant: "success" | "destructive" | "warning" }> = {
  positive: { label: "Sponsors", variant: "success" },
  reject: { label: "No Visa", variant: "destructive" },
  unknown: { label: "Unknown", variant: "warning" },
};

export default function JobsPage() {
  const [jobs, setJobs] = useState<JobPosting[]>([]);
  const [loading, setLoading] = useState(false);
  const [searching, setSearching] = useState(false);
  const [keywords, setKeywords] = useState("Data Engineer\nAnalytics Engineer");
  const [locations, setLocations] = useState("Newark, NJ\nRemote\nUnited States");
  const [days, setDays] = useState(7);
  const [visaFilter, setVisaFilter] = useState(true);

  useEffect(() => {
    loadCachedJobs();
  }, []);

  const loadCachedJobs = async () => {
    setLoading(true);
    try {
      const resp = await fetch("/api/jobs");
      const data = await resp.json();
      setJobs(data.jobs || []);
    } catch {
      toast.error("Failed to load jobs");
    } finally {
      setLoading(false);
    }
  };

  const searchJobs = async () => {
    setSearching(true);
    try {
      const resp = await fetch("/api/jobs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          keywords: keywords.split("\n").filter(Boolean),
          locations: locations.split("\n").filter(Boolean),
          postedWithinDays: days,
          requireVisaSponsorship: visaFilter,
        }),
      });
      const data = await resp.json();
      if (data.error) throw new Error(data.error);
      setJobs(data.jobs || []);
      toast.success(`Found ${data.count || 0} jobs`);
    } catch (e) {
      toast.error(`Search failed: ${e instanceof Error ? e.message : "Unknown error"}`);
    } finally {
      setSearching(false);
    }
  };

  const saveJob = async (job: JobPosting) => {
    const supabase = createClient();
    const { error } = await supabase.from("applications").upsert({
      job_id: job.id,
      status: "Saved",
    }, { onConflict: "job_id" });
    if (error) toast.error("Failed to save");
    else toast.success(`Saved ${job.title} at ${job.company}`);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Search Jobs</h1>
          <p className="text-zinc-500">Discover jobs across JSearch, Adzuna, Greenhouse, Lever, and more.</p>
        </div>
        <Button onClick={searchJobs} disabled={searching} size="lg">
          <Search className="mr-2 h-4 w-4" />
          {searching ? "Searching..." : "Search Now"}
        </Button>
      </div>

      <Card>
        <CardContent className="grid grid-cols-4 gap-4 pt-6">
          <div className="col-span-1">
            <label className="text-sm font-medium">Keywords (one per line)</label>
            <Textarea value={keywords} onChange={(e) => setKeywords(e.target.value)} rows={3} />
          </div>
          <div className="col-span-1">
            <label className="text-sm font-medium">Locations (one per line)</label>
            <Textarea value={locations} onChange={(e) => setLocations(e.target.value)} rows={3} />
          </div>
          <div>
            <label className="text-sm font-medium">Posted within (days)</label>
            <Input type="number" value={days} onChange={(e) => setDays(Number(e.target.value))} min={1} max={30} />
          </div>
          <div className="flex items-end">
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={visaFilter} onChange={(e) => setVisaFilter(e.target.checked)} className="rounded" />
              Require visa sponsorship
            </label>
          </div>
        </CardContent>
      </Card>

      {loading && <p className="text-center text-zinc-500">Loading cached jobs...</p>}

      <div className="space-y-3">
        {jobs.map((job) => {
          const visa = VISA_BADGE[job.visa_signal] || VISA_BADGE.unknown;
          return (
            <Card key={job.id} className="transition-shadow hover:shadow-md">
              <CardContent className="flex items-start justify-between gap-4 pt-6">
                <div className="min-w-0 flex-1 space-y-1.5">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold">{job.title}</h3>
                    <Badge variant={visa.variant}>{visa.label}</Badge>
                    {job.remote && <Badge variant="secondary">Remote</Badge>}
                    <Badge variant="outline">{job.source}</Badge>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-zinc-500">
                    <span className="flex items-center gap-1"><Building2 className="h-3.5 w-3.5" />{job.company}</span>
                    <span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5" />{job.location || "N/A"}</span>
                    {job.salary && <span className="font-medium text-emerald-600">{job.salary}</span>}
                    {job.posted_at && <span>{new Date(job.posted_at).toLocaleDateString()}</span>}
                  </div>
                  {job.jd_text && (
                    <p className="line-clamp-2 text-sm text-zinc-400">{job.jd_text.slice(0, 200)}...</p>
                  )}
                </div>
                <div className="flex flex-shrink-0 items-center gap-2">
                  <Button variant="outline" size="sm" onClick={() => saveJob(job)}>
                    <Bookmark className="mr-1 h-3.5 w-3.5" /> Save
                  </Button>
                  {job.url && (
                    <a href={job.url} target="_blank" rel="noopener noreferrer">
                      <Button variant="ghost" size="sm">
                        <ExternalLink className="h-3.5 w-3.5" />
                      </Button>
                    </a>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
        {!loading && jobs.length === 0 && (
          <div className="rounded-lg border-2 border-dashed border-zinc-200 p-12 text-center dark:border-zinc-800">
            <Search className="mx-auto h-12 w-12 text-zinc-300" />
            <p className="mt-2 text-zinc-500">No jobs yet. Click &ldquo;Search Now&rdquo; to discover jobs.</p>
          </div>
        )}
      </div>
    </div>
  );
}
