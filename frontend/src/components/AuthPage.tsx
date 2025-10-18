import React, { useState } from 'react';
import { Layout, Typography, Space } from 'antd';
import { ThunderboltOutlined } from '@ant-design/icons';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';

const { Header, Content } = Layout;
const { Title } = Typography;

interface AuthPageProps {
  onAuthSuccess: (user: any) => void;
}

const AuthPage: React.FC<AuthPageProps> = ({ onAuthSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);

  const handleAuthSuccess = (user: any) => {
    onAuthSuccess(user);
  };

  const switchToRegister = () => {
    setIsLogin(false);
  };

  const switchToLogin = () => {
    setIsLogin(true);
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* 顶部导航栏 */}
      <Header style={{ 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
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
      </Header>

      {/* 主要内容区域 */}
      <Content style={{ 
        padding: '50px 24px', 
        background: '#f5f5f5',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 'calc(100vh - 60px)'
      }}>
        <div style={{ width: '100%', maxWidth: '500px' }}>
          {isLogin ? (
            <LoginForm 
              onLoginSuccess={handleAuthSuccess}
              onSwitchToRegister={switchToRegister}
            />
          ) : (
            <RegisterForm 
              onRegisterSuccess={handleAuthSuccess}
              onSwitchToLogin={switchToLogin}
            />
          )}
        </div>
      </Content>
    </Layout>
  );
};

export default AuthPage;
