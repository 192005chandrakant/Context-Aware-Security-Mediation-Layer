export interface ToolDefinition {
  name: string;
  description: string;
  category: string;
  sensitivity: string;
  parameters_schema: Record<string, any>;
  requires_confirmation: boolean;
}

export interface ProvenanceRecord {
  request_id: string;
  source: 'user' | 'agent' | 'llm' | 'tool_output' | 'external' | 'unknown';
  confidence: number;
  chain: string[];
  tainted: boolean;
  details: Record<string, any>;
}

export interface DetectionResult {
  request_id: string;
  injection_detected: boolean;
  injection_type: string | null;
  confidence: number;
  indicators: string[];
  model_scores: Record<string, number>;
  details: Record<string, any>;
}

export interface UserIntent {
  intent_summary: string;
  confidence: number;
  extracted_entities: Record<string, any>;
  intent_category: string;
  raw_request: string;
}

export interface AlignmentResult {
  request_id: string;
  aligned: boolean;
  alignment_score: number;
  user_intent: string;
  proposed_action: string;
  misalignment_reasons: string[];
  details: Record<string, any>;
}

export interface RiskResult {
  request_id: string;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  risk_score: number;
  component_scores: Record<string, number>;
  explanation: string;
}

export interface PolicyDecision {
  request_id: string;
  action: 'allow' | 'deny' | 'escalate' | 'sandbox';
  matched_policies: string[];
  overrides: string[];
  explanation: string;
}

export interface AuthorizationDecision {
  request_id: string;
  authorized: boolean;
  action: 'allow' | 'deny' | 'escalate' | 'sandbox';
  requires_sandbox: boolean;
  explanation: string;
  timestamp: string;
}

export interface SecurityDecision {
  request_id: string;
  tool_name: string;
  provenance: ProvenanceRecord;
  detection: DetectionResult;
  intent: UserIntent;
  alignment: AlignmentResult;
  risk: RiskResult;
  policy: PolicyDecision;
  authorization: AuthorizationDecision;
  overall_action: 'allow' | 'deny' | 'escalate' | 'sandbox';
  processing_time_ms: number;
  timestamp: string;
}

export interface ExperimentConfig {
  id: string;
  name: string;
  description: string;
  attack_types: string[];
  model_configs: Record<string, any>;
  dataset_path: string;
  parameters: Record<string, any>;
  num_trials: number;
  seed: number;
}

export interface ExperimentResult {
  experiment_id: string;
  config: ExperimentConfig;
  metrics: Record<string, number>;
  confusion_matrix: Record<string, number> | null;
  per_sample_results: Record<string, any>[];
  duration_seconds: number;
  timestamp: string;
  notes: string;
}

export interface AuditEvent {
  id: string;
  event_type: string;
  request_id: string | null;
  tool_name: string | null;
  user_id: string;
  action: 'allow' | 'deny' | 'escalate' | 'sandbox' | null;
  risk_level: 'low' | 'medium' | 'high' | 'critical' | null;
  details: Record<string, any>;
  timestamp: string;
}
