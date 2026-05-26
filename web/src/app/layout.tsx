import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/sidebar";
import { Toaster } from "sonner";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Job Application Copilot",
  description: "Personal job-application copilot — discover, tailor, apply, and track",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} h-full bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100`}>
        <Sidebar />
        <main className="ml-64 min-h-full">
          <div className="mx-auto max-w-6xl px-6 py-8">
            {children}
          </div>
        </main>
        <Toaster position="top-right" richColors />
      </body>
    </html>
  );
}
