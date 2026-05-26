"use client";

import { useState, useEffect, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BarChart3, TrendingUp, Mail, Briefcase } from "lucide-react";

interface AppRow { status: string; applied_at: string | null; created_at: string; job_id: string; recruiter_email?: string; jobs?: { title: string; company: string } }
interface EmailRow { email_type: string; job_id: string; sent_at: string }
interface JobRow { source: string; id: string; company: string; created_at: string }

export default function AnalyticsPage() {
  const [apps, setApps] = useState<AppRow[]>([]);
  const [emails, setEmails] = useState<EmailRow[]>([]);
  const [jobs, setJobs] = useState<JobRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/analytics")
      .then((r) => r.json())
      .then((d) => {
        setApps(d.applications || []);
        setEmails(d.emails || []);
        setJobs(d.jobs || []);
      })
      .finally(() => setLoading(false));
  }, []);

  const statusCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    apps.forEach((a) => { counts[a.status] = (counts[a.status] || 0) + 1; });
    return counts;
  }, [apps]);

  const sourceCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    jobs.forEach((j) => { counts[j.source] = (counts[j.source] || 0) + 1; });
    return counts;
  }, [jobs]);

  const emailTypeCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    emails.forEach((e) => { counts[e.email_type] = (counts[e.email_type] || 0) + 1; });
    return counts;
  }, [emails]);

  const replied = apps.filter((a) => a.status === "Recruiter Replied").length;
  const emailed = new Set(emails.map((e) => e.job_id)).size;
  const replyRate = emailed > 0 ? ((replied / emailed) * 100).toFixed(1) : "0";

  const weeklyCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    apps.forEach((a) => {
      const d = a.applied_at || a.created_at;
      if (!d) return;
      const date = new Date(d);
      const week = `${date.getFullYear()}-W${String(Math.ceil((date.getDate() + new Date(date.getFullYear(), date.getMonth(), 1).getDay()) / 7)).padStart(2, "0")}`;
      counts[week] = (counts[week] || 0) + 1;
    });
    return Object.entries(counts).sort(([a], [b]) => a.localeCompare(b));
  }, [apps]);

  const maxWeekly = Math.max(...weeklyCounts.map(([, c]) => c), 1);

  if (loading) return <p className="text-center text-zinc-500 py-12">Loading analytics...</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Analytics Dashboard</h1>
        <p className="text-zinc-500">Track your application funnel, response rates, and trends.</p>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6 text-center">
            <Briefcase className="mx-auto h-8 w-8 text-zinc-400" />
            <p className="mt-2 text-3xl font-bold">{jobs.length}</p>
            <p className="text-sm text-zinc-500">Jobs Discovered</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <TrendingUp className="mx-auto h-8 w-8 text-blue-500" />
            <p className="mt-2 text-3xl font-bold">{apps.length}</p>
            <p className="text-sm text-zinc-500">Applications</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <Mail className="mx-auto h-8 w-8 text-emerald-500" />
            <p className="mt-2 text-3xl font-bold">{emails.length}</p>
            <p className="text-sm text-zinc-500">Emails Sent</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <BarChart3 className="mx-auto h-8 w-8 text-purple-500" />
            <p className="mt-2 text-3xl font-bold">{replyRate}%</p>
            <p className="text-sm text-zinc-500">Reply Rate</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="funnel">
        <TabsList>
          <TabsTrigger value="funnel">Funnel</TabsTrigger>
          <TabsTrigger value="weekly">Weekly</TabsTrigger>
          <TabsTrigger value="sources">Sources</TabsTrigger>
          <TabsTrigger value="emails">Emails</TabsTrigger>
        </TabsList>

        <TabsContent value="funnel">
          <Card>
            <CardHeader><CardTitle>Application Funnel</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-2">
                {["Saved", "Applied", "Email Sent", "Followup1 Sent", "Followup2 Sent", "Recruiter Replied", "Interview", "Offer", "Rejected", "Ghosted"].map((status) => {
                  const count = statusCounts[status] || 0;
                  const max = Math.max(...Object.values(statusCounts), 1);
                  const pct = (count / max) * 100;
                  return (
                    <div key={status} className="flex items-center gap-3">
                      <span className="w-36 text-sm">{status}</span>
                      <div className="flex-1">
                        <div className="h-7 rounded-md bg-zinc-100 dark:bg-zinc-800">
                          <div
                            className="flex h-full items-center rounded-md bg-zinc-900 px-2 text-xs font-medium text-white dark:bg-white dark:text-zinc-900"
                            style={{ width: `${Math.max(pct, count > 0 ? 8 : 0)}%` }}
                          >
                            {count > 0 ? count : ""}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="weekly">
          <Card>
            <CardHeader><CardTitle>Applications Per Week</CardTitle></CardHeader>
            <CardContent>
              {weeklyCounts.length === 0 ? (
                <p className="text-center text-zinc-500 py-8">No data yet</p>
              ) : (
                <div className="flex items-end gap-2" style={{ height: 200 }}>
                  {weeklyCounts.map(([week, count]) => (
                    <div key={week} className="flex flex-1 flex-col items-center gap-1">
                      <div
                        className="w-full rounded-t-md bg-zinc-900 dark:bg-white"
                        style={{ height: `${(count / maxWeekly) * 160}px` }}
                      />
                      <span className="text-xs text-zinc-400">{week}</span>
                      <span className="text-xs font-medium">{count}</span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="sources">
          <Card>
            <CardHeader><CardTitle>Jobs by Source</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-2">
                {Object.entries(sourceCounts)
                  .sort(([, a], [, b]) => b - a)
                  .map(([source, count]) => (
                    <div key={source} className="flex items-center justify-between rounded-lg bg-zinc-50 px-4 py-2 dark:bg-zinc-900">
                      <span className="text-sm font-medium">{source}</span>
                      <Badge variant="secondary">{count}</Badge>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="emails">
          <Card>
            <CardHeader><CardTitle>Emails by Type</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-2">
                {Object.entries(emailTypeCounts).map(([type, count]) => (
                  <div key={type} className="flex items-center justify-between rounded-lg bg-zinc-50 px-4 py-2 dark:bg-zinc-900">
                    <span className="text-sm font-medium capitalize">{type}</span>
                    <Badge variant="secondary">{count}</Badge>
                  </div>
                ))}
                {Object.keys(emailTypeCounts).length === 0 && (
                  <p className="text-center text-zinc-500 py-4">No emails sent yet</p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Card>
        <CardHeader><CardTitle>Recent Applications</CardTitle></CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-zinc-500">
                  <th className="pb-2 font-medium">Job</th>
                  <th className="pb-2 font-medium">Status</th>
                  <th className="pb-2 font-medium">Recruiter</th>
                  <th className="pb-2 font-medium">Date</th>
                </tr>
              </thead>
              <tbody>
                {apps.slice(0, 20).map((a, i) => (
                  <tr key={i} className="border-b border-zinc-100 dark:border-zinc-800">
                    <td className="py-2">{a.jobs?.title || a.job_id} at {a.jobs?.company || ""}</td>
                    <td className="py-2"><Badge variant="secondary">{a.status}</Badge></td>
                    <td className="py-2 text-zinc-500">{a.recruiter_email || "-"}</td>
                    <td className="py-2 text-zinc-400">{a.applied_at ? new Date(a.applied_at).toLocaleDateString() : "-"}</td>
                  </tr>
                ))}
                {apps.length === 0 && (
                  <tr><td colSpan={4} className="py-8 text-center text-zinc-400">No applications yet</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
