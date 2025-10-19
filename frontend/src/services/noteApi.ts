import axios from 'axios';

const baseUrl = '/api/notes';

// 笔记分类枚举
export enum NoteCategory {
  PERSONAL = 'PERSONAL',
  WORK = 'WORK',
  STUDY = 'STUDY',
  IDEA = 'IDEA',
  MEETING = 'MEETING',
  OTHER = 'OTHER'
}

// 笔记接口
export interface Note {
  id: number;
  title: string;
  content: string;
  category: NoteCategory;
  tags: string[];
  is_pinned: boolean;
  is_archived: boolean;
  word_count: number;
  last_accessed: string;
  created_at: string;
  updated_at: string;
  user_id: number;
}

// 创建笔记请求
export interface CreateNoteRequest {
  title: string;
  content: string;
  category: NoteCategory;
  tags?: string[];
  is_pinned?: boolean;
  is_archived?: boolean;
}

// 更新笔记请求
export interface UpdateNoteRequest {
  title?: string;
  content?: string;
  category?: NoteCategory;
  tags?: string[];
  is_pinned?: boolean;
  is_archived?: boolean;
}

// 搜索笔记请求
export interface SearchNoteRequest {
  query?: string;
  category?: NoteCategory;
  tags?: string[];
  is_pinned?: boolean;
  is_archived?: boolean;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

// 笔记列表响应
export interface NoteListResponse {
  notes: Note[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// 笔记统计响应
export interface NoteStatsResponse {
  total_notes: number;
  notes_by_category: Record<string, number>;
  total_words: number;
  pinned_notes: number;
  archived_notes: number;
  recent_notes: number;
}

class NoteApiService {
  private getAuthHeaders() {
    const token = localStorage.getItem('auth_token');
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  }

  // 创建笔记
  async createNote(noteData: CreateNoteRequest): Promise<Note> {
    try {
      const response = await axios.post(baseUrl, noteData, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '创建笔记失败');
    }
  }

  // 获取单个笔记
  async getNote(noteId: number): Promise<Note> {
    try {
      const response = await axios.get(`${baseUrl}/${noteId}`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '获取笔记失败');
    }
  }

  // 更新笔记
  async updateNote(noteId: number, noteData: UpdateNoteRequest): Promise<Note> {
    try {
      const response = await axios.put(`${baseUrl}/${noteId}`, noteData, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '更新笔记失败');
    }
  }

  // 删除笔记
  async deleteNote(noteId: number): Promise<void> {
    try {
      await axios.delete(`${baseUrl}/${noteId}`, {
        headers: this.getAuthHeaders()
      });
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '删除笔记失败');
    }
  }

  // 搜索笔记
  async searchNotes(searchRequest: SearchNoteRequest): Promise<NoteListResponse> {
    try {
      const response = await axios.post(`${baseUrl}/search`, searchRequest, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '搜索笔记失败');
    }
  }

  // 根据分类获取笔记
  async getNotesByCategory(category: NoteCategory, limit: number = 20): Promise<Note[]> {
    try {
      const response = await axios.get(`${baseUrl}/category/${category}`, {
        params: { limit },
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '获取分类笔记失败');
    }
  }

  // 获取置顶笔记
  async getPinnedNotes(): Promise<Note[]> {
    try {
      const response = await axios.get(`${baseUrl}/pinned/list`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '获取置顶笔记失败');
    }
  }

  // 获取最近笔记
  async getRecentNotes(days: number = 7, limit: number = 20): Promise<Note[]> {
    try {
      const response = await axios.get(`${baseUrl}/recent/list`, {
        params: { days, limit },
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '获取最近笔记失败');
    }
  }

  // 获取笔记统计
  async getNoteStats(): Promise<NoteStatsResponse> {
    try {
      const response = await axios.get(`${baseUrl}/stats/overview`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '获取笔记统计失败');
    }
  }

  // 切换置顶状态
  async togglePin(noteId: number): Promise<Note> {
    try {
      const response = await axios.patch(`${baseUrl}/${noteId}/pin`, {}, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '切换置顶状态失败');
    }
  }

  // 切换归档状态
  async toggleArchive(noteId: number): Promise<Note> {
    try {
      const response = await axios.patch(`${baseUrl}/${noteId}/archive`, {}, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '切换归档状态失败');
    }
  }

  // 添加标签
  async addTag(noteId: number, tag: string): Promise<Note> {
    try {
      const response = await axios.post(`${baseUrl}/${noteId}/tags`, null, {
        params: { tag },
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '添加标签失败');
    }
  }

  // 移除标签
  async removeTag(noteId: number, tag: string): Promise<Note> {
    try {
      const response = await axios.delete(`${baseUrl}/${noteId}/tags`, {
        params: { tag },
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '移除标签失败');
    }
  }
}

export const noteApiService = new NoteApiService();
