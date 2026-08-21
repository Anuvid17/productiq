export interface User {
  id: string;
  name: string;
  email: string;
  role: 'Product Manager' | 'Lead Engineer' | 'QA Lead' | 'Administrator';
  avatar?: string;
}

export interface Feedback {
  id: string;
  original_text: string;
  summary?: string;
  feedback_type?: string;
  category?: string;
  subcategory?: string;
  bug_category?: string;
  severity?: string;
  priority?: string;
  impact_area?: string;
  platform?: string;
  recommended_action?: string;
  confidence?: string;
  status: string;
  created_at?: string;
  updated_at?: string;
}

export interface DuplicateResult {
  is_duplicate: boolean;
  similarity_score: number;
  matched_feedback_id?: string | null;
  matched_text?: string | null;
  reason: string;
}

export interface RoadmapTask {
  id: string;
  roadmap_id: string;
  title: string;
  description?: string | null;
  effort?: string | null;
  status: string;
  progress: number;
  dependencies?: string[] | any;
  acceptance_criteria?: string[] | null;
  created_at?: string;
  updated_at?: string;
}

export interface Roadmap {
  id: string;
  feedback_id: string;
  title: string;
  description?: string | null;
  status: string;
  effort?: string | null;
  progress: number;
  created_at?: string;
  updated_at?: string;
  tasks: RoadmapTask[];
}

export interface FeedbackDetail extends Feedback {
  duplicate?: DuplicateResult | null;
  roadmap?: Roadmap | null;
}

export interface PaginatedFeedback {
  items: Feedback[];
  page: number;
  page_size: number;
  total: number;
}

export interface Notification {
  id: string;
  feedback_id: string;
  message: string;
  notification_type: string;
  read: boolean;
  created_at?: string;
}

export interface HealthResponse {
  status: string;
  service: string;
  database: {
    status: string;
    database: string;
    connected: boolean;
    error?: string;
  };
  ollama: {
    available: boolean;
    model: string;
    error?: string;
  };
}

export interface DashboardSummary {
  total_feedback: number;
  open_feedback: number;
  resolved_feedback: number;
  critical_blocker_issues: number;
  feature_requests: number;
  bug_reports: number;
  active_roadmaps: number;
  average_roadmap_progress: number;
  resolution_rate: number;
  feedback_by_type: Record<string, number>;
  feedback_by_category: Record<string, number>;
  feedback_by_priority: Record<string, number>;
  feedback_by_status: Record<string, number>;
}
