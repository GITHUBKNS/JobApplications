"use client";

import { useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { Upload, Save, FileText, CheckCircle2, XCircle } from "lucide-react";
import type { MasterResume } from "@/lib/types";
import { createClient } from "@/lib/supabase/client";

export default function SettingsPage() {
  const [resume, setResume] = useState<MasterResume | null>(null);
  const [parsing, setParsing] = useState(false);
  const [resumeText, setResumeText] = useState("");

  const loadResume = useCallback(async () => {
    const supabase = createClient();
    const { data } = await supabase
      .from("resumes")
      .select("data")
      .eq("is_active", true)
      .single();
    if (data?.data) setResume(data.data as MasterResume);
  }, []);

  useState(() => { loadResume(); });

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const text = await file.text();
    setResumeText(text);
    toast.info("PDF uploaded. Click 'Parse Resume' to extract structured data.");
  };

  const parseResume = async () => {
    if (!resumeText) {
      toast.error("Upload a resume file first");
      return;
    }
    setParsing(true);
    try {
      const resp = await fetch("/api/resume/parse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: resumeText }),
      });
      const data = await resp.json();
      if (data.error) throw new Error(data.error);
      setResume(data.resume);
      toast.success("Resume parsed and saved!");
    } catch (e) {
      toast.error(`Parse failed: ${e instanceof Error ? e.message : "Unknown error"}`);
    } finally {
      setParsing(false);
    }
  };

  const saveResume = async () => {
    if (!resume) return;
    const supabase = createClient();
    await supabase.from("resumes").update({ is_active: false }).eq("is_active", true);
    const { error } = await supabase.from("resumes").insert({ data: resume, is_active: true });
    if (error) toast.error("Save failed");
    else toast.success("Resume saved!");
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
        <p className="text-zinc-500">Upload your resume, manage your profile and API integrations.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" /> Master Resume
          </CardTitle>
          <CardDescription>Upload your resume as a text file or paste the content below.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-3">
            <label className="flex cursor-pointer items-center gap-2 rounded-lg border border-dashed border-zinc-300 px-4 py-3 transition-colors hover:bg-zinc-50 dark:border-zinc-700 dark:hover:bg-zinc-900">
              <Upload className="h-4 w-4" />
              <span className="text-sm">Upload file</span>
              <input type="file" accept=".txt,.pdf,.md" onChange={handleFileUpload} className="hidden" />
            </label>
            <Button onClick={parseResume} disabled={parsing || !resumeText}>
              {parsing ? "Parsing..." : "Parse Resume with AI"}
            </Button>
          </div>

          <Textarea
            placeholder="Or paste your resume text here..."
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            rows={6}
          />
        </CardContent>
      </Card>

      {resume && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Parsed Resume</CardTitle>
            <Button size="sm" onClick={saveResume}>
              <Save className="mr-1 h-4 w-4" /> Save Changes
            </Button>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">Name</label>
                <Input
                  value={resume.contact.name}
                  onChange={(e) => setResume({ ...resume, contact: { ...resume.contact, name: e.target.value } })}
                />
              </div>
              <div>
                <label className="text-sm font-medium">Email</label>
                <Input
                  value={resume.contact.email}
                  onChange={(e) => setResume({ ...resume, contact: { ...resume.contact, email: e.target.value } })}
                />
              </div>
              <div>
                <label className="text-sm font-medium">Phone</label>
                <Input
                  value={resume.contact.phone}
                  onChange={(e) => setResume({ ...resume, contact: { ...resume.contact, phone: e.target.value } })}
                />
              </div>
              <div>
                <label className="text-sm font-medium">Location</label>
                <Input
                  value={resume.contact.location}
                  onChange={(e) => setResume({ ...resume, contact: { ...resume.contact, location: e.target.value } })}
                />
              </div>
              <div>
                <label className="text-sm font-medium">LinkedIn</label>
                <Input
                  value={resume.contact.linkedin}
                  onChange={(e) => setResume({ ...resume, contact: { ...resume.contact, linkedin: e.target.value } })}
                />
              </div>
              <div>
                <label className="text-sm font-medium">GitHub</label>
                <Input
                  value={resume.contact.github}
                  onChange={(e) => setResume({ ...resume, contact: { ...resume.contact, github: e.target.value } })}
                />
              </div>
            </div>

            <div>
              <label className="text-sm font-medium">Summary</label>
              <Textarea
                value={resume.summary}
                onChange={(e) => setResume({ ...resume, summary: e.target.value })}
                rows={3}
              />
            </div>

            <div>
              <label className="text-sm font-medium">Skills</label>
              <div className="mt-1 flex flex-wrap gap-1.5">
                {resume.skills.map((s, i) => (
                  <Badge key={i} variant="secondary">{s}</Badge>
                ))}
              </div>
              <Textarea
                className="mt-2"
                value={resume.skills.join(", ")}
                onChange={(e) => setResume({ ...resume, skills: e.target.value.split(",").map((s) => s.trim()).filter(Boolean) })}
                rows={2}
                placeholder="Comma-separated skills"
              />
            </div>

            {resume.experience.map((exp, i) => (
              <div key={i} className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold">{exp.title}</p>
                    <p className="text-sm text-zinc-500">{exp.company} &middot; {exp.location}</p>
                  </div>
                  <p className="text-sm text-zinc-400">{exp.start_date} &ndash; {exp.end_date}</p>
                </div>
                <ul className="mt-2 space-y-1 text-sm">
                  {exp.bullets.map((b, j) => (
                    <li key={j} className="text-zinc-600 dark:text-zinc-400">&bull; {b}</li>
                  ))}
                </ul>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Environment Variables</CardTitle>
          <CardDescription>Set these in your Vercel project settings or Supabase Edge Function secrets.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-2 text-sm">
            {[
              "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "JSEARCH_API_KEY",
              "ADZUNA_APP_ID", "HUNTER_API_KEY", "APOLLO_API_KEY",
              "NEVERBOUNCE_API_KEY", "TAVILY_API_KEY",
            ].map((k) => (
              <div key={k} className="flex items-center gap-2 rounded-md bg-zinc-50 px-3 py-2 dark:bg-zinc-900">
                <code className="text-xs">{k}</code>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
