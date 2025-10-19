import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 用户相关接口
export interface User {
  id: number;
  username: string;
  email: string;
  display_name?: string;
  role?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_login?: string;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
  display_name?: string;
}

export interface UserLogin {
  username: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  expires_in: number;
}

// 认证API
export const authApi = {
  // 用户注册
  register: async (userData: UserCreate): Promise<User> => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  // 用户登录
  login: async (credentials: UserLogin): Promise<Token> => {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  // 获取当前用户信息
  getCurrentUser: async (token: string): Promise<User> => {
    const response = await api.get('/auth/me', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    return response.data;
  },

  // 更新用户信息
  updateUser: async (token: string, userData: Partial<User>): Promise<User> => {
    const response = await api.put('/auth/me', userData, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    return response.data;
  },
};

// 认证状态管理
export class AuthService {
  private static instance: AuthService;
  private token: string | null = null;
  private user: User | null = null;

  private constructor() {
    // 从localStorage恢复token
    this.token = localStorage.getItem('auth_token');
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        this.user = JSON.parse(storedUser);
      } catch (e) {
        console.error("Failed to parse stored user data", e);
        this.clearAuthData();
      }
    }
  }

  static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService();
    }
    return AuthService.instance;
  }

  // 登录
  async login(credentials: UserLogin): Promise<User> {
    try {
      const tokenData = await authApi.login(credentials);
      this.token = tokenData.access_token;
      localStorage.setItem('auth_token', this.token);
      
      // 获取用户信息
      this.user = await authApi.getCurrentUser(this.token);
      localStorage.setItem('user', JSON.stringify(this.user));
      return this.user;
    } catch (error) {
      this.logout();
      throw error;
    }
  }

  // 注册
  async register(userData: UserCreate): Promise<User> {
    try {
      const user = await authApi.register(userData);
      // 注册成功后自动登录
      return await this.login({
        username: userData.username,
        password: userData.password,
      });
    } catch (error) {
      throw error;
    }
  }

  // 登出
  logout(): void {
    this.clearAuthData();
  }

  // 清除认证数据
  private clearAuthData() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    this.token = null;
    this.user = null;
  }

  // 验证token
  async validateToken(): Promise<void> {
    if (!this.token) return;
    
    try {
      this.user = await authApi.getCurrentUser(this.token);
      localStorage.setItem('user', JSON.stringify(this.user));
    } catch (error) {
      // token无效，清除
      this.clearAuthData();
    }
  }

  // 获取当前用户
  getCurrentUser(): User | null {
    return this.user;
  }

  // 获取token
  getToken(): string | null {
    return this.token;
  }

  // 检查是否已登录
  isAuthenticated(): boolean {
    return this.token !== null && this.user !== null;
  }

  // 更新用户信息
  async updateUser(userData: Partial<User>): Promise<User> {
    if (!this.token) {
      throw new Error('No authentication token');
    }
    
    try {
      const updatedUser = await authApi.updateUser(this.token, userData);
      this.user = updatedUser;
      return updatedUser;
    } catch (error) {
      throw error;
    }
  }

  // 获取认证头
  getAuthHeaders(): Record<string, string> {
    if (!this.token) return {};
    return {
      'Authorization': `Bearer ${this.token}`,
    };
  }
}

export default AuthService;
