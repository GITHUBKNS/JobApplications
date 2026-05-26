"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { Users, Search, CheckCircle2 } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import type { JobPosting, RecruiterCandidate } from "@/lib/types";

export default function RecruiterPage() {
  const [jobs, setJobs] = useState<JobPosting[]>([]);
  const [selectedJob, setSelectedJob] = useState<JobPosting | null>(null);
  const [domain, setDomain] = useState("");
  const [candidates, setCandidates] = useState<RecruiterCandidate[]>([]);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    const load = async () => {
      const supabase = createClient();
      const { data } = await supabase.from("jobs").select("*").order("created_at", { ascending: false }).limit(100);
      setJobs(data || []);
    };
    load();
  }, []);

  const searchRecruiters = async () => {
    if (!selectedJob) return;
    setSearching(true);
    try {
      const resp = await fetch("/api/recruiter", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          companyDomain: domain,
          company: selectedJob.company,
        }),
      });
      const data = await resp.json();
      if (data.error) throw new Error(data.error);
      setCandidates(data.candidates || []);
      toast.success(`Found ${data.candidates?.length || 0} recruiter(s)`);
    } catch (e) {
      toast.error(`Search failed: ${e instanceof Error ? e.message : "Unknown"}`);
    } finally {
      setSearching(false);
    }
  };

  const selectRecruiter = async (c: RecruiterCandidate) => {
    if (!selectedJob) return;
    const supabase = createClient();
    await supabase.from("applications").upsert({
      job_id: selectedJob.id,
      recruiter_name: c.name,
      recruiter_email: c.email,
      updated_at: new Date().toISOString(),
    }, { onConflict: "job_id" });
    toast.success(`Selected ${c.name} (${c.email})`);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Find Recruiter</h1>
        <p className="text-zinc-500">Discover and verify recruiter emails via Hunter.io and Apollo.</p>
      </div>

      <Card>
        <CardContent className="space-y-4 pt-6">
          <div>
            <label className="text-sm font-medium">Select a Job</label>
            <select
              className="mt-1 w-full rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
              onChange={(e) => {
                const j = jobs.find((j) => j.id === e.target.value);
                setSelectedJob(j || null);
                setCandidates([]);
                if (j?.company_domain) {
                  setDomain(j.company_domain.replace(/https?:\/\//, "").split("/")[0]);
                }
              }}
            >
              <option value="">Choose a job...</option>
              {jobs.map((j) => (
                <option key={j.id} value={j.id}>{j.title} @ {j.company}</option>
              ))}
            </select>
          </div>
          <div className="flex gap-3">
            <Input
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              placeholder="Company domain (e.g., stripe.com)"
              className="max-w-xs"
            />
            <Button onClick={searchRecruiters} disabled={searching || !selectedJob}>
              <Search className="mr-2 h-4 w-4" />
              {searching ? "Searching..." : "Search Recruiters"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {candidates.length > 0 && (
        <div className="space-y-3">
          {candidates.map((c, i) => (
            <Card key={i} className="transition-shadow hover:shadow-md">
              <CardContent className="flex items-center justify-between pt-6">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <p className="font-semibold">{c.name || "Unknown"}</p>
                    <Badge variant="secondary">{c.source}</Badge>
                    <Badge variant={c.confidence >= 0.7 ? "success" : "warning"}>
                      {Math.round(c.confidence * 100)}% confidence
                    </Badge>
                  </div>
                  <p className="text-sm text-zinc-500">{c.title} at {c.company}</p>
                  <p className="font-mono text-sm">{c.email || "No email found"}</p>
                  {c.linkedin_url && (
                    <a href={c.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:underline">
                      LinkedIn Profile
                    </a>
                  )}
                </div>
                {c.email && (
                  <Button variant="outline" onClick={() => selectRecruiter(c)}>
                    <CheckCircle2 className="mr-2 h-4 w-4" /> Select
                  </Button>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
