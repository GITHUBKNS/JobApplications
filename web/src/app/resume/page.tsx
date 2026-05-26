"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { FileText, Zap, ArrowRight } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import type { JobPosting, MasterResume, ATSAnalysis } from "@/lib/types";

export default function ResumePage() {
  const [jobs, setJobs] = useState<JobPosting[]>([]);
  const [resume, setResume] = useState<MasterResume | null>(null);
  const [selectedJob, setSelectedJob] = useState<JobPosting | null>(null);
  const [analysis, setAnalysis] = useState<ATSAnalysis | null>(null);
  const [tailored, setTailored] = useState<MasterResume | null>(null);
  const [scoring, setScoring] = useState(false);
  const [tailoring, setTailoring] = useState(false);

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

  const scoreResume = async () => {
    if (!selectedJob || !resume) return;
    setScoring(true);
    try {
      const resp = await fetch("/api/resume/score", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resume, jdText: selectedJob.jd_text }),
      });
      const data = await resp.json();
      if (data.error) throw new Error(data.error);
      setAnalysis(data);
      toast.success(`ATS Score: ${data.score}/100`);
    } catch (e) {
      toast.error(`Scoring failed: ${e instanceof Error ? e.message : "Unknown"}`);
    } finally {
      setScoring(false);
    }
  };

  const tailorResume = async () => {
    if (!selectedJob || !resume) return;
    setTailoring(true);
    try {
      const resp = await fetch("/api/resume/tailor", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resume, jdText: selectedJob.jd_text, jobId: selectedJob.id }),
      });
      const data = await resp.json();
      if (data.error) throw new Error(data.error);
      setTailored(data.tailored);
      toast.success("Resume tailored!");
    } catch (e) {
      toast.error(`Tailoring failed: ${e instanceof Error ? e.message : "Unknown"}`);
    } finally {
      setTailoring(false);
    }
  };

  if (!resume) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">Resume Tailoring</h1>
        <Card className="p-12 text-center">
          <FileText className="mx-auto h-12 w-12 text-zinc-300" />
          <p className="mt-2 text-zinc-500">Upload your resume in Settings first.</p>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Resume Tailoring & ATS Scoring</h1>
        <p className="text-zinc-500">Score your resume against a job and auto-tailor keywords.</p>
      </div>

      <Card>
        <CardHeader><CardTitle>Select a Job</CardTitle></CardHeader>
        <CardContent>
          <select
            className="w-full rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
            onChange={(e) => {
              const j = jobs.find((j) => j.id === e.target.value);
              setSelectedJob(j || null);
              setAnalysis(null);
              setTailored(null);
            }}
            value={selectedJob?.id || ""}
          >
            <option value="">Choose a job...</option>
            {jobs.map((j) => (
              <option key={j.id} value={j.id}>{j.title} @ {j.company} ({j.source})</option>
            ))}
          </select>
        </CardContent>
      </Card>

      {selectedJob && (
        <div className="flex gap-3">
          <Button onClick={scoreResume} disabled={scoring}>
            <Zap className="mr-2 h-4 w-4" />
            {scoring ? "Analyzing..." : "Run ATS Analysis"}
          </Button>
          <Button variant="outline" onClick={tailorResume} disabled={tailoring}>
            {tailoring ? "Tailoring..." : "Generate Tailored Resume"}
          </Button>
        </div>
      )}

      {analysis && (
        <Card>
          <CardHeader><CardTitle>ATS Analysis</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div className="rounded-lg bg-zinc-50 p-4 text-center dark:bg-zinc-900">
                <p className="text-3xl font-bold" style={{ color: analysis.score >= 75 ? "#16a34a" : analysis.score >= 50 ? "#d97706" : "#dc2626" }}>
                  {analysis.score}
                </p>
                <p className="text-sm text-zinc-500">ATS Score</p>
              </div>
              <div className="rounded-lg bg-zinc-50 p-4 text-center dark:bg-zinc-900">
                <p className="text-3xl font-bold text-emerald-600">{analysis.matched_keywords.length}</p>
                <p className="text-sm text-zinc-500">Matched</p>
              </div>
              <div className="rounded-lg bg-zinc-50 p-4 text-center dark:bg-zinc-900">
                <p className="text-3xl font-bold text-red-500">{analysis.missing_keywords.length}</p>
                <p className="text-sm text-zinc-500">Missing</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium text-emerald-600">Matched Keywords</p>
                <div className="mt-1 flex flex-wrap gap-1">{analysis.matched_keywords.map((k, i) => <Badge key={i} variant="success">{k}</Badge>)}</div>
              </div>
              <div>
                <p className="text-sm font-medium text-red-500">Missing Keywords</p>
                <div className="mt-1 flex flex-wrap gap-1">{analysis.missing_keywords.map((k, i) => <Badge key={i} variant="destructive">{k}</Badge>)}</div>
              </div>
            </div>

            {analysis.suggestions.length > 0 && (
              <div>
                <p className="text-sm font-medium">Suggestions</p>
                <ul className="mt-1 space-y-1 text-sm text-zinc-600 dark:text-zinc-400">
                  {analysis.suggestions.map((s, i) => <li key={i}>&bull; {s}</li>)}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {tailored && (
        <Card>
          <CardHeader><CardTitle>Tailored vs. Original</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-6">
              <div>
                <p className="mb-2 text-sm font-semibold text-zinc-400">Original</p>
                {resume.experience.map((exp, i) => (
                  <div key={i} className="mb-3">
                    <p className="text-sm font-medium">{exp.title} at {exp.company}</p>
                    <ul className="mt-1 space-y-0.5 text-sm text-zinc-500">
                      {exp.bullets.map((b, j) => <li key={j}>&bull; {b}</li>)}
                    </ul>
                  </div>
                ))}
              </div>
              <div>
                <p className="mb-2 text-sm font-semibold text-emerald-600">Tailored</p>
                {tailored.experience.map((exp, i) => (
                  <div key={i} className="mb-3">
                    <p className="text-sm font-medium">{exp.title} at {exp.company}</p>
                    <ul className="mt-1 space-y-0.5 text-sm text-zinc-700 dark:text-zinc-300">
                      {exp.bullets.map((b, j) => <li key={j}>&bull; {b}</li>)}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
