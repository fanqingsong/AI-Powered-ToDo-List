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
import { chatApi, conversationApi, ChatMessage, ConversationMessage } from '../services/api';
import { User } from '../services/authApi';

const { TextArea } = Input;
const { Title, Text } = Typography;

interface AIAssistantProps {
  onChatResponse?: () => void;
  user?: User | null;
  sessionId?: string;
}

interface ChatMessageWithId extends ChatMessage {
  id: string;
}

const AIAssistant: React.FC<AIAssistantProps> = ({ onChatResponse, user, sessionId: externalSessionId }) => {
  const [messages, setMessages] = useState<ChatMessageWithId[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(() => externalSessionId || `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [initialized, setInitialized] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  // 监听外部sessionId变化
  useEffect(() => {
    if (externalSessionId && externalSessionId !== sessionId) {
      // 更新sessionId状态
      setSessionId(externalSessionId);
      // 重置消息和初始化状态
      setMessages([]);
      setInitialized(false);
      // 重新加载会话历史
      loadConversationHistory(externalSessionId);
    }
  }, [externalSessionId]);

  // 加载会话历史
  const loadConversationHistory = async (targetSessionId?: string) => {
    const actualSessionId = targetSessionId || sessionId;
    try {
      // 如果用户已登录，使用用户ID，否则使用sessionId
      const userId = user ? user.id.toString() : actualSessionId;
      const history = await conversationApi.getHistory(actualSessionId, userId);
      const formattedMessages: ChatMessageWithId[] = history.map((msg: ConversationMessage) => ({
        id: msg.id.toString(),
        role: msg.role as 'user' | 'assistant',
        content: msg.content
      }));
      setMessages(formattedMessages);
      setInitialized(true);
    } catch (error) {
      console.error('Failed to load conversation history:', error);
      setInitialized(true); // 即使失败也标记为已初始化
    }
  };

  // 初始加载会话历史
  useEffect(() => {
    loadConversationHistory();
  }, [sessionId, user]);

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
      // 如果用户已登录，使用用户ID，否则使用sessionId
      const userId = user ? user.id.toString() : sessionId;
      
      // 使用流式处理
      let aiContent = '';
      const aiMessage: ChatMessageWithId = {
        id: Date.now().toString() + '-ai',
        role: 'assistant',
        content: '',
      };
      
      // 先添加空的AI消息到界面
      setMessages(prev => [...prev, aiMessage]);
      
      // 流式接收响应
      for await (const chunk of chatApi.sendMessageStream(userMessage.content, [], sessionId, userId)) {
        if (chunk.type === 'content') {
          aiContent += chunk.content;
          // 更新AI消息内容
          setMessages(prev => prev.map(msg => 
            msg.id === aiMessage.id 
              ? { ...msg, content: aiContent }
              : msg
          ));
        } else if (chunk.type === 'done') {
          break;
        }
      }
      
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

  const handleClearChat = async () => {
    try {
      // 如果用户已登录，使用用户ID，否则使用sessionId
      const userId = user ? user.id.toString() : sessionId;
      await conversationApi.clearHistory(sessionId, userId);
      setMessages([]);
      message.success('对话历史已清空');
    } catch (error) {
      console.error('Failed to clear conversation history:', error);
      message.error('清空对话历史失败');
      // 即使API调用失败，也清空本地状态
      setMessages([]);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // 如果还没有初始化完成，显示加载状态
  if (!initialized) {
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
      >
        <div style={{ textAlign: 'center', padding: '50px 0' }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>
            <Text type="secondary">正在加载会话历史...</Text>
          </div>
        </div>
      </Card>
    );
  }

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
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                <Spin size="small" />
                <span style={{ margin: 0 }}>AI 助手正在思考</span>
                <div style={{ display: 'inline-flex', alignItems: 'center', gap: '2px', marginLeft: '4px' }}>
                  <span style={{
                    width: '3px',
                    height: '3px',
                    borderRadius: '50%',
                    background: '#52c41a',
                    animation: 'thinkingPulse 1.4s infinite ease-in-out'
                  }}></span>
                  <span style={{
                    width: '3px',
                    height: '3px',
                    borderRadius: '50%',
                    background: '#52c41a',
                    animation: 'thinkingPulse 1.4s infinite ease-in-out',
                    animationDelay: '-0.16s'
                  }}></span>
                  <span style={{
                    width: '3px',
                    height: '3px',
                    borderRadius: '50%',
                    background: '#52c41a',
                    animation: 'thinkingPulse 1.4s infinite ease-in-out',
                    animationDelay: '0s'
                  }}></span>
                </div>
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
