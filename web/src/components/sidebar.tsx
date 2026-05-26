"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  Settings, Search, FileText, Mail, Send, Users,
  BarChart3, Briefcase, Rocket, ChevronRight,
} from "lucide-react";

const navItems = [
  { href: "/", label: "Dashboard", icon: Rocket, color: "from-indigo-500 to-purple-500" },
  { href: "/jobs", label: "Search Jobs", icon: Search, color: "from-blue-500 to-cyan-500" },
  { href: "/resume", label: "Resume Tailoring", icon: FileText, color: "from-emerald-500 to-teal-500" },
  { href: "/cover-letter", label: "Cover Letter", icon: Mail, color: "from-amber-500 to-orange-500" },
  { href: "/apply", label: "Apply", icon: Briefcase, color: "from-rose-500 to-pink-500" },
  { href: "/recruiter", label: "Find Recruiter", icon: Users, color: "from-violet-500 to-purple-500" },
  { href: "/email", label: "Cold Email", icon: Send, color: "from-sky-500 to-blue-500" },
  { href: "/analytics", label: "Analytics", icon: BarChart3, color: "from-fuchsia-500 to-pink-500" },
  { href: "/settings", label: "Settings", icon: Settings, color: "from-zinc-500 to-zinc-600" },
];

const pipeline = ["Discover", "Tailor", "Apply", "Email", "Track"];

export function Sidebar() {
  const pathname = usePathname();

  const activeIdx = navItems.findIndex((item) => item.href === pathname);

  return (
    <aside className="fixed inset-y-0 left-0 z-50 flex w-[272px] flex-col border-r border-zinc-200/60 bg-white/80 backdrop-blur-xl dark:border-zinc-800/60 dark:bg-zinc-950/80">
      <div className="flex h-16 items-center gap-3 border-b border-zinc-200/60 px-5 dark:border-zinc-800/60">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg shadow-indigo-500/20">
          <Rocket className="h-4.5 w-4.5 text-white" />
        </div>
        <div>
          <span className="text-[15px] font-bold tracking-tight text-zinc-900 dark:text-white">Job Copilot</span>
          <p className="text-[10px] font-medium uppercase tracking-widest text-zinc-400">personal assistant</p>
        </div>
      </div>

      {/* Pipeline progress */}
      <div className="mx-4 mt-4 mb-2 rounded-xl bg-gradient-to-r from-zinc-50 to-zinc-100/50 p-3 dark:from-zinc-900 dark:to-zinc-900/50">
        <p className="mb-2 text-[10px] font-semibold uppercase tracking-widest text-zinc-400">Pipeline</p>
        <div className="flex items-center gap-1">
          {pipeline.map((step, i) => (
            <div key={step} className="flex items-center gap-1">
              <div className={cn(
                "flex h-5 items-center rounded-full px-2 text-[10px] font-semibold transition-all duration-300",
                i <= Math.min(activeIdx, 4)
                  ? "bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-sm shadow-indigo-500/30"
                  : "bg-zinc-200/80 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-500"
              )}>
                {step}
              </div>
              {i < pipeline.length - 1 && (
                <ChevronRight className="h-2.5 w-2.5 text-zinc-300 dark:text-zinc-700" />
              )}
            </div>
          ))}
        </div>
      </div>

      <nav className="flex flex-1 flex-col gap-0.5 overflow-y-auto px-3 py-2">
        {navItems.map((item, i) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-[13px] font-medium transition-all duration-200",
                "animate-slide-in-left",
                `stagger-${i + 1}`,
                isActive
                  ? "bg-gradient-to-r from-indigo-50 to-purple-50/50 text-zinc-900 shadow-sm dark:from-indigo-950/40 dark:to-purple-950/20 dark:text-white"
                  : "text-zinc-500 hover:bg-zinc-100/80 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-900/60 dark:hover:text-white"
              )}
            >
              {isActive && (
                <div className="absolute left-0 top-1/2 h-6 w-[3px] -translate-y-1/2 rounded-r-full bg-gradient-to-b from-indigo-500 to-purple-500" />
              )}
              <div className={cn(
                "flex h-8 w-8 items-center justify-center rounded-lg transition-all duration-200",
                isActive
                  ? `bg-gradient-to-br ${item.color} text-white shadow-md`
                  : "bg-zinc-100 text-zinc-500 group-hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-400 dark:group-hover:bg-zinc-700"
              )}>
                <item.icon className="h-4 w-4" />
              </div>
              <span className="flex-1">{item.label}</span>
              {isActive && (
                <div className="h-1.5 w-1.5 rounded-full bg-indigo-500 animate-pulse-glow" />
              )}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-zinc-200/60 px-4 py-3 dark:border-zinc-800/60">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 text-[11px] font-bold text-white">
            PK
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-[12px] font-semibold text-zinc-800 dark:text-zinc-200">Prasanth Konada</p>
            <p className="truncate text-[10px] text-zinc-400">Newark, NJ</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
