import React, { useState, useRef, useEffect } from 'react';
import {
  Card,
  Input,
  Button,
  Space,
  message,
  Typography,
  Avatar,
  Divider,
  Spin,
} from 'antd';
import {
  SendOutlined,
  ClearOutlined,
  RobotOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { chatApi, ChatMessage } from '../services/api';

const { TextArea } = Input;
const { Title, Text } = Typography;

interface AIAssistantProps {
  onChatResponse?: () => void;
}

interface ChatMessageWithId extends ChatMessage {
  id: string;
}

const AIAssistant: React.FC<AIAssistantProps> = ({ onChatResponse }) => {
  const [messages, setMessages] = useState<ChatMessageWithId[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSendMessage = async () => {
    if (!currentMessage.trim()) {
      message.warning('请输入消息内容');
      return;
    }

    const userMessage: ChatMessageWithId = {
      id: Date.now().toString() + '-user',
      role: 'user',
      content: currentMessage,
    };
    
    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setLoading(true);

    try {
      const aiResponse = await chatApi.sendMessage(userMessage.content);
      const aiMessage: ChatMessageWithId = {
        id: Date.now().toString() + '-ai',
        role: 'assistant',
        content: aiResponse.content,
      };
      
      setMessages(prev => [...prev, aiMessage]);
      
      // 触发任务列表刷新
      if (onChatResponse) {
        onChatResponse();
      }
    } catch (error) {
      message.error('发送消息失败');
      console.error('Error sending message:', error);
      const errorMessage: ChatMessageWithId = {
        id: Date.now().toString() + '-error',
        role: 'assistant',
        content: '抱歉，AI 助手当前无法响应。请检查后端服务或配置。',
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Card 
      title={
        <Space>
          <RobotOutlined style={{ color: '#52c41a' }} />
          <Title level={4} style={{ margin: 0 }}>
            AI 助手
          </Title>
        </Space>
      }
      style={{ height: '100%' }}
      extra={
        <Button 
          icon={<ClearOutlined />} 
          onClick={handleClearChat}
          size="small"
        >
          清空对话
        </Button>
      }
    >
      {/* 代理选择器 */}
      <div style={{ marginBottom: 16 }}>
        <Text strong style={{ marginRight: 8 }}>选择代理:</Text>
        <div style={{ 
          padding: '8px 12px', 
          backgroundColor: '#f0f2f5', 
          borderRadius: '6px',
          border: '1px solid #d9d9d9',
          display: 'inline-block'
        }}>
          <Text type="secondary">LangGraph Agent</Text>
        </div>
      </div>

      <Divider />

      {/* 聊天消息区域 */}
      <div 
        style={{ 
          height: 'calc(100vh - 400px)', 
          overflowY: 'auto', 
          marginBottom: 16,
          padding: '8px 0',
        }}
      >
        {messages.length === 0 ? (
          <div style={{ 
            textAlign: 'center', 
            padding: '40px 20px',
            color: '#999'
          }}>
            <RobotOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
            <div>开始与 AI 助手对话</div>
            <div style={{ fontSize: '12px', marginTop: '8px' }}>
              您可以询问任务管理相关问题
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
                <Spin size="small" />
                <span style={{ marginLeft: '8px' }}>AI 助手正在思考...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <Divider />

      {/* 输入区域 */}
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
    </Card>
  );
};

export default AIAssistant;
