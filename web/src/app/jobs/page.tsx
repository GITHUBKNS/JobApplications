"use client";

import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { Search, ExternalLink, MapPin, Building2, Bookmark, Loader2, Sparkles, Filter, Globe2, Clock } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import type { JobPosting } from "@/lib/types";

const VISA_BADGE: Record<string, { label: string; variant: "success" | "destructive" | "warning" }> = {
  positive: { label: "Sponsors Visa", variant: "success" },
  reject: { label: "No Visa", variant: "destructive" },
  unknown: { label: "Visa Unknown", variant: "warning" },
};

const SOURCE_COLORS: Record<string, string> = {
  jsearch: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  adzuna: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
  greenhouse: "bg-lime-100 text-lime-700 dark:bg-lime-900/30 dark:text-lime-400",
  lever: "bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-400",
  ashby: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
};

export default function JobsPage() {
  const [jobs, setJobs] = useState<JobPosting[]>([]);
  const [loading, setLoading] = useState(false);
  const [searching, setSearching] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [keywords, setKeywords] = useState("Data Engineer\nAnalytics Engineer");
  const [locations, setLocations] = useState("Newark, NJ\nRemote\nUnited States");
  const [days, setDays] = useState(7);
  const [visaFilter, setVisaFilter] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => { loadCachedJobs(); }, []);

  const loadCachedJobs = async () => {
    setLoading(true);
    try {
      const resp = await fetch("/api/jobs");
      const data = await resp.json();
      setJobs(data.jobs || []);
    } catch { /* empty */ }
    finally { setLoading(false); }
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
      toast.success(`Found ${data.count || 0} unique jobs across all sources`);
    } catch (e) {
      toast.error(`Search failed: ${e instanceof Error ? e.message : "Unknown error"}`);
    } finally {
      setSearching(false);
    }
  };

  const saveJob = async (job: JobPosting) => {
    const supabase = createClient();
    const { error } = await supabase.from("applications").upsert({ job_id: job.id, status: "Saved" }, { onConflict: "job_id" });
    if (error) toast.error("Failed to save");
    else toast.success(`Saved: ${job.title} at ${job.company}`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="animate-fade-in-up flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Search Jobs</h1>
          <p className="mt-1 text-sm text-zinc-500">Multi-source discovery across 10+ job boards and ATS platforms</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => setShowFilters(!showFilters)} className="gap-1.5">
            <Filter className="h-3.5 w-3.5" />
            Filters
          </Button>
          <Button onClick={searchJobs} disabled={searching} className="bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 shadow-lg shadow-indigo-500/20 gap-2">
            {searching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
            {searching ? "Searching..." : "Search Now"}
          </Button>
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <Card className="animate-fade-in-up border-zinc-200/60 dark:border-zinc-800/60">
          <CardContent className="grid grid-cols-4 gap-4 pt-5 pb-5">
            <div>
              <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-zinc-400">Keywords</label>
              <Textarea value={keywords} onChange={(e) => setKeywords(e.target.value)} rows={3} className="text-sm" />
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-zinc-400">Locations</label>
              <Textarea value={locations} onChange={(e) => setLocations(e.target.value)} rows={3} className="text-sm" />
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-zinc-400">Posted within</label>
              <Input type="number" value={days} onChange={(e) => setDays(Number(e.target.value))} min={1} max={30} />
              <p className="mt-1 text-[10px] text-zinc-400">days</p>
            </div>
            <div className="flex flex-col justify-center">
              <label className="flex items-center gap-2.5 cursor-pointer">
                <input type="checkbox" checked={visaFilter} onChange={(e) => setVisaFilter(e.target.checked)} className="h-4 w-4 rounded border-zinc-300 text-indigo-600 focus:ring-indigo-500" />
                <span className="text-sm font-medium">Visa sponsorship required</span>
              </label>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results Count */}
      {jobs.length > 0 && (
        <div className="flex items-center gap-2 text-sm text-zinc-500">
          <Globe2 className="h-4 w-4" />
          <span><strong className="text-zinc-700 dark:text-zinc-300">{jobs.length}</strong> jobs from {new Set(jobs.map(j => j.source)).size} sources</span>
        </div>
      )}

      {/* Job Cards */}
      <div className="space-y-2">
        {loading && (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-6 w-6 animate-spin text-indigo-500" />
            <span className="ml-2 text-sm text-zinc-500">Loading cached jobs...</span>
          </div>
        )}

        {!loading && jobs.map((job, i) => {
          const visa = VISA_BADGE[job.visa_signal] || VISA_BADGE.unknown;
          const sourceStyle = SOURCE_COLORS[job.source] || "bg-zinc-100 text-zinc-600";
          const isExpanded = expandedId === job.id;

          return (
            <Card
              key={job.id}
              className={`animate-fade-in-up stagger-${Math.min(i + 1, 8)} group border-zinc-200/60 transition-all duration-200 hover:border-zinc-300/80 hover:shadow-md dark:border-zinc-800/60 dark:hover:border-zinc-700/80 ${isExpanded ? "ring-1 ring-indigo-200 dark:ring-indigo-900" : ""}`}
            >
              <CardContent className="p-4">
                <div className="flex items-start gap-4">
                  {/* Company avatar */}
                  <div className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-zinc-100 to-zinc-200 text-sm font-bold text-zinc-500 dark:from-zinc-800 dark:to-zinc-700 dark:text-zinc-400">
                    {job.company.slice(0, 2).toUpperCase()}
                  </div>

                  <div className="min-w-0 flex-1">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h3 className="font-semibold leading-tight">{job.title}</h3>
                        <div className="mt-1 flex flex-wrap items-center gap-2 text-sm text-zinc-500">
                          <span className="flex items-center gap-1 font-medium text-zinc-700 dark:text-zinc-300">
                            <Building2 className="h-3.5 w-3.5" />{job.company}
                          </span>
                          {job.location && (
                            <span className="flex items-center gap-1">
                              <MapPin className="h-3 w-3" />{job.location}
                            </span>
                          )}
                          {job.posted_at && (
                            <span className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />{new Date(job.posted_at).toLocaleDateString()}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="flex flex-shrink-0 items-center gap-1.5">
                        <Button variant="ghost" size="sm" onClick={() => saveJob(job)} className="h-8 gap-1 text-xs hover:text-indigo-600">
                          <Bookmark className="h-3.5 w-3.5" /> Save
                        </Button>
                        {job.url && (
                          <a href={job.url} target="_blank" rel="noopener noreferrer">
                            <Button variant="ghost" size="icon" className="h-8 w-8 hover:text-indigo-600">
                              <ExternalLink className="h-3.5 w-3.5" />
                            </Button>
                          </a>
                        )}
                      </div>
                    </div>

                    <div className="mt-2 flex flex-wrap items-center gap-1.5">
                      <Badge variant={visa.variant}>{visa.label}</Badge>
                      {job.remote && <Badge variant="secondary" className="gap-1"><Globe2 className="h-2.5 w-2.5" />Remote</Badge>}
                      <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold ${sourceStyle}`}>
                        {job.source}
                      </span>
                      {job.salary && <Badge variant="outline" className="border-emerald-200 text-emerald-600 dark:border-emerald-800 dark:text-emerald-400">{job.salary}</Badge>}
                    </div>

                    {job.jd_text && (
                      <button
                        onClick={() => setExpandedId(isExpanded ? null : job.id)}
                        className="mt-2 text-left text-xs text-indigo-500 hover:text-indigo-600"
                      >
                        {isExpanded ? "Hide description" : "Show description..."}
                      </button>
                    )}
                    {isExpanded && job.jd_text && (
                      <div className="mt-2 max-h-60 overflow-y-auto rounded-lg bg-zinc-50 p-3 text-xs leading-relaxed text-zinc-600 dark:bg-zinc-900 dark:text-zinc-400">
                        {job.jd_text.slice(0, 3000)}
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}

        {!loading && jobs.length === 0 && (
          <div className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-zinc-200 py-20 dark:border-zinc-800">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-100 to-purple-100 dark:from-indigo-950 dark:to-purple-950">
              <Search className="h-7 w-7 text-indigo-500" />
            </div>
            <h3 className="mt-4 font-semibold text-zinc-700 dark:text-zinc-300">No jobs yet</h3>
            <p className="mt-1 text-sm text-zinc-400">Click &ldquo;Search Now&rdquo; to discover jobs across all sources</p>
            <Button onClick={searchJobs} disabled={searching} className="mt-4 bg-gradient-to-r from-indigo-500 to-purple-600 shadow-lg shadow-indigo-500/20">
              <Sparkles className="mr-2 h-4 w-4" /> Run First Search
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
