import axios from 'axios';
import { AuthService } from './authApi';
// 静态导入 assistant-stream，确保 Vite 可以正确解析
import { createAssistantStreamResponse } from 'assistant-stream';

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
  // Assistant-UI 聊天 API (使用 /api/chat 接口)
  sendMessageAssistantUI: async function* (
    message: string,
    conversationHistory: ChatMessage[] = [],
    sessionId?: string,
    userId?: string
  ): AsyncGenerator<{ type: string; content: string; isStreaming?: boolean }, void, unknown> {
    try {
      const token = localStorage.getItem('auth_token');
      const baseApiUrl = import.meta.env.VITE_API_URL || "";
      const apiUrl = baseApiUrl.endsWith("/api") 
        ? baseApiUrl 
        : baseApiUrl 
          ? `${baseApiUrl}/api` 
          : "/api";
      
      // 构建消息历史
      const messages = conversationHistory.map(msg => ({
        role: msg.role,
        content: [{ type: "text", text: msg.content }]
      }));
      
      // 添加当前用户消息
      messages.push({
        role: "user",
        content: [{ type: "text", text: message }]
      });
      
      const response = await fetch(`${apiUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          messages,
          system: "",
          tools: []
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // 使用 assistant-stream 包解析 DataStreamResponse 格式的响应
      try {
        console.log('[DataStream] 使用 assistant-stream 解析响应');
        const dataStream = createAssistantStreamResponse(response);
        
        for await (const chunk of dataStream) {
          console.log('[DataStream] 收到 chunk:', chunk);
          
          if (chunk.type === 'text-delta' && chunk.textDelta) {
            yield {
              type: 'assistant',
              content: chunk.textDelta,
              isStreaming: true
            };
          } else if (chunk.type === 'text-done') {
            yield {
              type: 'assistant',
              content: '',
              isStreaming: false
            };
          } else if (chunk.type === 'error') {
            yield {
              type: 'error',
              content: chunk.error || '处理消息时出错',
              isStreaming: false
            };
            break;
          }
        }
      } catch (parseError) {
        // 如果解析失败，使用手动解析作为后备
        console.warn('[DataStream] assistant-stream 解析失败，使用手动解析:', parseError);
        
        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('No reader available');
        }

        const decoder = new TextDecoder();
        let buffer = '';
        let pendingEvent: { type: string } | null = null;
        let accumulatedText = ''; // 累积非标准格式的文本内容

        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) {
              // 流结束时，发送累积的文本
              if (accumulatedText) {
                yield {
                  type: 'assistant',
                  content: accumulatedText,
                  isStreaming: false
                };
                accumulatedText = '';
              }
              break;
            }

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (let i = 0; i < lines.length; i++) {
              const line = lines[i];
              if (line.trim() === '') continue;
              
              console.log('[DataStream] 收到行:', line);
              
              // DataStream 格式: 索引:"值"
              const match = line.match(/^(\d+):"(.*)"$/);
              if (match) {
                const [, indexStr, value] = match;
                const index = parseInt(indexStr, 10);
                
                // 处理转义字符
                const unescapedValue = value
                  .replace(/\\"/g, '"')
                  .replace(/\\n/g, '\n')
                  .replace(/\\r/g, '\r')
                  .replace(/\\t/g, '\t')
                  .replace(/\\\\/g, '\\')
                  .replace(/\\u([0-9a-fA-F]{4})/g, (match, hex) => String.fromCharCode(parseInt(hex, 16)));
                
                console.log(`[DataStream] 解析: index=${index}, value="${unescapedValue}"`);
                
                if (index === 0) {
                  // 检查是否是事件类型（如 "text-delta"）还是数据内容
                  if (unescapedValue === 'text-delta' || unescapedValue === 'text-done' || unescapedValue === 'error') {
                    // 如果之前有累积的文本，先发送
                    if (accumulatedText) {
                      yield {
                        type: 'assistant',
                        content: accumulatedText,
                        isStreaming: true
                      };
                      accumulatedText = '';
                    }
                    pendingEvent = { type: unescapedValue };
                    console.log(`[DataStream] 设置事件类型: ${unescapedValue}`);
                  } else {
                    // 如果 index=0 但不是事件类型，说明是数据内容（非标准格式）
                    // 累积字符，批量发送
                    accumulatedText += unescapedValue;
                    // 每累积一定长度或遇到换行时发送一次
                    if (accumulatedText.length >= 10 || unescapedValue === '\n') {
                      yield {
                        type: 'assistant',
                        content: accumulatedText,
                        isStreaming: true
                      };
                      accumulatedText = '';
                    }
                  }
                } else if (index === 1 && pendingEvent) {
                  // 标准格式：index=1 是数据
                  // 先发送累积的文本
                  if (accumulatedText) {
                    yield {
                      type: 'assistant',
                      content: accumulatedText,
                      isStreaming: true
                    };
                    accumulatedText = '';
                  }
                  
                  if (pendingEvent.type === 'text-delta') {
                    yield {
                      type: 'assistant',
                      content: unescapedValue,
                      isStreaming: true
                    };
                  } else if (pendingEvent.type === 'text-done') {
                    yield {
                      type: 'assistant',
                      content: '',
                      isStreaming: false
                    };
                  } else if (pendingEvent.type === 'error') {
                    yield {
                      type: 'error',
                      content: unescapedValue || '处理消息时出错',
                      isStreaming: false
                    };
                    break;
                  }
                  pendingEvent = null;
                } else if (index > 1) {
                  // 多行数据，继续追加
                  if (pendingEvent && pendingEvent.type === 'text-delta') {
                    yield {
                      type: 'assistant',
                      content: unescapedValue,
                      isStreaming: true
                    };
                  } else if (!pendingEvent) {
                    // 没有事件类型，累积文本
                    accumulatedText += unescapedValue;
                    if (accumulatedText.length >= 10) {
                      yield {
                        type: 'assistant',
                        content: accumulatedText,
                        isStreaming: true
                      };
                      accumulatedText = '';
                    }
                  }
                }
              } else {
                console.warn('[DataStream] 无法解析的行:', line);
              }
            }
          }
        } finally {
          reader.releaseLock();
        }
      }
      
      yield {
        type: 'done',
        content: '',
        isStreaming: false
      };
    } catch (error) {
      console.error('Assistant UI chat error:', error);
      yield {
        type: 'error',
        content: '连接失败，请检查网络或后端服务',
        isStreaming: false,
      };
    }
  },
  
  // 流式聊天 API (使用 /api/chat/stream 接口，保留向后兼容)
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
