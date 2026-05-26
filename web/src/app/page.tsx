"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Search, FileText, Mail, Send, Users, BarChart3, Briefcase, Settings,
  ArrowRight, Sparkles, Zap, TrendingUp, Target, CheckCircle2,
  Clock, Rocket, ChevronRight,
} from "lucide-react";
import Link from "next/link";
import { createClient } from "@/lib/supabase/client";

const workflow = [
  {
    step: 1, href: "/jobs", icon: Search, title: "Discover Jobs",
    desc: "Search across JSearch, Adzuna, Greenhouse, Lever & more — filtered by visa sponsorship",
    color: "from-blue-500 to-cyan-500", bg: "bg-blue-50 dark:bg-blue-950/30",
  },
  {
    step: 2, href: "/resume", icon: FileText, title: "Tailor Resume",
    desc: "ATS score 0-100 against any JD, then auto-rewrite bullets to match keywords",
    color: "from-emerald-500 to-teal-500", bg: "bg-emerald-50 dark:bg-emerald-950/30",
  },
  {
    step: 3, href: "/cover-letter", icon: Mail, title: "Cover Letter",
    desc: "AI-generated 3-paragraph letters with company news personalization hooks",
    color: "from-amber-500 to-orange-500", bg: "bg-amber-50 dark:bg-amber-950/30",
  },
  {
    step: 4, href: "/apply", icon: Briefcase, title: "Apply",
    desc: "Autofill payloads ready to paste — opens the application page for you",
    color: "from-rose-500 to-pink-500", bg: "bg-rose-50 dark:bg-rose-950/30",
  },
  {
    step: 5, href: "/recruiter", icon: Users, title: "Find Recruiter",
    desc: "Waterfall: Hunter.io → Apollo → RocketReach with email verification",
    color: "from-violet-500 to-purple-500", bg: "bg-violet-50 dark:bg-violet-950/30",
  },
  {
    step: 6, href: "/email", icon: Send, title: "Cold Email",
    desc: "A/B subject lines, under 120 words, CAN-SPAM compliant with follow-ups",
    color: "from-sky-500 to-blue-500", bg: "bg-sky-50 dark:bg-sky-950/30",
  },
];

export default function Home() {
  const [stats, setStats] = useState({ jobs: 0, apps: 0, emails: 0, replies: 0 });
  const [hasResume, setHasResume] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const supabase = createClient();
        const [jobsRes, appsRes, emailsRes, resumeRes] = await Promise.all([
          supabase.from("jobs").select("id", { count: "exact", head: true }),
          supabase.from("applications").select("id, status", { count: "exact" }),
          supabase.from("emails").select("id", { count: "exact", head: true }),
          supabase.from("resumes").select("id").eq("is_active", true).limit(1),
        ]);
        const replies = (appsRes.data || []).filter((a: { status: string }) => a.status === "Recruiter Replied").length;
        setStats({
          jobs: jobsRes.count || 0,
          apps: appsRes.count || 0,
          emails: emailsRes.count || 0,
          replies,
        });
        setHasResume(!!resumeRes.data?.length);
      } catch { /* Supabase not configured yet */ }
    };
    load();
  }, []);

  return (
    <div className="space-y-10">
      {/* Hero */}
      <div className="animate-fade-in-up relative overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-600 via-purple-600 to-fuchsia-600 px-8 py-10 text-white shadow-2xl shadow-indigo-500/20">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNCI+PGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMiIvPjwvZz48L2c+PC9zdmc+')] opacity-60" />
        <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-white/5 blur-3xl" />
        <div className="absolute -bottom-16 -left-16 h-48 w-48 rounded-full bg-white/5 blur-3xl" />
        <div className="relative z-10 flex items-center justify-between">
          <div className="max-w-xl">
            <div className="mb-3 flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-amber-300" />
              <span className="text-sm font-semibold text-indigo-200">AI-Powered Job Search Assistant</span>
            </div>
            <h1 className="text-4xl font-extrabold tracking-tight">
              Land your next role,<br />
              <span className="bg-gradient-to-r from-white to-purple-200 bg-clip-text text-transparent">intelligently.</span>
            </h1>
            <p className="mt-3 text-base leading-relaxed text-indigo-100/80">
              Discover jobs, ATS-optimize your resume, generate cold outreach, and track your entire pipeline — from a single dashboard.
            </p>
            <div className="mt-6 flex gap-3">
              <Link href={hasResume ? "/jobs" : "/settings"}>
                <Button size="lg" className="bg-white text-indigo-700 shadow-lg shadow-white/20 hover:bg-indigo-50">
                  <Rocket className="mr-2 h-4 w-4" />
                  {hasResume ? "Search Jobs" : "Upload Resume"}
                </Button>
              </Link>
              <Link href="/analytics">
                <Button size="lg" variant="outline" className="border-white/30 bg-white/10 text-white backdrop-blur hover:bg-white/20">
                  View Analytics
                </Button>
              </Link>
            </div>
          </div>
          <div className="hidden lg:block">
            <div className="animate-float relative">
              <div className="flex flex-col gap-2">
                {[
                  { icon: CheckCircle2, text: "Resume parsed", color: "text-emerald-300" },
                  { icon: Target, text: "ATS Score: 92/100", color: "text-amber-300" },
                  { icon: Send, text: "Email delivered", color: "text-sky-300" },
                ].map((item, i) => (
                  <div key={i} className={`animate-fade-in stagger-${i + 2} flex items-center gap-2 rounded-lg bg-white/10 px-4 py-2.5 backdrop-blur-sm`}>
                    <item.icon className={`h-4 w-4 ${item.color}`} />
                    <span className="text-sm font-medium">{item.text}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Live Stats */}
      <div className="animate-fade-in-up stagger-2 grid grid-cols-4 gap-4">
        {[
          { label: "Jobs Discovered", value: stats.jobs, icon: Search, color: "text-blue-500", bg: "bg-blue-50 dark:bg-blue-950/30" },
          { label: "Applications", value: stats.apps, icon: Briefcase, color: "text-emerald-500", bg: "bg-emerald-50 dark:bg-emerald-950/30" },
          { label: "Emails Sent", value: stats.emails, icon: Send, color: "text-purple-500", bg: "bg-purple-50 dark:bg-purple-950/30" },
          { label: "Replies", value: stats.replies, icon: TrendingUp, color: "text-amber-500", bg: "bg-amber-50 dark:bg-amber-950/30" },
        ].map((stat, i) => (
          <Card key={i} className="hover-lift border-zinc-200/60 dark:border-zinc-800/60">
            <CardContent className="flex items-center gap-4 p-5">
              <div className={`flex h-11 w-11 items-center justify-center rounded-xl ${stat.bg}`}>
                <stat.icon className={`h-5 w-5 ${stat.color}`} />
              </div>
              <div>
                <p className="animate-count-up text-2xl font-bold tracking-tight">{stat.value}</p>
                <p className="text-xs font-medium text-zinc-400">{stat.label}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Workflow Pipeline */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold tracking-tight">Your Workflow</h2>
            <p className="text-sm text-zinc-500">Follow this pipeline from discovery to offer</p>
          </div>
          <Badge variant="secondary" className="gap-1">
            <Zap className="h-3 w-3" /> 6 steps
          </Badge>
        </div>

        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
          {workflow.map((item, i) => (
            <Link key={item.href} href={item.href}>
              <Card className={`animate-fade-in-up stagger-${i + 1} group h-full cursor-pointer border-zinc-200/60 transition-all duration-300 hover:shadow-lg hover:shadow-indigo-500/5 hover:-translate-y-1 dark:border-zinc-800/60`}>
                <CardContent className="p-5">
                  <div className="flex items-start gap-4">
                    <div className="relative">
                      <div className={`flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br ${item.color} text-white shadow-lg transition-transform duration-300 group-hover:scale-110`}>
                        <item.icon className="h-5 w-5" />
                      </div>
                      <div className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-white text-[10px] font-bold text-zinc-700 shadow-sm ring-2 ring-white dark:bg-zinc-800 dark:text-zinc-200 dark:ring-zinc-800">
                        {item.step}
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h3 className="font-semibold tracking-tight">{item.title}</h3>
                        <ArrowRight className="h-4 w-4 text-zinc-300 transition-transform duration-200 group-hover:translate-x-1 group-hover:text-indigo-500" />
                      </div>
                      <p className="mt-1 text-[13px] leading-relaxed text-zinc-500">{item.desc}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>

      {/* Quick Start / Getting Started */}
      <div className="animate-fade-in-up stagger-8">
        <Card className="overflow-hidden border-zinc-200/60 dark:border-zinc-800/60">
          <div className="flex">
            <div className="flex-1 p-6">
              <CardTitle className="text-lg">Get Started in 3 Steps</CardTitle>
              <div className="mt-5 space-y-4">
                {[
                  { done: hasResume, label: "Upload your master resume", sub: "Go to Settings and upload a PDF — AI parses it into structured data", href: "/settings" },
                  { done: false, label: "Add your API keys", sub: "Configure LLM keys (Claude/GPT-4o) in Vercel environment variables", href: "/settings" },
                  { done: stats.jobs > 0, label: "Search for jobs", sub: "Run your first multi-source job discovery across 10+ portals", href: "/jobs" },
                ].map((step, i) => (
                  <Link key={i} href={step.href} className="group flex items-start gap-3">
                    <div className={`mt-0.5 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full transition-colors ${step.done ? "bg-emerald-100 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400" : "bg-zinc-100 text-zinc-400 group-hover:bg-indigo-100 group-hover:text-indigo-500 dark:bg-zinc-800"}`}>
                      {step.done ? <CheckCircle2 className="h-4 w-4" /> : <span className="text-xs font-bold">{i + 1}</span>}
                    </div>
                    <div>
                      <p className={`text-sm font-semibold ${step.done ? "text-zinc-400 line-through" : "text-zinc-800 group-hover:text-indigo-600 dark:text-zinc-200"}`}>
                        {step.label}
                      </p>
                      <p className="text-xs text-zinc-400">{step.sub}</p>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
            <div className="hidden w-64 items-center justify-center bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-950/20 dark:to-purple-950/20 lg:flex">
              <div className="space-y-2 p-6 text-center">
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-xl shadow-indigo-500/30">
                  <Rocket className="h-7 w-7" />
                </div>
                <p className="text-sm font-semibold text-zinc-600 dark:text-zinc-400">Ready to launch?</p>
                <p className="text-xs text-zinc-400">Complete setup to unlock all features</p>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Bottom Quick Actions */}
      <div className="flex items-center justify-between rounded-xl bg-zinc-100/80 px-6 py-4 dark:bg-zinc-900/50">
        <div className="flex items-center gap-3">
          <Clock className="h-4 w-4 text-zinc-400" />
          <span className="text-sm text-zinc-500">Pro tip: Set up daily auto-discovery to get fresh jobs every morning at 8 AM ET</span>
        </div>
        <Link href="/settings">
          <Button size="sm" variant="ghost" className="text-indigo-600 hover:text-indigo-700">
            Configure <ChevronRight className="ml-1 h-3 w-3" />
          </Button>
        </Link>
      </div>
    </div>
  );
}
