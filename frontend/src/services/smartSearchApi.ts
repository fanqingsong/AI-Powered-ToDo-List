/**
 * 智能搜索API服务
 * 提供基于向量数据库的智能搜索功能
 */

import { Note, NoteCategory } from './noteApi';

// 智能搜索请求接口
export interface SmartSearchRequest {
  query: string;
  limit?: number;
  category?: NoteCategory;
  tags?: string[];
  include_archived?: boolean;
}

// 智能搜索响应接口
export interface SmartSearchResponse {
  notes: Note[];
  total: number;
  query: string;
  suggestions?: string[];
}

// 相似笔记请求接口
export interface SimilarNotesRequest {
  note_id: number;
  limit?: number;
}

// 搜索建议请求接口
export interface SearchSuggestionsRequest {
  query: string;
  limit?: number;
}

// 搜索统计信息接口
export interface SearchStats {
  total_notes: number;
  total_words: number;
  pinned_notes: number;
  archived_notes: number;
  category_stats: Record<string, number>;
  tag_stats: Record<string, number>;
  search_enabled: boolean;
  vector_db_status: string;
}

// 重新索引结果接口
export interface ReindexResult {
  user_id: number;
  total_notes: number;
  success_count: number;
  failed_count: number;
  status: string;
}

class SmartSearchApi {
  private baseUrl: string;

  constructor() {
    this.baseUrl = '/api/smart-search/';
  }

  /**
   * 智能搜索笔记
   */
  async smartSearch(request: SmartSearchRequest): Promise<SmartSearchResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/smart-search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        throw new Error(`智能搜索失败: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('智能搜索错误:', error);
      throw error;
    }
  }

  /**
   * 获取相似笔记
   */
  async getSimilarNotes(request: SimilarNotesRequest): Promise<Note[]> {
    try {
      const response = await fetch(`${this.baseUrl}/similar-notes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        throw new Error(`获取相似笔记失败: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('获取相似笔记错误:', error);
      throw error;
    }
  }

  /**
   * 获取搜索建议
   */
  async getSearchSuggestions(request: SearchSuggestionsRequest): Promise<string[]> {
    try {
      const response = await fetch(`${this.baseUrl}/search-suggestions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        throw new Error(`获取搜索建议失败: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('获取搜索建议错误:', error);
      throw error;
    }
  }

  /**
   * 获取搜索统计信息
   */
  async getSearchStats(): Promise<SearchStats> {
    try {
      const response = await fetch(`${this.baseUrl}/search-stats`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`获取搜索统计失败: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('获取搜索统计错误:', error);
      throw error;
    }
  }

  /**
   * 重新索引用户笔记
   */
  async reindexUserNotes(): Promise<ReindexResult> {
    try {
      const response = await fetch(`${this.baseUrl}/reindex`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`重新索引失败: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('重新索引错误:', error);
      throw error;
    }
  }

  /**
   * 搜索服务健康检查
   */
  async healthCheck(): Promise<{ status: string; vector_db_status: string; search_enabled: boolean }> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET'
      });

      if (!response.ok) {
        throw new Error(`健康检查失败: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('健康检查错误:', error);
      return {
        status: 'unhealthy',
        vector_db_status: 'error',
        search_enabled: false
      };
    }
  }
}

// 导出单例实例
export const smartSearchApi = new SmartSearchApi();
