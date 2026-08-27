import type {
  AuditEvent,
  ExperimentResult,
  SecurityDecision,
  ToolDefinition,
} from '../types';

const API_BASE = 'http://localhost:8000';

export async function fetchHealth(): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Failed to fetch health status');
  return res.json();
}

export async function fetchTools(): Promise<ToolDefinition[]> {
  const res = await fetch(`${API_BASE}/api/tools`);
  if (!res.ok) throw new Error('Failed to fetch tools');
  return res.json();
}

export async function analyzeSecurity(data: {
  tool_name: string;
  parameters: Record<string, any>;
  user_request: string;
  session_id?: string;
}): Promise<SecurityDecision> {
  const res = await fetch(`${API_BASE}/api/security/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to run security analysis');
  return res.json();
}

export async function runExperiment(data: {
  name: string;
  description: string;
  attack_types: string[];
  num_trials: number;
}): Promise<ExperimentResult> {
  const res = await fetch(`${API_BASE}/api/experiments/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to run experiment');
  return res.json();
}

export async function fetchExperiments(): Promise<ExperimentResult[]> {
  const res = await fetch(`${API_BASE}/api/experiments`);
  if (!res.ok) throw new Error('Failed to fetch experiments');
  return res.json();
}

export async function fetchAuditLogs(): Promise<AuditEvent[]> {
  const res = await fetch(`${API_BASE}/api/audit`);
  if (!res.ok) throw new Error('Failed to fetch audit logs');
  return res.json();
}

export async function fetchMetrics(): Promise<any> {
  const res = await fetch(`${API_BASE}/api/metrics`);
  if (!res.ok) throw new Error('Failed to fetch metrics');
  return res.json();
}
