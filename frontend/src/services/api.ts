import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

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
  sendMessage: async (message: string, conversationHistory?: ChatMessage[], sessionId?: string): Promise<ChatMessage> => {
    const response = await api.post('/chat/langgraph', { 
      message, 
      conversation_history: conversationHistory,
      sessionId: sessionId
    });
    return response.data;
  },
};

export default api;
