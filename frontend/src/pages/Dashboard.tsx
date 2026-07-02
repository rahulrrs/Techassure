import { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2, FileWarning, Server } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { api, demoLogin } from "../api/client";
import { MetricCard } from "../components/MetricCard";
import type { Control, DashboardSummary, Evidence, Finding } from "../types/api";

const fallbackSummary: DashboardSummary = {
  kpis: { assets: 0, open_findings: 0, controls: 0, enterprise_risk: 0 },
  risk_trend: [{ period: "Current", score: 0 }],
  department_risk: [],
  severity_mix: [],
  heatmap: []
};

export function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary>(fallbackSummary);
  const [controls, setControls] = useState<Control[]>([]);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [copilot, setCopilot] = useState("");
  const [question, setQuestion] = useState("Which controls are driving the highest residual risk?");

  async function refresh() {
    await demoLogin();
    const [summaryRes, controlsRes, findingsRes, evidenceRes] = await Promise.all([
      api.get("/dashboard/summary"),
      api.get("/controls"),
      api.get("/findings"),
      api.get("/evidence")
    ]);
    setSummary(summaryRes.data);
    setControls(controlsRes.data);
    setFindings(findingsRes.data);
    setEvidence(evidenceRes.data);
  }

  useEffect(() => {
    refresh().catch(() => undefined);
  }, []);

  async function seedAndRun() {
    await api.post("/controls/seed");
    await api.post("/controls/run-all");
    await api.post("/dashboard/risk/recompute");
    await refresh();
  }

  async function askCopilot() {
    const { data } = await api.post("/dashboard/copilot", { question });
    setCopilot(data.answer);
  }

  return (
    <div className="space-y-5">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Enterprise Risk" value={summary.kpis.enterprise_risk ?? 0} icon={AlertTriangle} tone="text-rose" />
        <MetricCard label="Open Findings" value={summary.kpis.open_findings ?? 0} icon={FileWarning} tone="text-amber" />
        <MetricCard label="Active Controls" value={summary.kpis.controls ?? 0} icon={CheckCircle2} tone="text-teal" />
        <MetricCard label="Assets Monitored" value={summary.kpis.assets ?? 0} icon={Server} tone="text-slate-600" />
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.35fr_0.65fr]">
        <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-base font-semibold text-ink">Department Risk</h2>
            <button onClick={seedAndRun} className="rounded-md bg-ink px-3 py-2 text-sm font-semibold text-white">Run Controls</button>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={summary.department_risk}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="department" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="score" fill="#117c78" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <h2 className="mb-3 text-base font-semibold text-ink">Finding Severity</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={summary.severity_mix} dataKey="count" nameKey="severity" outerRadius={92} label>
                  {summary.severity_mix.map((_, index) => <Cell key={index} fill={["#b9384f", "#c47a18", "#117c78", "#536271"][index % 4]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-3">
        <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm xl:col-span-2">
          <h2 className="mb-3 text-base font-semibold text-ink">Control Library</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-200 text-xs uppercase text-slate-500">
                <tr><th className="py-2">Control</th><th>Test</th><th>Frameworks</th><th>Weight</th></tr>
              </thead>
              <tbody>
                {controls.map((control) => (
                  <tr key={control.id} className="border-b border-slate-100">
                    <td className="py-3 font-medium text-ink">{control.control_id} · {control.name}</td>
                    <td>{control.test_type}</td>
                    <td>{Object.keys(control.frameworks).join(", ")}</td>
                    <td>{control.weight}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <h2 className="mb-3 text-base font-semibold text-ink">AI Audit Copilot</h2>
          <textarea value={question} onChange={(event) => setQuestion(event.target.value)} className="h-24 w-full rounded-md border border-slate-300 p-3 text-sm" />
          <button onClick={askCopilot} className="mt-3 w-full rounded-md bg-teal px-3 py-2 text-sm font-semibold text-white">Ask Copilot</button>
          <p className="mt-3 text-sm leading-6 text-slate-700">{copilot}</p>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-2">
        <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <h2 className="mb-3 text-base font-semibold text-ink">Recent Findings</h2>
          <div className="space-y-3">
            {findings.slice(0, 6).map((finding) => (
              <div key={finding.id} className="rounded-md border border-slate-200 p-3">
                <div className="flex items-center justify-between gap-3">
                  <span className="font-medium text-ink">{finding.title}</span>
                  <span className="rounded bg-mist px-2 py-1 text-xs">{finding.severity}</span>
                </div>
                <p className="mt-1 text-sm text-slate-600">{finding.remediation}</p>
              </div>
            ))}
          </div>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <h2 className="mb-3 text-base font-semibold text-ink">Evidence Loads</h2>
          <div className="space-y-3">
            {evidence.slice(0, 6).map((item) => (
              <div key={item.id} className="flex items-center justify-between rounded-md border border-slate-200 p-3 text-sm">
                <span className="font-medium text-ink">{item.filename}</span>
                <span>{item.dataset_type} · {item.rows_loaded} rows</span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
