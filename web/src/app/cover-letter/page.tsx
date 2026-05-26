"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { Mail, Copy, Save } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import type { JobPosting, MasterResume } from "@/lib/types";

export default function CoverLetterPage() {
  const [jobs, setJobs] = useState<JobPosting[]>([]);
  const [resume, setResume] = useState<MasterResume | null>(null);
  const [selectedJob, setSelectedJob] = useState<JobPosting | null>(null);
  const [letter, setLetter] = useState("");
  const [companyNews, setCompanyNews] = useState("");
  const [recruiterName, setRecruiterName] = useState("");
  const [generating, setGenerating] = useState(false);

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

  const generateLetter = async () => {
    if (!selectedJob || !resume) return;
    setGenerating(true);
    try {
      const resp = await fetch("/api/cover-letter", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resume,
          jdText: selectedJob.jd_text,
          company: selectedJob.company,
          jobTitle: selectedJob.title,
          companyNews,
          recruiterName,
          jobId: selectedJob.id,
        }),
      });
      const data = await resp.json();
      if (data.error) throw new Error(data.error);
      setLetter(data.letter);
      toast.success("Cover letter generated!");
    } catch (e) {
      toast.error(`Generation failed: ${e instanceof Error ? e.message : "Unknown"}`);
    } finally {
      setGenerating(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(letter);
    toast.success("Copied to clipboard!");
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Cover Letter Generator</h1>
        <p className="text-zinc-500">AI-generated, personalized cover letters for each job.</p>
      </div>

      <Card>
        <CardContent className="space-y-4 pt-6">
          <div>
            <label className="text-sm font-medium">Select a Job</label>
            <select
              className="mt-1 w-full rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
              onChange={(e) => {
                setSelectedJob(jobs.find((j) => j.id === e.target.value) || null);
                setLetter("");
              }}
            >
              <option value="">Choose a job...</option>
              {jobs.map((j) => (
                <option key={j.id} value={j.id}>{j.title} @ {j.company}</option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium">Company news / personalization hook</label>
              <Input
                value={companyNews}
                onChange={(e) => setCompanyNews(e.target.value)}
                placeholder="e.g., Company just raised Series C..."
              />
            </div>
            <div>
              <label className="text-sm font-medium">Recruiter name (optional)</label>
              <Input
                value={recruiterName}
                onChange={(e) => setRecruiterName(e.target.value)}
                placeholder="e.g., Jane Smith"
              />
            </div>
          </div>
          <Button onClick={generateLetter} disabled={generating || !selectedJob || !resume}>
            <Mail className="mr-2 h-4 w-4" />
            {generating ? "Generating..." : "Generate Cover Letter"}
          </Button>
        </CardContent>
      </Card>

      {letter && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Generated Cover Letter</CardTitle>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={copyToClipboard}>
                <Copy className="mr-1 h-3.5 w-3.5" /> Copy
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <Textarea
              value={letter}
              onChange={(e) => setLetter(e.target.value)}
              rows={16}
              className="font-serif text-base leading-relaxed"
            />
            <p className="mt-2 text-sm text-zinc-400">{letter.split(/\s+/).length} words</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
