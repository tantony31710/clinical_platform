// ─── Auth ──────────────────────────────────────────────────────────────────
export interface LoginPayload {
  patient_id: string;
  password: string;
}

export interface AuthUser {
  patient_id: string;
}

// ─── Specialty Config ──────────────────────────────────────────────────────
export type FieldType = 'numeric' | 'choice';

export interface FieldConfig {
  prompt: string;
  type: FieldType;
  min_allowed?: number;
  max_allowed?: number;
  max_optimal?: number;
  default: number | string;
  choices?: string[];
  tip?: string;
}

export interface SpecialtyEngine {
  type: 'ml' | 'rule';
  model_file?: string;
  feature_order?: string[];
  rule_fn?: string;
  positive_verdict?: string;
  negative_verdict?: string;
}

export interface SpecialtyConfig {
  title: string;
  category: string;
  description: string;
  engine: SpecialtyEngine;
  registry: Record<string, FieldConfig>;
}

// ─── Assessment ────────────────────────────────────────────────────────────
export interface AssessPayload {
  trackId: string;
  profile: Record<string, number | string>;
}

export interface AssessResult {
  specialty: string;
  risk_score?: number;
  risk_percent?: number;
  verdict?: string;
  details?: Record<string, unknown>;
  engine_type?: string;
  label?: string;
  [key: string]: unknown;
}

export interface AssessResponse {
  results: AssessResult | AssessResult[];
  profile_used: Record<string, number | string>;
}

// ─── History ───────────────────────────────────────────────────────────────
export interface HistoryEntry {
  id: string;
  timestamp: string;
  track_id: string;
  specialty_title?: string;
  results: AssessResult | AssessResult[];
  profile_used: Record<string, number | string>;
}

// ─── Global Baseline ───────────────────────────────────────────────────────
export interface GlobalBaseline {
  Age: number;
  Sex: number;
  BloodPressure: number;
  Smoker: string;
}
