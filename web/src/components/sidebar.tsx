"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  Settings, Search, FileText, Mail, Send, Users,
  BarChart3, Briefcase, Target,
} from "lucide-react";

const navItems = [
  { href: "/", label: "Dashboard", icon: Target },
  { href: "/jobs", label: "Search Jobs", icon: Search },
  { href: "/resume", label: "Resume Tailoring", icon: FileText },
  { href: "/cover-letter", label: "Cover Letter", icon: Mail },
  { href: "/apply", label: "Apply", icon: Briefcase },
  { href: "/recruiter", label: "Find Recruiter", icon: Users },
  { href: "/email", label: "Cold Email", icon: Send },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed inset-y-0 left-0 z-50 w-64 border-r border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
      <div className="flex h-16 items-center gap-2 border-b border-zinc-200 px-6 dark:border-zinc-800">
        <Target className="h-6 w-6 text-zinc-900 dark:text-white" />
        <span className="text-lg font-bold text-zinc-900 dark:text-white">Job Copilot</span>
      </div>
      <nav className="flex flex-col gap-1 p-3">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-zinc-100 text-zinc-900 dark:bg-zinc-800 dark:text-white"
                  : "text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-900 dark:hover:text-white"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
