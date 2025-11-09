import React, { useState, useEffect, useCallback } from 'react';
import { Layout, Typography, Space, Badge, Button } from 'antd';
import { ThunderboltOutlined, RobotOutlined } from '@ant-design/icons';
import TaskManager from './components/TaskManager';
import ScheduleManager from './components/ScheduleManager';
import NoteManager from './components/NoteManager';
import AnalyticsManager from './components/AnalyticsManager';
import SideMenu from './components/SideMenu';
import CopilotSidebar from './components/CopilotSidebar';
import AuthPage from './components/AuthPage';
import UserInfo from './components/UserInfo';
import UserManagement from './components/UserManagement';
import ErrorBoundary from './components/ErrorBoundary';
import Footer from './components/Footer';
import { AuthService, User } from './services/authApi';
import './App.css';

const { Header } = Layout;
const { Title, Text } = Typography;

const App: React.FC = () => {
  const [taskRefreshTrigger, setTaskRefreshTrigger] = useState(0);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentSessionId, setCurrentSessionId] = useState<string>('');
  const [isCopilotCollapsed, setIsCopilotCollapsed] = useState(false);
  const [copilotWidth, setCopilotWidth] = useState(450);
  const [isCopilotResizing, setIsCopilotResizing] = useState(false);
  const [selectedMenuKey, setSelectedMenuKey] = useState('tasks');
  const [isMenuCollapsed, setIsMenuCollapsed] = useState(true); // 默认收起
  const authService = AuthService.getInstance();

  useEffect(() => {
    // 检查用户是否已登录
    const checkAuth = async () => {
      try {
        if (authService.isAuthenticated()) {
          const currentUser = authService.getCurrentUser();
          if (currentUser) {
            setUser(currentUser);
          } else {
            // 如果有token但没有用户信息，尝试验证token
            await authService.validateToken();
            const user = authService.getCurrentUser();
            if (user) {
              setUser(user);
            }
          }
        }
      } catch (error) {
        console.error('Auth check failed:', error);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const handleAuthSuccess = (userData: User) => {
    setUser(userData);
  };

  const handleLogout = () => {
    authService.logout();
    setUser(null);
  };

  const handleUserUpdate = (updatedUser: User) => {
    setUser(updatedUser);
  };

  const handleMenuSelect = (key: string) => {
    setSelectedMenuKey(key);
  };

  const handleToggleMenu = () => {
    setIsMenuCollapsed(prev => !prev);
  };

  // 监听前端工具调用的页面导航事件
  useEffect(() => {
    const handleNavigateToPage = (event: CustomEvent) => {
      console.log('🧭 收到页面导航事件:', event.detail);
      const { page } = event.detail;
      setSelectedMenuKey(page);
    };

    window.addEventListener('navigateToPage', handleNavigateToPage as EventListener);
    
    return () => {
      window.removeEventListener('navigateToPage', handleNavigateToPage as EventListener);
    };
  }, []);

  const handleSessionSelect = (sessionId: string) => {
    setCurrentSessionId(sessionId);
  };

  const handleChatResponse = useCallback(() => {
    setTaskRefreshTrigger(prev => prev + 1);
  }, []);

  const handleRefreshTaskList = useCallback(() => {
    console.log('🔄 刷新任务列表');
    setTaskRefreshTrigger(prev => prev + 1);
  }, []);

  const handleToggleCopilot = () => {
    setIsCopilotCollapsed(prev => !prev);
  };

  // copilot拖拽调整宽度处理函数
  const handleCopilotMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    console.log('copilot拖拽开始', { startX: e.clientX, startWidth: copilotWidth });
    
    setIsCopilotResizing(true);
    document.body.classList.add('resizing');
    
    const startX = e.clientX;
    const startWidth = copilotWidth;
    
    const handleMouseMove = (e: MouseEvent) => {
      e.preventDefault();
      const deltaX = startX - e.clientX; // 注意这里是反向的，因为是从右边向左拖拽
      const newWidth = Math.max(280, Math.min(600, startWidth + deltaX));
      
      console.log('copilot拖拽中', { deltaX, newWidth });
      setCopilotWidth(newWidth);
    };
    
    const handleMouseUp = (e: MouseEvent) => {
      e.preventDefault();
      console.log('copilot拖拽结束');
      
      setIsCopilotResizing(false);
      document.body.classList.remove('resizing');
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
    
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  };

  // 如果正在加载，显示加载状态
  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        background: '#f5f5f5'
      }}>
        <div style={{ textAlign: 'center' }}>
          <ThunderboltOutlined style={{ fontSize: '48px', color: '#1890ff', marginBottom: '16px' }} />
          <div>正在加载...</div>
        </div>
      </div>
    );
  }

  // 如果用户未登录，显示认证页面
  if (!user) {
    return <AuthPage onAuthSuccess={handleAuthSuccess} />;
  }

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* 顶部导航栏 */}
      <Header style={{ 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '60px',
        lineHeight: '60px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        flexShrink: 0
      }}>
        <Space align="center">
          <ThunderboltOutlined style={{ fontSize: '24px', color: '#fff' }} />
          <Title level={3} style={{ color: '#fff', margin: 0 }}>
            AI Native 智能工作台
          </Title>
        </Space>
        
        <Space>
          <Badge count={0} showZero color="#52c41a">
            <Text style={{ color: '#fff' }}>AI 助手</Text>
          </Badge>
          <Button
            type="text"
            icon={<RobotOutlined />}
            onClick={handleToggleCopilot}
            style={{ color: '#fff' }}
            title={isCopilotCollapsed ? '展开AI助手' : '收缩AI助手'}
          >
            AI 助手
          </Button>
          <UserInfo 
            user={user} 
            onLogout={handleLogout}
            onUserUpdate={handleUserUpdate}
          />
        </Space>
      </Header>

      {/* 主要内容区域 */}
      <div style={{ 
        flex: 1,
        display: 'flex',
        overflow: 'hidden'
      }}>
        {/* 左侧菜单区域 */}
        <div 
          style={{ 
            width: isMenuCollapsed ? '80px' : '280px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            boxShadow: '2px 0 20px rgba(0,0,0,0.1)',
            display: 'flex',
            flexDirection: 'column',
            flexShrink: 0,
            transition: 'width 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            overflow: 'hidden'
          }}
        >
          <SideMenu 
            selectedKey={selectedMenuKey}
            onMenuSelect={handleMenuSelect}
            collapsed={isMenuCollapsed}
            onToggleCollapse={handleToggleMenu}
          />
        </div>

        {/* 中间工作区域 */}
        <div style={{ 
          flex: 1,
          background: '#f5f5f5',
          marginRight: isCopilotCollapsed ? '60px' : `${copilotWidth}px`,
          transition: isCopilotResizing ? 'none' : 'margin-right 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}>
          <div style={{ 
            flex: 1,
            padding: '24px',
            background: '#fff',
            margin: '24px',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            overflow: 'auto'
          }}>
            {selectedMenuKey === 'tasks' ? (
              <TaskManager refreshTrigger={taskRefreshTrigger} />
            ) : selectedMenuKey === 'calendar' ? (
              <ErrorBoundary>
                <ScheduleManager />
              </ErrorBoundary>
            ) : selectedMenuKey === 'notes' ? (
              <ErrorBoundary>
                <NoteManager />
              </ErrorBoundary>
            ) : selectedMenuKey === 'analytics' ? (
              <ErrorBoundary>
                <AnalyticsManager />
              </ErrorBoundary>
            ) : selectedMenuKey === 'settings' ? (
              <ErrorBoundary>
                <UserManagement currentUser={user} />
              </ErrorBoundary>
            ) : (
              <div style={{ 
                textAlign: 'center', 
                padding: '50px 20px',
                color: '#999'
              }}>
                <ThunderboltOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
                <div style={{ fontSize: '18px', marginBottom: '8px' }}>
                  功能开发中
                </div>
                <div style={{ fontSize: '14px' }}>
                  该功能正在开发中，敬请期待
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <Footer />
        </div>

        {/* Copilot侧边栏 */}
        <CopilotSidebar
          onChatResponse={handleChatResponse}
          user={user}
          sessionId={currentSessionId}
          isCollapsed={isCopilotCollapsed}
          onToggleCollapse={handleToggleCopilot}
          onSessionSelect={handleSessionSelect}
          onPageNavigate={handleMenuSelect}
          onRefreshTaskList={handleRefreshTaskList}
          width={copilotWidth}
          isResizing={isCopilotResizing}
          onMouseDown={handleCopilotMouseDown}
        />
      </div>
    </div>
  );
};

export default App;