"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { Send, Copy, Sparkles } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import type { JobPosting, MasterResume, Application } from "@/lib/types";

export default function EmailPage() {
  const [jobs, setJobs] = useState<JobPosting[]>([]);
  const [resume, setResume] = useState<MasterResume | null>(null);
  const [selectedJob, setSelectedJob] = useState<JobPosting | null>(null);
  const [application, setApplication] = useState<Application | null>(null);
  const [subject, setSubject] = useState("");
  const [subjectB, setSubjectB] = useState("");
  const [body, setBody] = useState("");
  const [personalization, setPersonalization] = useState("");
  const [generating, setGenerating] = useState(false);
  const [sending, setSending] = useState(false);

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

  const generateEmail = async () => {
    if (!selectedJob || !resume) return;
    setGenerating(true);
    try {
      const resp = await fetch("/api/email/send", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "generate",
          resume,
          jdText: selectedJob.jd_text,
          company: selectedJob.company,
          jobTitle: selectedJob.title,
          recruiterName: application?.recruiter_name || "",
          companyNews: personalization,
          jobId: selectedJob.id,
        }),
      });
      const data = await resp.json();
      if (data.error) throw new Error(data.error);
      setSubject(data.subject_a || "");
      setSubjectB(data.subject_b || "");
      setBody(data.body || "");
      toast.success("Email generated!");
    } catch (e) {
      toast.error(`Generation failed: ${e instanceof Error ? e.message : "Unknown"}`);
    } finally {
      setGenerating(false);
    }
  };

  const recordSend = async () => {
    if (!selectedJob || !application?.recruiter_email) {
      toast.error("No recruiter email set. Go to Find Recruiter first.");
      return;
    }
    setSending(true);
    try {
      const resp = await fetch("/api/email/send", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "record",
          jobId: selectedJob.id,
          to: application.recruiter_email,
          recruiterName: application.recruiter_name,
          subject,
          body,
          company: selectedJob.company,
          jobTitle: selectedJob.title,
        }),
      });
      const data = await resp.json();
      if (data.success) toast.success("Email recorded! Copy the body and send from your Gmail.");
      else toast.error("Failed to record email");
    } catch (e) {
      toast.error("Failed to record");
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Cold Email Outreach</h1>
        <p className="text-zinc-500">Generate personalized cold emails with A/B subject lines.</p>
      </div>

      <Card>
        <CardContent className="space-y-4 pt-6">
          <select
            className="w-full rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
            onChange={(e) => {
              setSelectedJob(jobs.find((j) => j.id === e.target.value) || null);
              setSubject("");
              setBody("");
            }}
          >
            <option value="">Choose a job...</option>
            {jobs.map((j) => (
              <option key={j.id} value={j.id}>{j.title} @ {j.company}</option>
            ))}
          </select>

          {application?.recruiter_email ? (
            <div className="flex items-center gap-2 text-sm">
              <Badge variant="success">Recruiter</Badge>
              <span>{application.recruiter_name} ({application.recruiter_email})</span>
            </div>
          ) : (
            <p className="text-sm text-amber-600">No recruiter selected. Visit Find Recruiter page first.</p>
          )}

          <Input
            value={personalization}
            onChange={(e) => setPersonalization(e.target.value)}
            placeholder="Personalization hook (company news, recruiter activity, etc.)"
          />

          <Button onClick={generateEmail} disabled={generating || !selectedJob || !resume}>
            <Sparkles className="mr-2 h-4 w-4" />
            {generating ? "Generating..." : "Generate Email"}
          </Button>
        </CardContent>
      </Card>

      {subject && (
        <Card>
          <CardHeader>
            <CardTitle>Email Preview</CardTitle>
            <CardDescription>Edit below, then copy and send from your Gmail.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Subject A</label>
              <Input value={subject} onChange={(e) => setSubject(e.target.value)} />
              {subjectB && (
                <>
                  <label className="text-sm font-medium">Subject B (alternative)</label>
                  <Input value={subjectB} onChange={(e) => setSubjectB(e.target.value)} />
                </>
              )}
            </div>

            <div>
              <label className="text-sm font-medium">Body</label>
              <Textarea value={body} onChange={(e) => setBody(e.target.value)} rows={10} />
              <p className="mt-1 text-sm text-zinc-400">{body.split(/\s+/).filter(Boolean).length} words</p>
            </div>

            <div className="rounded-lg bg-zinc-50 p-3 text-xs text-zinc-400 dark:bg-zinc-900">
              CAN-SPAM Footer (auto-appended):<br />
              Physical address &middot; <a href="#" className="underline">Unsubscribe</a>
            </div>

            <div className="flex gap-3">
              <Button
                onClick={() => { navigator.clipboard.writeText(`Subject: ${subject}\n\n${body}`); toast.success("Copied!"); }}
                variant="outline"
              >
                <Copy className="mr-2 h-4 w-4" /> Copy Email
              </Button>
              <Button onClick={recordSend} disabled={sending}>
                <Send className="mr-2 h-4 w-4" /> {sending ? "Recording..." : "Record as Sent"}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
