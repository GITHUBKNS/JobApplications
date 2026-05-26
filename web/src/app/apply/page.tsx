"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { ExternalLink, Clipboard, CheckCircle2 } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import type { JobPosting, MasterResume, Application } from "@/lib/types";

export default function ApplyPage() {
  const [jobs, setJobs] = useState<JobPosting[]>([]);
  const [resume, setResume] = useState<MasterResume | null>(null);
  const [selectedJob, setSelectedJob] = useState<JobPosting | null>(null);
  const [application, setApplication] = useState<Application | null>(null);

  useEffect(() => {
    const load = async () => {
      const supabase = createClient();
      const [jobsRes, resumeRes] = await Promise.all([
        supabase.from("jobs").select("*").order("created_at", { ascending: false }).limit(100),
        supabase.from("resumes").select("data").eq("is_active", true).single(),
      ]);
      setJobs(jobsRes.data || []);
      if (resumeRes.data?.data) setResume(resumeRes.data.data as MasterResume);
    };
    load();
  }, []);

  useEffect(() => {
    if (!selectedJob) return;
    const loadApp = async () => {
      const supabase = createClient();
      const { data } = await supabase
        .from("applications")
        .select("*")
        .eq("job_id", selectedJob.id)
        .single();
      setApplication(data as Application | null);
    };
    loadApp();
  }, [selectedJob]);

  const buildAutofill = () => {
    if (!resume) return "";
    const lines = [
      `Full Name: ${resume.contact.name}`,
      `Email: ${resume.contact.email}`,
      `Phone: ${resume.contact.phone}`,
      `LinkedIn: ${resume.contact.linkedin}`,
      `Website: ${resume.contact.website || resume.contact.github}`,
      "",
      "Work Authorization: Require sponsorship",
      "Sponsorship Needed: Yes",
      "Willing to Relocate: Yes",
      "Salary Expectation: Negotiable",
      "Start Date: 2 weeks notice",
      "",
      "Skills:",
      ...resume.skills.slice(0, 15).map((s) => `  - ${s}`),
    ];
    return lines.join("\n");
  };

  const markApplied = async () => {
    if (!selectedJob) return;
    const supabase = createClient();
    const { error } = await supabase.from("applications").upsert({
      job_id: selectedJob.id,
      status: "Applied",
      applied_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }, { onConflict: "job_id" });
    if (error) toast.error("Failed to update");
    else {
      toast.success("Marked as Applied!");
      setApplication((prev) => prev ? { ...prev, status: "Applied" } : null);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Apply to Jobs</h1>
        <p className="text-zinc-500">Generate autofill payloads and open application pages.</p>
      </div>

      <Card>
        <CardContent className="pt-6">
          <select
            className="w-full rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
            onChange={(e) => setSelectedJob(jobs.find((j) => j.id === e.target.value) || null)}
          >
            <option value="">Choose a job...</option>
            {jobs.map((j) => (
              <option key={j.id} value={j.id}>{j.title} @ {j.company}</option>
            ))}
          </select>
        </CardContent>
      </Card>

      {selectedJob && (
        <>
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>{selectedJob.title} at {selectedJob.company}</CardTitle>
                {application?.status && <Badge variant="secondary">{application.status}</Badge>}
              </div>
              <CardDescription>{selectedJob.location} &middot; {selectedJob.source}</CardDescription>
            </CardHeader>
            <CardContent className="flex gap-3">
              {selectedJob.url && (
                <a href={selectedJob.url} target="_blank" rel="noopener noreferrer">
                  <Button>
                    <ExternalLink className="mr-2 h-4 w-4" /> Open Application Page
                  </Button>
                </a>
              )}
              <Button variant="outline" onClick={markApplied}>
                <CheckCircle2 className="mr-2 h-4 w-4" /> Mark as Applied
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clipboard className="h-5 w-5" /> Autofill Payload
              </CardTitle>
              <CardDescription>Copy this info to paste into application forms.</CardDescription>
            </CardHeader>
            <CardContent>
              <Textarea value={buildAutofill()} readOnly rows={16} className="font-mono text-sm" />
              <Button
                variant="outline"
                className="mt-3"
                onClick={() => { navigator.clipboard.writeText(buildAutofill()); toast.success("Copied!"); }}
              >
                <Clipboard className="mr-2 h-4 w-4" /> Copy to Clipboard
              </Button>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
