import React, { useState, useRef, useEffect } from 'react';
import {
  Input,
  Button,
  message,
  Typography,
  Avatar,
  Spin,
  Modal,
  Popconfirm,
  Tag,
} from 'antd';
import {
  SendOutlined,
  ClearOutlined,
  RobotOutlined,
  UserOutlined,
  MenuOutlined,
  CloseOutlined,
  PlusOutlined,
  PictureOutlined,
  AudioOutlined,
  MessageOutlined,
  EditOutlined,
  DeleteOutlined,
  ClockCircleOutlined,
  DoubleLeftOutlined,
  DoubleRightOutlined,
} from '@ant-design/icons';
import { chatApi, conversationApi, ChatMessage, ConversationMessage } from '../services/api';
import { User } from '../services/authApi';
import './CopilotSidebar.css';

const { TextArea } = Input;
const { Text } = Typography;

interface UserSession {
  id: number;
  session_id: string;
  session_name?: string;
  user_id: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_activity: string;
}

interface CopilotSidebarProps {
  onChatResponse?: () => void;
  user?: User | null;
  sessionId?: string;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
  onSessionSelect?: (sessionId: string) => void;
  width?: number;
  isResizing?: boolean;
  onMouseDown?: (e: React.MouseEvent) => void;
}

interface ChatMessageWithId extends ChatMessage {
  id: string;
}

const CopilotSidebar: React.FC<CopilotSidebarProps> = ({ 
  onChatResponse, 
  user, 
  sessionId: externalSessionId,
  isCollapsed = false,
  onToggleCollapse,
  onSessionSelect,
  width = 600,
  isResizing = false,
  onMouseDown
}) => {
  const [messages, setMessages] = useState<ChatMessageWithId[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(() => externalSessionId || `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [initialized, setInitialized] = useState(false);
  const [isSessionsCollapsed, setIsSessionsCollapsed] = useState(true);
  const [sessionsPanelWidth, setSessionsPanelWidth] = useState(200);
  const [isSessionsResizing, setIsSessionsResizing] = useState(false);
  
  // 会话管理相关状态
  const [sessions, setSessions] = useState<UserSession[]>([]);
  const [sessionsLoading, setSessionsLoading] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [editingSession, setEditingSession] = useState<UserSession | null>(null);
  const [sessionName, setSessionName] = useState('');
  const [createLoading, setCreateLoading] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  // 监听外部sessionId变化
  useEffect(() => {
    if (externalSessionId && externalSessionId !== sessionId) {
      setSessionId(externalSessionId);
      setMessages([]);
      setInitialized(false);
      loadConversationHistory(externalSessionId);
    }
  }, [externalSessionId]);

  // 加载会话历史
  const loadConversationHistory = async (targetSessionId?: string) => {
    const actualSessionId = targetSessionId || sessionId;
    try {
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
      setInitialized(true);
    }
  };

  useEffect(() => {
    loadConversationHistory();
  }, [sessionId, user]);

  // 加载会话列表
  useEffect(() => {
    if (user) {
      loadSessions();
    }
  }, [user]);

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

    // 创建 AI 消息占位符
    const aiMessageId = Date.now().toString() + '-ai';
    const aiMessage: ChatMessageWithId = {
      id: aiMessageId,
      role: 'assistant',
      content: '',
    };
    
    setMessages(prev => [...prev, aiMessage]);

    try {
      const userId = user ? user.id.toString() : sessionId;
      
      // 使用流式 API
      for await (const chunk of chatApi.sendMessageStream(
        userMessage.content, 
        undefined, 
        sessionId, 
        userId
      )) {
        if (chunk.type === 'assistant' && chunk.content) {
          // 更新 AI 消息内容
          setMessages(prev => prev.map(msg => 
            msg.id === aiMessageId 
              ? { ...msg, content: msg.content + chunk.content }
              : msg
          ));
        } else if (chunk.type === 'error') {
          // 处理错误
          setMessages(prev => prev.map(msg => 
            msg.id === aiMessageId 
              ? { ...msg, content: chunk.content }
              : msg
          ));
          message.error('AI 响应出错');
          break;
        } else if (chunk.type === 'done') {
          // 流式响应完成
          break;
        }
      }
      
      if (onChatResponse) {
        onChatResponse();
      }
    } catch (error) {
      message.error('发送消息失败');
      console.error('Error sending message:', error);
      setMessages(prev => prev.map(msg => 
        msg.id === aiMessageId 
          ? { ...msg, content: '抱歉，AI 助手当前无法响应。请检查后端服务或配置。' }
          : msg
      ));
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = async () => {
    try {
      const userId = user ? user.id.toString() : sessionId;
      await conversationApi.clearHistory(sessionId, userId);
      setMessages([]);
      message.success('对话历史已清空');
    } catch (error) {
      console.error('Failed to clear conversation history:', error);
      message.error('清空对话历史失败');
      setMessages([]);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setCurrentMessage(e.target.value);
  };

  // 会话管理相关函数
  const loadSessions = async () => {
    if (!user) return;
    
    setSessionsLoading(true);
    try {
      const sessions = await conversationApi.getUserSessions(user.id.toString());
      setSessions(sessions);
      
      // 如果没有当前选中的会话，自动选择第一个会话
      if (!externalSessionId && sessions.length > 0) {
        const firstSession = sessions[0];
        setSessionId(firstSession.session_id);
        if (onSessionSelect) {
          onSessionSelect(firstSession.session_id);
        }
      }
    } catch (error) {
      console.error('Failed to load sessions:', error);
      message.error('加载会话列表失败');
      setSessions([]);
    } finally {
      setSessionsLoading(false);
    }
  };

  const handleQuickCreateSession = async () => {
    if (!user) {
      message.warning('请先登录');
      return;
    }

    setCreateLoading(true);
    try {
      // 生成默认会话名称
      const defaultSessionName = `会话 ${new Date().toLocaleString('zh-CN', { 
        month: '2-digit', 
        day: '2-digit', 
        hour: '2-digit', 
        minute: '2-digit' 
      })}`;
      
      const newSession = await conversationApi.createSession(user.id, defaultSessionName);
      setSessions(prev => [newSession, ...prev]);
      message.success('新会话创建成功');
      
      // 自动选择新创建的会话
      setSessionId(newSession.session_id);
      if (onSessionSelect) {
        onSessionSelect(newSession.session_id);
      }
    } catch (error) {
      console.error('Failed to create session:', error);
      message.error('创建会话失败');
    } finally {
      setCreateLoading(false);
    }
  };

  const handleEditSession = async () => {
    if (!editingSession || !sessionName.trim()) {
      message.warning('请输入会话名称');
      return;
    }

    try {
      setSessions(prev => prev.map(session => 
        session.id === editingSession.id 
          ? { ...session, session_name: sessionName, updated_at: new Date().toISOString() }
          : session
      ));
      
      setSessionName('');
      setEditModalVisible(false);
      setEditingSession(null);
      message.success('会话名称更新成功');
    } catch (error) {
      console.error('Failed to update session:', error);
      message.error('更新会话失败');
    }
  };

  const handleDeleteSession = async (sessionIdToDelete: string) => {
    try {
      setSessions(prev => prev.filter(session => session.session_id !== sessionIdToDelete));
      message.success('会话删除成功');
      
      // 如果删除的是当前会话，选择第一个会话
      if (sessionIdToDelete === sessionId && sessions.length > 1) {
        const remainingSessions = sessions.filter(session => session.session_id !== sessionIdToDelete);
        if (remainingSessions.length > 0) {
          const newSessionId = remainingSessions[0].session_id;
          setSessionId(newSessionId);
          if (onSessionSelect) {
            onSessionSelect(newSessionId);
          }
        }
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
      message.error('删除会话失败');
    }
  };

  const formatTime = (timeString: string) => {
    const date = new Date(timeString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (minutes < 1) return '刚刚';
    if (minutes < 60) return `${minutes}分钟前`;
    if (hours < 24) return `${hours}小时前`;
    return `${days}天前`;
  };

  // 拖拽调整宽度处理函数
  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    console.log('拖拽开始', { startX: e.clientX, startWidth: sessionsPanelWidth });
    
    setIsSessionsResizing(true);
    document.body.classList.add('resizing');
    
    const startX = e.clientX;
    const startWidth = sessionsPanelWidth;
    
    const handleMouseMove = (e: MouseEvent) => {
      e.preventDefault();
      const deltaX = e.clientX - startX;
      const newWidth = Math.max(150, Math.min(350, startWidth + deltaX));
      
      console.log('拖拽中', { deltaX, newWidth });
      setSessionsPanelWidth(newWidth);
    };
    
    const handleMouseUp = (e: MouseEvent) => {
      e.preventDefault();
      console.log('拖拽结束');
      
      setIsSessionsResizing(false);
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

  // 如果收缩状态，只显示最小化的侧边栏
  if (isCollapsed) {
    return (
      <div className="copilot-sidebar collapsed">
        <div className="sidebar-header">
          <Button
            type="text"
            icon={<MenuOutlined />}
            onClick={onToggleCollapse}
            className="toggle-btn"
          />
        </div>
        <div className="sidebar-content">
          <div className="copilot-logo">
            <Avatar 
              icon={<RobotOutlined />} 
              style={{ backgroundColor: '#6366f1' }}
              size="large"
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div 
      className={`copilot-sidebar expanded ${isResizing ? 'resizing' : ''}`}
      style={{ width: `${width}px` }}
    >
      {/* 左侧拖拽手柄 */}
      <div 
        className="copilot-resize-handle"
        onMouseDown={onMouseDown}
        onMouseEnter={() => console.log('鼠标进入copilot拖拽手柄')}
        onMouseLeave={() => console.log('鼠标离开copilot拖拽手柄')}
        style={{
          position: 'absolute',
          top: 0,
          left: -5,
          width: 10,
          height: '100%',
          cursor: 'col-resize',
          background: 'rgba(99, 102, 241, 0.1)',
          zIndex: 1000,
          border: 'none',
          outline: 'none',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
        title="拖拽调整copilot宽度"
      >
        <div style={{
          width: 2,
          height: 30,
          background: '#6366f1',
          borderRadius: 1,
          opacity: 0.6
        }} />
      </div>

      {/* 头部导航 */}
      <div className="sidebar-header">
        <div className="header-left">
          <Button
            type="text"
            icon={isSessionsCollapsed ? <DoubleRightOutlined /> : <DoubleLeftOutlined />}
            onClick={() => setIsSessionsCollapsed(!isSessionsCollapsed)}
            size="small"
            className="collapse-btn"
          />
          <Button
            type="text"
            icon={<PlusOutlined />}
            onClick={handleQuickCreateSession}
            loading={createLoading}
            size="small"
            className="new-session-btn"
            title="创建新会话"
          />
        </div>
        <div className="header-right">
          <Button
            type="text"
            icon={<CloseOutlined />}
            onClick={onToggleCollapse}
            size="small"
          />
        </div>
      </div>

      {/* 调试信息 */}
      <div style={{ 
        padding: '4px 16px', 
        fontSize: '12px', 
        color: '#666',
        background: '#f0f0f0',
        borderBottom: '1px solid #e1e5e9'
      }}>
        Copilot宽度: {width}px | 会话面板宽度: {sessionsPanelWidth}px | Copilot拖拽: {isResizing ? '是' : '否'} | 会话拖拽: {isSessionsResizing ? '是' : '否'}
      </div>

      {/* 主要内容区域 */}
      <div className="main-content">
        {/* 左侧会话列表 */}
        <div 
          className={`sessions-panel ${isSessionsCollapsed ? 'collapsed' : ''} ${isSessionsResizing ? 'resizing' : ''}`}
          style={{ width: isSessionsCollapsed ? 0 : `${sessionsPanelWidth}px` }}
        >
          <div className="sessions-header">
            <span className="sessions-title">历史会话</span>
          </div>
          
          <div className="sessions-list">
            {sessionsLoading ? (
              <div className="loading-state">
                <Spin size="small" />
                <Text type="secondary" style={{ fontSize: '12px' }}>加载中...</Text>
              </div>
            ) : sessions.length === 0 ? (
              <div className="empty-sessions">
                <MessageOutlined className="empty-icon" />
                <Text type="secondary" style={{ fontSize: '12px' }}>暂无会话</Text>
              </div>
            ) : (
              sessions.map((session) => (
                <div
                  key={session.session_id}
                  className={`session-item ${session.session_id === sessionId ? 'active' : ''}`}
                  onClick={() => {
                    setSessionId(session.session_id);
                    if (onSessionSelect) {
                      onSessionSelect(session.session_id);
                    }
                  }}
                >
                  <div className="session-content">
                    <div className="session-title">
                      <Text 
                        strong={session.session_id === sessionId}
                        style={{ fontSize: '13px' }}
                        ellipsis={{ tooltip: session.session_name || '未命名会话' }}
                      >
                        {session.session_name || '未命名会话'}
                      </Text>
                      {session.session_id === sessionId && (
                        <Tag color="blue">当前</Tag>
                      )}
                    </div>
                    <div className="session-time">
                      <ClockCircleOutlined style={{ fontSize: '10px', marginRight: '2px' }} />
                      <Text type="secondary" style={{ fontSize: '10px' }}>
                        {formatTime(session.last_activity)}
                      </Text>
                    </div>
                  </div>
                  {!isSessionsCollapsed && (
                    <div className="session-actions">
                      <Button
                        type="text"
                        icon={<EditOutlined />}
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          setEditingSession(session);
                          setSessionName(session.session_name || '');
                          setEditModalVisible(true);
                        }}
                      />
                      <Popconfirm
                        title="确定要删除这个会话吗？"
                        description="删除后无法恢复，包括所有对话历史。"
                        onConfirm={(e) => {
                          e?.stopPropagation();
                          handleDeleteSession(session.session_id);
                        }}
                        okText="确定"
                        cancelText="取消"
                      >
                        <Button
                          type="text"
                          icon={<DeleteOutlined />}
                          size="small"
                          danger
                          onClick={(e) => e.stopPropagation()}
                        />
                      </Popconfirm>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
          
          {/* 拖拽手柄 */}
          {!isSessionsCollapsed && (
            <div 
              className="resize-handle"
              onMouseDown={handleMouseDown}
              onMouseEnter={() => console.log('鼠标进入拖拽手柄')}
              onMouseLeave={() => console.log('鼠标离开拖拽手柄')}
              style={{
                position: 'absolute',
                top: 0,
                right: -5,
                width: 10,
                height: '100%',
                cursor: 'col-resize',
                background: 'rgba(99, 102, 241, 0.1)',
                zIndex: 1000,
                border: 'none',
                outline: 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
              title="拖拽调整宽度"
            >
              <div style={{
                width: 2,
                height: 30,
                background: '#6366f1',
                borderRadius: 1,
                opacity: 0.6
              }} />
            </div>
          )}
        </div>

        {/* 右侧对话区域 */}
        <div className="chat-panel">
          {/* 对话历史区域 */}
          <div className="messages-container">
            {!initialized ? (
              <div className="loading-state">
                <Spin size="small" />
                <Text type="secondary" style={{ fontSize: '12px', marginLeft: 8 }}>加载中...</Text>
              </div>
            ) : messages.length === 0 ? (
              <div className="empty-state">
                <div className="welcome-message">
                  <Avatar 
                    icon={<RobotOutlined />} 
                    style={{ backgroundColor: '#6366f1' }}
                    size="large"
                  />
                  <div className="welcome-text">
                    <Text strong style={{ fontSize: '16px', color: '#1f2937' }}>你好!</Text>
                    <Text type="secondary" style={{ fontSize: '14px' }}>
                      有什么我可以帮助你的吗?
                    </Text>
                  </div>
                </div>
                <div className="suggestions">
                  <Text type="secondary" style={{ fontSize: '12px', marginBottom: 8 }}>
                    试试说:"添加任务:学习新技能"或"查看我的任务"
                  </Text>
                </div>
              </div>
            ) : (
              <div className="messages-list">
                {messages.map((message) => (
                  <div key={message.id} className={`message-item ${message.role}`}>
                    {message.role === 'assistant' && (
                      <div className="message-avatar">
                        <Avatar 
                          icon={<RobotOutlined />}
                          style={{ 
                            backgroundColor: '#6366f1',
                            fontSize: '12px'
                          }}
                          size="small"
                        />
                      </div>
                    )}
                    <div className="message-content">
                      <div className={`message-bubble ${message.role}`}>
                        <div className="message-text">
                          {message.content.split('\n').map((line, index) => (
                            <div key={index}>{line}</div>
                          ))}
                        </div>
                      </div>
                      <div className="message-time">
                        <Text type="secondary" style={{ fontSize: '10px' }}>
                          {new Date().toLocaleTimeString('zh-CN', { 
                            hour: '2-digit', 
                            minute: '2-digit', 
                            second: '2-digit',
                            hour12: false 
                          })}
                        </Text>
                      </div>
                    </div>
                    {message.role === 'user' && (
                      <div className="message-avatar">
                        <Avatar 
                          icon={<UserOutlined />}
                          style={{ 
                            backgroundColor: '#1890ff',
                            fontSize: '12px'
                          }}
                          size="small"
                        />
                      </div>
                    )}
                  </div>
                ))}
                {loading && (
                  <div className="message-item assistant">
                    <div className="message-avatar">
                      <Avatar 
                        icon={<RobotOutlined />}
                        style={{ backgroundColor: '#6366f1' }}
                        size="small"
                      />
                    </div>
                    <div className="message-content">
                      <div className="message-bubble assistant">
                        <div className="typing-indicator">
                          <Spin size="small" />
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            AI 正在思考
                          </Text>
                          <div className="thinking-dots">
                            <span></span>
                            <span></span>
                            <span></span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* 用户输入区域 */}
          <div className="input-area">
            <div className="input-tools">
              <Button
                type="text"
                icon={<ClearOutlined />}
                size="small"
                onClick={handleClearChat}
                title="清空对话"
              />
              <Button
                type="text"
                icon={<PictureOutlined />}
                size="small"
                title="上传图片"
                disabled
              />
              <Button
                type="text"
                icon={<AudioOutlined />}
                size="small"
                title="语音输入"
                disabled
              />
            </div>
            
            <div className="input-container">
              <TextArea
                value={currentMessage}
                onChange={handleInputChange}
                onKeyPress={handleKeyPress}
                placeholder="Write a message..."
                autoSize={{ minRows: 1, maxRows: 4 }}
                className="message-input"
                disabled={loading}
              />
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={handleSendMessage}
                loading={loading}
                disabled={!currentMessage.trim()}
                className="send-button"
              >
                发送
              </Button>
            </div>
            
            <div className="input-suggestions">
              <Text type="secondary" style={{ fontSize: '12px' }}>
                试试说:"添加任务:学习新技能"或"查看我的任务"
              </Text>
            </div>
          </div>
        </div>
      </div>

      {/* 编辑会话模态框 */}
      <Modal
        title="编辑会话名称"
        open={editModalVisible}
        onCancel={() => {
          setEditModalVisible(false);
          setEditingSession(null);
          setSessionName('');
        }}
        footer={[
          <Button key="cancel" onClick={() => setEditModalVisible(false)}>
            取消
          </Button>,
          <Button 
            key="save" 
            type="primary" 
            onClick={handleEditSession}
          >
            保存
          </Button>,
        ]}
      >
        <Input
          placeholder="请输入会话名称"
          value={sessionName}
          onChange={(e) => setSessionName(e.target.value)}
          onPressEnter={handleEditSession}
        />
      </Modal>
    </div>
  );
};

export default CopilotSidebar;
