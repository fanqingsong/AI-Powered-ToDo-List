import React, { useState, useEffect } from 'react';
import {
  Card,
  List,
  Button,
  Space,
  Typography,
  Modal,
  Input,
  message,
  Popconfirm,
  Tag,
  Empty,
  Spin,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  MessageOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { User } from '../services/authApi';
import { conversationApi } from '../services/api';

const { Title, Text } = Typography;

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

interface SessionManagerProps {
  user: User;
  onSessionSelect: (sessionId: string) => void;
  currentSessionId?: string;
}

const SessionManager: React.FC<SessionManagerProps> = ({ 
  user, 
  onSessionSelect, 
  currentSessionId 
}) => {
  const [sessions, setSessions] = useState<UserSession[]>([]);
  const [loading, setLoading] = useState(false);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [editingSession, setEditingSession] = useState<UserSession | null>(null);
  const [sessionName, setSessionName] = useState('');
  const [createLoading, setCreateLoading] = useState(false);

  // 加载用户会话列表
  const loadSessions = async () => {
    setLoading(true);
    try {
      const sessions = await conversationApi.getUserSessions(user.id.toString());
      setSessions(sessions);
      
      // 如果没有当前选中的会话，自动选择第一个会话
      if (!currentSessionId && sessions.length > 0) {
        onSessionSelect(sessions[0].session_id);
      }
    } catch (error) {
      console.error('Failed to load sessions:', error);
      message.error('加载会话列表失败');
      setSessions([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSessions();
  }, [user.id]);

  // 创建新会话
  const handleCreateSession = async () => {
    if (!sessionName.trim()) {
      message.warning('请输入会话名称');
      return;
    }

    setCreateLoading(true);
    try {
      // 调用API创建新会话
      const newSession = await conversationApi.createSession(user.id, sessionName);
      
      setSessions(prev => [newSession, ...prev]);
      setSessionName('');
      setCreateModalVisible(false);
      message.success('会话创建成功');
      
      // 自动选择新创建的会话
      onSessionSelect(newSession.session_id);
    } catch (error) {
      console.error('Failed to create session:', error);
      message.error('创建会话失败');
    } finally {
      setCreateLoading(false);
    }
  };

  // 编辑会话名称
  const handleEditSession = async () => {
    if (!editingSession || !sessionName.trim()) {
      message.warning('请输入会话名称');
      return;
    }

    try {
      // 这里应该调用API更新会话名称
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

  // 删除会话
  const handleDeleteSession = async (sessionId: string) => {
    try {
      // 这里应该调用API删除会话
      setSessions(prev => prev.filter(session => session.session_id !== sessionId));
      message.success('会话删除成功');
      
      // 如果删除的是当前会话，选择第一个会话
      if (sessionId === currentSessionId && sessions.length > 1) {
        const remainingSessions = sessions.filter(session => session.session_id !== sessionId);
        if (remainingSessions.length > 0) {
          onSessionSelect(remainingSessions[0].session_id);
        }
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
      message.error('删除会话失败');
    }
  };

  // 格式化时间
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

  return (
    <Card 
      title={
        <Space>
          <MessageOutlined />
          <span>会话管理</span>
        </Space>
      }
      extra={
        <Button 
          type="primary" 
          icon={<PlusOutlined />} 
          size="small"
          onClick={() => setCreateModalVisible(true)}
        >
          新建会话
        </Button>
      }
      style={{ height: '100%' }}
    >
      {loading ? (
        <div style={{ textAlign: 'center', padding: '50px 0' }}>
          <Spin />
          <div style={{ marginTop: 16 }}>
            <Text type="secondary">加载中...</Text>
          </div>
        </div>
      ) : sessions.length === 0 ? (
        <Empty 
          description="暂无会话"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        >
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={() => setCreateModalVisible(true)}
          >
            创建第一个会话
          </Button>
        </Empty>
      ) : (
        <List
          dataSource={sessions}
          renderItem={(session) => (
            <List.Item
              key={session.session_id}
              style={{
                padding: '12px 0',
                cursor: 'pointer',
                backgroundColor: session.session_id === currentSessionId ? '#e6f7ff' : 'transparent',
                borderRadius: '6px',
                marginBottom: '8px',
              }}
              onClick={() => onSessionSelect(session.session_id)}
              actions={[
                <Button
                  key="edit"
                  type="text"
                  icon={<EditOutlined />}
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    setEditingSession(session);
                    setSessionName(session.session_name || '');
                    setEditModalVisible(true);
                  }}
                />,
                <Popconfirm
                  key="delete"
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
                </Popconfirm>,
              ]}
            >
              <List.Item.Meta
                title={
                  <Space>
                    <Text strong={session.session_id === currentSessionId}>
                      {session.session_name || '未命名会话'}
                    </Text>
                    {session.session_id === currentSessionId && (
                      <Tag color="blue" size="small">当前</Tag>
                    )}
                  </Space>
                }
                description={
                  <Space>
                    <ClockCircleOutlined style={{ fontSize: '12px' }} />
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      {formatTime(session.last_activity)}
                    </Text>
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      )}

      {/* 创建会话模态框 */}
      <Modal
        title="创建新会话"
        open={createModalVisible}
        onCancel={() => {
          setCreateModalVisible(false);
          setSessionName('');
        }}
        footer={[
          <Button key="cancel" onClick={() => setCreateModalVisible(false)}>
            取消
          </Button>,
          <Button 
            key="create" 
            type="primary" 
            loading={createLoading}
            onClick={handleCreateSession}
          >
            创建
          </Button>,
        ]}
      >
        <Input
          placeholder="请输入会话名称"
          value={sessionName}
          onChange={(e) => setSessionName(e.target.value)}
          onPressEnter={handleCreateSession}
        />
      </Modal>

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
    </Card>
  );
};

export default SessionManager;
