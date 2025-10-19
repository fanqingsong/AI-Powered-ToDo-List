import React, { useState, useEffect } from 'react';
import { Button, Input, Space, Typography, Avatar, message } from 'antd';
import { SendOutlined, RobotOutlined, UserOutlined } from '@ant-design/icons';
import { User } from '../services/authApi';

const { TextArea } = Input;
const { Text } = Typography;

interface AssistantUIProps {
  user?: User | null;
  onPageNavigate?: (pageKey: string) => void;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

export const AssistantUI: React.FC<AssistantUIProps> = ({ user, onPageNavigate }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [loading, setLoading] = useState(false);

  // 监听消息中的页面跳转指令
  useEffect(() => {
    const lastMessage = messages[messages.length - 1];
    if (lastMessage?.role === 'assistant' && lastMessage.content) {
      const content = lastMessage.content;
      
      // 检查是否包含页面跳转指令
      if (content.includes('navigate_to_settings') || content.includes('打开系统设置')) {
        onPageNavigate?.('settings');
      } else if (content.includes('navigate_to_tasks') || content.includes('打开任务管理')) {
        onPageNavigate?.('tasks');
      } else if (content.includes('navigate_to_calendar') || content.includes('打开日程安排')) {
        onPageNavigate?.('calendar');
      } else if (content.includes('navigate_to_notes') || content.includes('打开笔记管理')) {
        onPageNavigate?.('notes');
      } else if (content.includes('navigate_to_analytics') || content.includes('打开数据分析')) {
        onPageNavigate?.('analytics');
      }
    }
  }, [messages, onPageNavigate]);

  const handleSendMessage = async () => {
    if (!currentMessage.trim()) {
      message.warning('请输入消息内容');
      return;
    }

    const userMessage: ChatMessage = {
      id: Date.now().toString() + '-user',
      role: 'user',
      content: currentMessage,
    };
    
    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setLoading(true);

    try {
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          sessionId: `session_${Date.now()}`,
          userId: user?.id?.toString() || 'anonymous',
        }),
      });

      if (!response.body) {
        throw new Error('No response body');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      const aiMessage: ChatMessage = {
        id: Date.now().toString() + '-ai',
        role: 'assistant',
        content: '',
      };
      
      setMessages(prev => [...prev, aiMessage]);

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                if (data.type === 'assistant' && data.content) {
                  setMessages(prev => prev.map(msg => 
                    msg.id === aiMessage.id 
                      ? { ...msg, content: msg.content + data.content }
                      : msg
                  ));
                } else if (data.type === 'done') {
                  break;
                }
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
      message.error('发送消息失败');
      console.error('Error sending message:', error);
      const aiMessageId = Date.now().toString() + '-ai';
      setMessages(prev => prev.map(msg => 
        msg.id === aiMessageId 
          ? { ...msg, content: '抱歉，AI 助手当前无法响应。请检查后端服务或配置。' }
          : msg
      ));
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div style={{ display: 'flex', height: '100%', flexDirection: 'column' }}>
      {/* 对话区域 */}
      <div style={{ flex: 1, padding: '16px', overflowY: 'auto' }}>
        {messages.length === 0 ? (
          <div style={{ 
            textAlign: 'center', 
            padding: '40px 20px',
            color: '#999'
          }}>
            <RobotOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
            <div>你好！我是你的 AI 助手</div>
            <div style={{ fontSize: '12px', marginTop: '8px' }}>
              我可以帮你管理任务、安排日程，或者回答任何问题
            </div>
            <div style={{ marginTop: '16px' }}>
              <Button 
                type="primary" 
                onClick={() => setCurrentMessage('看看系统设置')}
              >
                看看系统设置
              </Button>
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              style={{
                display: 'flex',
                justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                marginBottom: '16px',
              }}
            >
              <div
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  maxWidth: '80%',
                  flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
                }}
              >
                <Avatar
                  icon={msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                  style={{
                    backgroundColor: msg.role === 'user' ? '#1890ff' : '#52c41a',
                    margin: msg.role === 'user' ? '0 0 0 8px' : '0 8px 0 0',
                  }}
                />
                <div
                  style={{
                    backgroundColor: msg.role === 'user' ? '#1890ff' : '#f0f0f0',
                    color: msg.role === 'user' ? '#fff' : '#000',
                    padding: '8px 12px',
                    borderRadius: '12px',
                    whiteSpace: 'pre-wrap',
                    wordWrap: 'break-word',
                  }}
                >
                  <div style={{ fontSize: '12px', opacity: 0.8, marginBottom: '4px' }}>
                    {msg.role === 'user' ? '您' : 'AI 助手'}
                  </div>
                  <div>{msg.content}</div>
                </div>
              </div>
            </div>
          ))
        )}
        
        {loading && (
          <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'flex-start' }}>
              <Avatar
                icon={<RobotOutlined />}
                style={{ backgroundColor: '#52c41a', marginRight: '8px' }}
              />
              <div
                style={{
                  backgroundColor: '#f0f0f0',
                  padding: '8px 12px',
                  borderRadius: '12px',
                }}
              >
                <Text type="secondary">AI 助手正在思考...</Text>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 输入区域 */}
      <div style={{ padding: '16px', borderTop: '1px solid #e8e8e8' }}>
        <Space.Compact style={{ width: '100%' }}>
          <TextArea
            value={currentMessage}
            onChange={(e) => setCurrentMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="输入您的消息... (Enter 发送，Shift+Enter 换行)"
            autoSize={{ minRows: 1, maxRows: 3 }}
            style={{ flexGrow: 1 }}
            disabled={loading}
          />
          <Button 
            type="primary" 
            icon={<SendOutlined />} 
            onClick={handleSendMessage}
            loading={loading}
            disabled={!currentMessage.trim()}
          >
            发送
          </Button>
        </Space.Compact>
      </div>
    </div>
  );
};

export default AssistantUI;
