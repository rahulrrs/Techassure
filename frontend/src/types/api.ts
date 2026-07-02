export type DashboardSummary = {
  kpis: Record<string, number>;
  risk_trend: Array<{ period: string; score: number }>;
  department_risk: Array<{ department: string; score: number; rating: string }>;
  severity_mix: Array<{ severity: string; count: number }>;
  heatmap: Array<{ framework: string; domain: string; risk: number }>;
};

export type Control = {
  id: number;
  control_id: string;
  name: string;
  description: string;
  test_type: string;
  weight: number;
  frameworks: Record<string, string[]>;
  parameters: Record<string, unknown>;
  is_active: boolean;
};

export type Finding = {
  id: number;
  title: string;
  description: string;
  severity: string;
  status: string;
  department?: string;
  impact: string;
  remediation: string;
};

export type Evidence = {
  id: number;
  filename: string;
  dataset_type: string;
  rows_loaded: number;
  validation_summary: Record<string, unknown>;
  created_at: string;
};
