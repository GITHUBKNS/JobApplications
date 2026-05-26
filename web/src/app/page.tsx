import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Search, FileText, Mail, Send, Users, BarChart3, Briefcase, Settings,
} from "lucide-react";
import Link from "next/link";

const features = [
  { href: "/jobs", icon: Search, title: "Search Jobs", desc: "Discover fresh jobs across JSearch, Adzuna, Greenhouse, Lever & more" },
  { href: "/resume", icon: FileText, title: "Resume Tailoring", desc: "ATS score your resume and auto-tailor keywords per job" },
  { href: "/cover-letter", icon: Mail, title: "Cover Letter", desc: "AI-generated personalized cover letters" },
  { href: "/apply", icon: Briefcase, title: "Apply", desc: "Autofill payloads and one-click open to apply manually" },
  { href: "/recruiter", icon: Users, title: "Find Recruiter", desc: "Hunter, Apollo, RocketReach waterfall email finding" },
  { href: "/email", icon: Send, title: "Cold Email", desc: "Personalized outreach with follow-up cadence via Gmail" },
  { href: "/analytics", icon: BarChart3, title: "Analytics", desc: "Funnel charts, response rates, weekly trends" },
  { href: "/settings", icon: Settings, title: "Settings", desc: "Upload resume, configure API keys, manage profile" },
];

export default function Home() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Job Application Copilot</h1>
        <p className="mt-2 text-zinc-500">
          Discover jobs, tailor your resume, send cold outreach, and track everything — all in one place.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {features.map((f) => (
          <Link key={f.href} href={f.href}>
            <Card className="h-full transition-shadow hover:shadow-md">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-zinc-100 dark:bg-zinc-800">
                    <f.icon className="h-4 w-4" />
                  </div>
                  <CardTitle className="text-base">{f.title}</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription>{f.desc}</CardDescription>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Quick Setup</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-zinc-600 dark:text-zinc-400">
          <div className="flex items-center gap-2">
            <Badge variant="secondary">1</Badge>
            <span>Go to <Link href="/settings" className="font-medium text-zinc-900 underline dark:text-white">Settings</Link> and upload your master resume PDF</span>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="secondary">2</Badge>
            <span>Configure your API keys in Vercel environment variables (or Supabase)</span>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="secondary">3</Badge>
            <span>Head to <Link href="/jobs" className="font-medium text-zinc-900 underline dark:text-white">Search Jobs</Link> to discover opportunities</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
