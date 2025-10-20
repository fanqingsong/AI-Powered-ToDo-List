import React, { useState, useEffect, useCallback } from 'react';
import {
  Input,
  Button,
  List,
  Checkbox,
  Typography,
  Space,
  message,
  Popconfirm,
  Empty,
  Spin,
  Divider,
} from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { taskApi, Task } from '../services/api';

const { Title, Text } = Typography;

interface TaskManagerProps {
  refreshTrigger?: number;
}

const TaskManager: React.FC<TaskManagerProps> = ({ refreshTrigger }) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [newTaskTitle, setNewTaskTitle] = useState('');

  // 加载任务列表
  const loadTasks = useCallback(async () => {
    try {
      setLoading(true);
      const tasksData = await taskApi.getAllTasks();
      setTasks(tasksData);
    } catch (error) {
      message.error('加载任务失败');
      console.error('Error loading tasks:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  useEffect(() => {
    if (refreshTrigger && refreshTrigger > 0) {
      loadTasks();
    }
  }, [refreshTrigger, loadTasks]);

  // 监听前端工具调用事件
  useEffect(() => {
    const handleRefreshTaskList = (event: CustomEvent) => {
      console.log('📡 收到刷新任务列表事件:', event.detail);
      loadTasks();
    };

    window.addEventListener('refreshTaskList', handleRefreshTaskList as EventListener);
    
    return () => {
      window.removeEventListener('refreshTaskList', handleRefreshTaskList as EventListener);
    };
  }, [loadTasks]);

  // 创建新任务
  const handleCreateTask = async () => {
    if (!newTaskTitle.trim()) {
      message.warning('请输入任务标题');
      return;
    }

    try {
      const newTask = await taskApi.createTask(newTaskTitle.trim());
      setTasks([...tasks, newTask]);
      setNewTaskTitle('');
      message.success('任务创建成功');
    } catch (error) {
      message.error('创建任务失败');
      console.error('Error creating task:', error);
    }
  };

  // 更新任务状态
  const handleToggleTask = async (task: Task) => {
    try {
      await taskApi.updateTask(task.id, task.title, !task.isComplete);
      setTasks(tasks.map(t => 
        t.id === task.id ? { ...t, isComplete: !t.isComplete } : t
      ));
      message.success('任务状态已更新');
    } catch (error) {
      message.error('更新任务失败');
      console.error('Error toggling task:', error);
    }
  };

  // 删除任务
  const handleDeleteTask = async (id: number) => {
    try {
      await taskApi.deleteTask(id);
      setTasks(tasks.filter(task => task.id !== id));
      message.success('任务删除成功');
    } catch (error) {
      message.error('删除任务失败');
      console.error('Error deleting task:', error);
    }
  };

  const completedTasks = tasks.filter(task => task.isComplete).length;
  const totalTasks = tasks.length;

  return (
    <div style={{ height: '100%' }}>
      {/* 标题和统计信息 */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '24px',
        paddingBottom: '16px',
        borderBottom: '1px solid #f0f0f0'
      }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <CheckCircleOutlined style={{ color: '#1890ff', fontSize: '20px', marginRight: '8px' }} />
          <Title level={3} style={{ margin: 0 }}>
            任务管理
          </Title>
        </div>
        <Text type="secondary">
          已完成: {completedTasks}/{totalTasks}
        </Text>
      </div>
      {/* 添加任务 */}
      <Space.Compact style={{ width: '100%', marginBottom: 16 }}>
        <Input
          placeholder="输入新任务..."
          value={newTaskTitle}
          onChange={(e) => setNewTaskTitle(e.target.value)}
          onPressEnter={handleCreateTask}
          style={{ flex: 1 }}
        />
        <Button 
          type="primary" 
          icon={<PlusOutlined />}
          onClick={handleCreateTask}
          loading={loading}
        >
          添加
        </Button>
      </Space.Compact>

      <Divider />

      {/* 任务列表 */}
      <div style={{ maxHeight: 'calc(100vh - 400px)', overflowY: 'auto' }}>
        <Spin spinning={loading}>
          {tasks.length === 0 ? (
            <Empty 
              description="暂无任务" 
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            />
          ) : (
            <List
              dataSource={tasks}
              renderItem={(task) => (
                <List.Item
                  key={task.id}
                  style={{
                    padding: '12px 0',
                    borderBottom: '1px solid #f0f0f0',
                  }}
                  actions={[
                    <Popconfirm
                      key="delete"
                      title="确定要删除这个任务吗？"
                      onConfirm={() => handleDeleteTask(task.id)}
                      okText="确定"
                      cancelText="取消"
                    >
                      <Button
                        size="small"
                        danger
                        icon={<DeleteOutlined />}
                      >
                        删除
                      </Button>
                    </Popconfirm>
                  ]}
                >
                  <List.Item.Meta
                    avatar={
                      <Checkbox
                        checked={task.isComplete}
                        onChange={() => handleToggleTask(task)}
                      />
                    }
                    title={
                      <Space>
                        {task.isComplete ? (
                          <CheckCircleOutlined style={{ color: '#52c41a' }} />
                        ) : (
                          <ClockCircleOutlined style={{ color: '#faad14' }} />
                        )}
                        <span
                          style={{
                            textDecoration: task.isComplete ? 'line-through' : 'none',
                            color: task.isComplete ? '#999' : '#000',
                            fontSize: '14px',
                          }}
                        >
                          {task.title}
                        </span>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          )}
        </Spin>
      </div>
    </div>
  );
};

export default TaskManager;
