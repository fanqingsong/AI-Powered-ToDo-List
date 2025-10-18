import React, { useState, useEffect } from 'react';
import { Layout, Typography, Space, Badge, Button } from 'antd';
import { ThunderboltOutlined, RobotOutlined } from '@ant-design/icons';
import TaskManager from './components/TaskManager';
import SideMenu from './components/SideMenu';
import CopilotSidebar from './components/CopilotSidebar';
import AuthPage from './components/AuthPage';
import UserInfo from './components/UserInfo';
import { AuthService, User } from './services/authApi';
import './App.css';

const { Header, Content, Sider } = Layout;
const { Title, Text } = Typography;

const App: React.FC = () => {
  const [taskRefreshTrigger, setTaskRefreshTrigger] = useState(0);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentSessionId, setCurrentSessionId] = useState<string>('');
  const [isCopilotCollapsed, setIsCopilotCollapsed] = useState(false);
  const [copilotWidth, setCopilotWidth] = useState(600);
  const [isCopilotResizing, setIsCopilotResizing] = useState(false);
  const [selectedMenuKey, setSelectedMenuKey] = useState('tasks');
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

  const handleSessionSelect = (sessionId: string) => {
    setCurrentSessionId(sessionId);
  };

  const handleChatResponse = () => {
    setTaskRefreshTrigger(prev => prev + 1);
  };

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
      const newWidth = Math.max(300, Math.min(800, startWidth + deltaX));
      
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
    <Layout style={{ minHeight: '100vh' }}>
      {/* 顶部导航栏 */}
      <Header style={{ 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: 'auto',
        minHeight: '60px',
        lineHeight: '60px'
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
      <Content style={{ 
        padding: '24px', 
        background: '#f5f5f5',
        marginRight: isCopilotCollapsed ? '60px' : `${copilotWidth}px`,
        transition: isCopilotResizing ? 'none' : 'margin-right 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
      }}>
        <Layout style={{ 
          background: '#fff', 
          borderRadius: '8px', 
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          minHeight: 'calc(100vh - 84px)'
        }}>
          {/* 左侧菜单区域 */}
          <Sider 
            width={200} 
            style={{ 
              background: '#fff',
              borderRight: '1px solid #f0f0f0'
            }}
          >
            <SideMenu 
              selectedKey={selectedMenuKey}
              onMenuSelect={handleMenuSelect}
            />
          </Sider>

          {/* 中间工作区域 */}
          <Content style={{ padding: '24px' }}>
            {selectedMenuKey === 'tasks' ? (
              <TaskManager key={taskRefreshTrigger} />
            ) : (
              <div style={{ 
                textAlign: 'center', 
                padding: '50px 20px',
                color: '#999'
              }}>
                <ThunderboltOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
                <div style={{ fontSize: '18px', marginBottom: '8px' }}>
                  {selectedMenuKey === 'calendar' && '日程安排功能'}
                  {selectedMenuKey === 'notes' && '笔记管理功能'}
                  {selectedMenuKey === 'analytics' && '数据分析功能'}
                  {selectedMenuKey === 'settings' && '系统设置功能'}
                  {!['calendar', 'notes', 'analytics', 'settings'].includes(selectedMenuKey) && '功能开发中'}
                </div>
                <div style={{ fontSize: '14px' }}>
                  该功能正在开发中，敬请期待
                </div>
              </div>
            )}
          </Content>
        </Layout>
      </Content>

      {/* Copilot侧边栏 */}
      <CopilotSidebar
        onChatResponse={handleChatResponse}
        user={user}
        sessionId={currentSessionId}
        isCollapsed={isCopilotCollapsed}
        onToggleCollapse={handleToggleCopilot}
        onSessionSelect={handleSessionSelect}
        width={copilotWidth}
        isResizing={isCopilotResizing}
        onMouseDown={handleCopilotMouseDown}
      />
    </Layout>
  );
};

export default App;