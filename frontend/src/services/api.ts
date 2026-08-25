import axios from 'axios';
import type {
  Feedback,
  FeedbackDetail,
  PaginatedFeedback,
  Roadmap,
  Notification,
  HealthResponse,
  DashboardSummary
} from '../types';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.PROD
    ? 'https://productiq-backend-2x15.onrender.com/api/v1'
    : '/api/v1');

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 125000,
});

export const api = {
  // Health
  getHealth: async (): Promise<HealthResponse> => {
    const res = await apiClient.get<HealthResponse>('/health');
    return res.data;
  },

  // Dashboard Analytics
  getDashboardSummary: async (): Promise<DashboardSummary> => {
    const res = await apiClient.get<DashboardSummary>('/dashboard/summary');
    return res.data;
  },

  // Feedback APIs
  createFeedback: async (payload: { original_text: string; platform?: string }): Promise<FeedbackDetail> => {
    const res = await apiClient.post<FeedbackDetail>('/feedback', payload);
    return res.data;
  },

  getFeedback: async (params?: {
    page?: number;
    page_size?: number;
    status?: string;
    priority?: string;
    severity?: string;
    category?: string;
    feedback_type?: string;
    search?: string;
  }): Promise<PaginatedFeedback> => {
    const res = await apiClient.get<PaginatedFeedback>('/feedback', { params });
    return res.data;
  },

  getFeedbackById: async (id: string): Promise<FeedbackDetail> => {
    const res = await apiClient.get<FeedbackDetail>(`/feedback/${id}`);
    return res.data;
  },

  updateFeedbackStatus: async (id: string, status: string): Promise<Feedback> => {
    const res = await apiClient.patch<Feedback>(`/feedback/${id}/status`, { status });
    return res.data;
  },

  // Roadmap APIs
  getRoadmaps: async (params?: { status?: string; limit?: number; offset?: number }): Promise<Roadmap[]> => {
    const res = await apiClient.get<Roadmap[]>('/roadmaps', { params });
    return res.data;
  },

  getRoadmapById: async (id: string): Promise<Roadmap> => {
    const res = await apiClient.get<Roadmap>(`/roadmaps/${id}`);
    return res.data;
  },

  updateRoadmap: async (id: string, payload: { status?: string; progress?: number; title?: string }): Promise<Roadmap> => {
    const res = await apiClient.patch<Roadmap>(`/roadmaps/${id}`, payload);
    return res.data;
  },

  // Task Workflow APIs
  getTaskById: async (id: string): Promise<any> => {
    const res = await apiClient.get<any>(`/tasks/${id}`);
    return res.data;
  },

  updateTask: async (taskId: string, payload: { progress?: number; status?: string }): Promise<any> => {
    const res = await apiClient.patch<any>(`/tasks/${taskId}`, payload);
    return res.data;
  },

  // Notification APIs
  getNotifications: async (read?: boolean): Promise<Notification[]> => {
    try {
      const res = await apiClient.get<Notification[]>('/notifications', { params: { read } });
      return res.data;
    } catch {
      return [];
    }
  },

  markNotificationRead: async (id: string): Promise<Notification> => {
    const res = await apiClient.patch<Notification>(`/notifications/${id}/read`);
    return res.data;
  },

  markAllNotificationsRead: async (): Promise<{ updated_count: number }> => {
    const res = await apiClient.patch<{ updated_count: number }>('/notifications/read-all');
    return res.data;
  }
};
