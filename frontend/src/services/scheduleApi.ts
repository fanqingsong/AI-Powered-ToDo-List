import { AuthService } from './authApi';

export interface Schedule {
  id: number;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  is_all_day: boolean;
  location?: string;
  color: string;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface ScheduleCreate {
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  is_all_day?: boolean;
  location?: string;
  color?: string;
}

export interface ScheduleUpdate {
  title?: string;
  description?: string;
  start_time?: string;
  end_time?: string;
  is_all_day?: boolean;
  location?: string;
  color?: string;
}

export interface ScheduleListResponse {
  schedules: Schedule[];
  total: number;
  page: number;
  page_size: number;
}

class ScheduleApiService {
  private baseUrl = '/api/schedules/';

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = AuthService.getInstance().getToken();
    
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async createSchedule(scheduleData: ScheduleCreate): Promise<Schedule> {
    return this.request<Schedule>('/', {
      method: 'POST',
      body: JSON.stringify(scheduleData),
    });
  }

  async getSchedules(params?: {
    start_date?: string;
    end_date?: string;
    page?: number;
    page_size?: number;
  }): Promise<ScheduleListResponse> {
    const searchParams = new URLSearchParams();
    if (params?.start_date) searchParams.append('start_date', params.start_date);
    if (params?.end_date) searchParams.append('end_date', params.end_date);
    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.page_size) searchParams.append('page_size', params.page_size.toString());

    const queryString = searchParams.toString();
    const endpoint = queryString ? `/?${queryString}` : '/';
    
    return this.request<ScheduleListResponse>(endpoint);
  }

  async getSchedulesByDateRange(startDate: string, endDate: string): Promise<Schedule[]> {
    const searchParams = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
    });
    
    return this.request<Schedule[]>(`/range?${searchParams.toString()}`);
  }

  async getUpcomingSchedules(limit: number = 10): Promise<Schedule[]> {
    return this.request<Schedule[]>(`/upcoming?limit=${limit}`);
  }

  async getSchedule(scheduleId: number): Promise<Schedule> {
    return this.request<Schedule>(`/${scheduleId}`);
  }

  async updateSchedule(scheduleId: number, scheduleData: ScheduleUpdate): Promise<Schedule> {
    return this.request<Schedule>(`/${scheduleId}`, {
      method: 'PUT',
      body: JSON.stringify(scheduleData),
    });
  }

  async deleteSchedule(scheduleId: number): Promise<void> {
    await this.request<void>(`/${scheduleId}`, {
      method: 'DELETE',
    });
  }
}

export const scheduleApi = new ScheduleApiService();
