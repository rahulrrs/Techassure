import { BarChart3, Bot, ClipboardCheck, Database, FileText, Gauge, ShieldCheck, UploadCloud } from "lucide-react";
import type { ReactNode } from "react";

const nav = [
  { label: "Dashboard", icon: Gauge },
  { label: "Controls", icon: ClipboardCheck },
  { label: "Evidence", icon: UploadCloud },
  { label: "Findings", icon: FileText },
  { label: "Risk", icon: BarChart3 },
  { label: "Copilot", icon: Bot }
];

export function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-[#f7f9fb]">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-slate-200 bg-white lg:block">
        <div className="flex h-16 items-center gap-3 border-b border-slate-200 px-5">
          <ShieldCheck className="h-7 w-7 text-teal" />
          <div>
            <div className="text-base font-semibold text-ink">TechAssure</div>
            <div className="text-xs text-slate-500">IT Risk & Control</div>
          </div>
        </div>
        <nav className="space-y-1 px-3 py-4">
          {nav.map((item) => (
            <button key={item.label} className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-slate-700 hover:bg-mist">
              <item.icon className="h-4 w-4" />
              {item.label}
            </button>
          ))}
        </nav>
      </aside>
      <main className="lg:pl-64">
        <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-slate-200 bg-white/95 px-5 backdrop-blur">
          <div>
            <h1 className="text-lg font-semibold text-ink">AI-Powered IT Risk & Control Assessment Platform</h1>
            <p className="text-xs text-slate-500">Continuous compliance monitoring for ISO 27001, NIST CSF, and SOC 2</p>
          </div>
          <button className="inline-flex items-center gap-2 rounded-md bg-teal px-3 py-2 text-sm font-semibold text-white">
            <Database className="h-4 w-4" />
            Live API
          </button>
        </header>
        <div className="p-5">{children}</div>
      </main>
    </div>
  );
}
