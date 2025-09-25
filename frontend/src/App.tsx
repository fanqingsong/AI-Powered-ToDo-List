import React, { useState } from 'react';
import { Layout, Typography, Space, Badge } from 'antd';
import { ThunderboltOutlined } from '@ant-design/icons';
import TaskManager from './components/TaskManager';
import AIAssistant from './components/AIAssistant';
import './App.css';

const { Header, Content, Sider } = Layout;
const { Title, Text } = Typography;

const App: React.FC = () => {
  const [taskRefreshTrigger, setTaskRefreshTrigger] = useState(0);

  const handleChatResponse = () => {
    setTaskRefreshTrigger(prev => prev + 1);
  };

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
            AI 智能任务管理器 (Vite 超快热重载!) - 参考项目配置修复! 🎉 111
          </Title>
        </Space>
        
        <Space>
          <Badge count={0} showZero color="#52c41a">
            <Text style={{ color: '#fff' }}>任务管理</Text>
          </Badge>
          <Badge count={0} showZero color="#1890ff">
            <Text style={{ color: '#fff' }}>AI 助手</Text>
          </Badge>
        </Space>
      </Header>

      {/* 主要内容区域 */}
      <Content style={{ padding: '24px', background: '#f5f5f5' }}>
        <Layout style={{ 
          background: '#fff', 
          borderRadius: '8px', 
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          minHeight: 'calc(100vh - 84px)'
        }}>
          {/* 左侧任务管理区域 */}
          <Sider 
            width={400} 
            style={{ 
              background: '#fff',
              borderRight: '1px solid #f0f0f0',
              padding: '24px'
            }}
          >
            <TaskManager key={taskRefreshTrigger} />
          </Sider>

          {/* 右侧AI助手区域 */}
          <Content style={{ padding: '24px' }}>
            <AIAssistant onChatResponse={handleChatResponse} />
          </Content>
        </Layout>
      </Content>
    </Layout>
  );
};

export default App;