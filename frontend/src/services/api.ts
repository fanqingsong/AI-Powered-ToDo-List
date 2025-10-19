import axios from 'axios';
import { AuthService } from './authApi';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器，自动添加认证头
api.interceptors.request.use(
  (config) => {
    const authService = AuthService.getInstance();
    const authHeaders = authService.getAuthHeaders();
    if (authHeaders.Authorization) {
      config.headers.Authorization = authHeaders.Authorization;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器，处理认证错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 认证失败，清除本地认证信息
      const authService = AuthService.getInstance();
      authService.logout();
      
      // 刷新页面以触发重新认证检查
      if (typeof window !== 'undefined') {
        // 避免在服务端渲染时执行
        window.location.reload();
      }
    }
    return Promise.reject(error);
  }
);

export interface Task {
  id: number;
  title: string;
  isComplete: boolean;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  conversation_history?: ChatMessage[];
  sessionId?: string;
  userId?: string;
}

export interface ConversationMessage {
  id: number;
  session_id: string;
  user_id?: string;
  role: string;
  content: string;
  message_order: number;
  metadata?: any;
  created_at: string;
}

export interface ConversationStats {
  session_id: string;
  total_messages: number;
  last_message_time?: string;
  user_id?: string;
}

// Task API
export const taskApi = {
  getAllTasks: async (): Promise<Task[]> => {
    const response = await api.get('/tasks');
    return response.data;
  },

  createTask: async (title: string, isComplete: boolean = false): Promise<Task> => {
    const response = await api.post('/tasks', { title, isComplete });
    return response.data;
  },

  updateTask: async (id: number, title?: string, isComplete?: boolean): Promise<Task> => {
    const response = await api.put(`/tasks/${id}`, { title, isComplete });
    return response.data;
  },

  deleteTask: async (id: number): Promise<void> => {
    await api.delete(`/tasks/${id}`);
  },
};

// Chat API
export const chatApi = {
  // 流式聊天 API
  sendMessageStream: async function* (
    message: string,
    conversationHistory: ChatMessage[] = [],
    sessionId?: string,
    userId?: string
  ): AsyncGenerator<{ type: string; content: string; isStreaming?: boolean }, void, unknown> {
    try {
      const token = localStorage.getItem('auth_token');
      console.log('[DEBUG] 流式聊天认证信息:', { token: token ? 'exists' : 'null', userId, sessionId });
      
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message,
          conversation_history: conversationHistory,
          sessionId: sessionId || `session_${Date.now()}`,
          userId: userId || sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No reader available');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                yield data;
              } catch (e) {
                console.warn('Failed to parse SSE data:', line);
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }
    } catch (error) {
      console.error('Stream chat error:', error);
      yield {
        type: 'error',
        content: '连接失败，请检查网络或后端服务',
        isStreaming: false,
      };
    }
  },
};

// Conversation API
export const conversationApi = {
  getHistory: async (sessionId: string, userId?: string, limit: number = 50): Promise<ConversationMessage[]> => {
    const params = new URLSearchParams();
    if (userId) params.append('user_id', userId);
    params.append('limit', limit.toString());
    
    const response = await api.get(`/conversations/${sessionId}?${params}`);
    return response.data;
  },

  clearHistory: async (sessionId: string, userId?: string): Promise<void> => {
    const params = new URLSearchParams();
    if (userId) params.append('user_id', userId);
    
    await api.delete(`/conversations/${sessionId}?${params}`);
  },

  getStats: async (sessionId: string, userId?: string): Promise<ConversationStats> => {
    const params = new URLSearchParams();
    if (userId) params.append('user_id', userId);
    
    const response = await api.get(`/conversations/stats/${sessionId}?${params}`);
    return response.data;
  },

  getUserSessions: async (userId: string, limit: number = 20): Promise<any[]> => {
    const response = await api.get(`/conversations/user/${userId}?limit=${limit}`);
    return response.data;
  },

  createSession: async (userId: number, sessionName?: string): Promise<any> => {
    const response = await api.post('/auth/sessions', {
      user_id: userId,
      session_name: sessionName
    });
    return response.data;
  },

  deleteSession: async (sessionId: string): Promise<void> => {
    await api.delete(`/auth/sessions/${sessionId}`);
  },
};

export default api;
