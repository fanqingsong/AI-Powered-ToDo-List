import { authApi } from './authApi';

export interface TaskAnalytics {
  total_tasks: number;
  completed_tasks: number;
  pending_tasks: number;
  completion_rate: number;
  tasks_by_day: Array<{
    period: string;
    total: number;
    completed: number;
    pending: number;
  }>;
  tasks_by_week: Array<{
    period: string;
    total: number;
    completed: number;
    pending: number;
  }>;
  tasks_by_month: Array<{
    period: string;
    total: number;
    completed: number;
    pending: number;
  }>;
  average_completion_time?: number;
}

export interface NoteAnalytics {
  total_notes: number;
  total_words: number;
  average_words_per_note: number;
  notes_by_category: Array<{
    category: string;
    count: number;
  }>;
  notes_by_day: Array<{
    period: string;
    count: number;
    total_words: number;
  }>;
  notes_by_week: Array<{
    period: string;
    count: number;
    total_words: number;
  }>;
  notes_by_month: Array<{
    period: string;
    count: number;
    total_words: number;
  }>;
  pinned_notes: number;
  archived_notes: number;
  most_used_tags: Array<{
    tag: string;
    count: number;
  }>;
}

export interface ScheduleAnalytics {
  total_schedules: number;
  completed_schedules: number;
  pending_schedules: number;
  completion_rate: number;
  schedules_by_day: Array<{
    period: string;
    total: number;
    completed: number;
    pending: number;
  }>;
  schedules_by_week: Array<{
    period: string;
    total: number;
    completed: number;
    pending: number;
  }>;
  schedules_by_month: Array<{
    period: string;
    total: number;
    completed: number;
    pending: number;
  }>;
  schedules_by_priority: Array<{
    priority: string;
    count: number;
  }>;
  average_duration?: number;
}

export interface UserActivityAnalytics {
  total_users: number;
  active_users: number;
  new_users_today: number;
  new_users_this_week: number;
  new_users_this_month: number;
  user_activity_by_day: Array<{
    period: string;
    new_users: number;
  }>;
  user_activity_by_week: Array<{
    period: string;
    new_users: number;
  }>;
  user_activity_by_month: Array<{
    period: string;
    new_users: number;
  }>;
}

export interface ProductivityMetrics {
  tasks_completed_today: number;
  notes_created_today: number;
  schedules_completed_today: number;
  total_work_time_today: number;
  productivity_score: number;
  streak_days: number;
  weekly_goal_progress: number;
}

export interface ChartData {
  title: string;
  type: 'line' | 'bar' | 'pie' | 'area' | 'scatter';
  data: Array<any>;
  x_axis: string;
  y_axis: string;
  colors?: string[];
}

export interface AnalyticsOverview {
  time_range: 'today' | 'week' | 'month' | 'quarter' | 'year' | 'all';
  generated_at: string;
  task_analytics: TaskAnalytics;
  note_analytics: NoteAnalytics;
  schedule_analytics: ScheduleAnalytics;
  user_activity: UserActivityAnalytics;
  productivity_metrics: ProductivityMetrics;
  charts: ChartData[];
}

export interface AnalyticsResponse {
  success: boolean;
  message: string;
  data?: AnalyticsOverview;
  error?: string;
}

export type TimeRange = 'today' | 'week' | 'month' | 'quarter' | 'year' | 'all';

class AnalyticsService {
  private baseUrl = '/api/analytics';

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = localStorage.getItem('auth_token');
    
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getAnalyticsOverview(timeRange: TimeRange = 'month', includeCharts: boolean = true): Promise<AnalyticsResponse> {
    try {
      const params = new URLSearchParams({
        time_range: timeRange,
        include_charts: includeCharts.toString()
      });
      
      return await this.request<AnalyticsResponse>(`/overview?${params}`);
    } catch (error) {
      console.error('Error fetching analytics overview:', error);
      throw error;
    }
  }

  async getTaskAnalytics(timeRange: TimeRange = 'month'): Promise<AnalyticsResponse> {
    try {
      const params = new URLSearchParams({
        time_range: timeRange
      });
      
      return await this.request<AnalyticsResponse>(`/tasks?${params}`);
    } catch (error) {
      console.error('Error fetching task analytics:', error);
      throw error;
    }
  }

  async getNoteAnalytics(timeRange: TimeRange = 'month'): Promise<AnalyticsResponse> {
    try {
      const params = new URLSearchParams({
        time_range: timeRange
      });
      
      return await this.request<AnalyticsResponse>(`/notes?${params}`);
    } catch (error) {
      console.error('Error fetching note analytics:', error);
      throw error;
    }
  }

  async getScheduleAnalytics(timeRange: TimeRange = 'month'): Promise<AnalyticsResponse> {
    try {
      const params = new URLSearchParams({
        time_range: timeRange
      });
      
      return await this.request<AnalyticsResponse>(`/schedules?${params}`);
    } catch (error) {
      console.error('Error fetching schedule analytics:', error);
      throw error;
    }
  }

  async getProductivityMetrics(): Promise<AnalyticsResponse> {
    try {
      return await this.request<AnalyticsResponse>('/productivity');
    } catch (error) {
      console.error('Error fetching productivity metrics:', error);
      throw error;
    }
  }

  async getChartData(timeRange: TimeRange = 'month', chartType?: string): Promise<AnalyticsResponse> {
    try {
      const params = new URLSearchParams({
        time_range: timeRange
      });
      
      if (chartType) {
        params.append('chart_type', chartType);
      }
      
      return await this.request<AnalyticsResponse>(`/charts?${params}`);
    } catch (error) {
      console.error('Error fetching chart data:', error);
      throw error;
    }
  }
}

export const analyticsApi = new AnalyticsService();
