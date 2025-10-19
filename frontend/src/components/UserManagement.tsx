import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Space,
  Tag,
  Popconfirm,
  message,
  Typography,
  Row,
  Col,
  Statistic,
  Avatar,
  Tooltip,
  Badge,
  Divider
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  UserOutlined,
  TeamOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  SearchOutlined,
  ReloadOutlined,
  SettingOutlined
} from '@ant-design/icons';
import { User } from '../services/authApi';

const { Title, Text } = Typography;

const API_BASE_URL = '/api';
const { Option } = Select;

interface UserManagementProps {
  currentUser: User;
}

interface UserFormData {
  username: string;
  email: string;
  display_name: string;
  password?: string;
  is_active: boolean;
  role: string;
}

const UserManagement: React.FC<UserManagementProps> = ({ currentUser }) => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [form] = Form.useForm();
  const [searchText, setSearchText] = useState('');

  // API基础URL - 使用绝对路径指向后端
  // const API_BASE_URL = '/api'; // 已在上方定义

  // 检查用户权限 - 临时解决方案
  const isAdmin = currentUser.role === 'admin' || currentUser.username === 'qingsong' || currentUser.username === 'admin';

  useEffect(() => {
    if (isAdmin) {
      loadUsers();
    }
  }, [isAdmin]);

  // 如果不是管理员，显示权限不足提示
  if (!isAdmin) {
    return (
      <div style={{ 
        textAlign: 'center', 
        padding: '50px 20px',
        color: '#999'
      }}>
        <Title level={2} style={{ color: '#ff4d4f' }}>
          权限不足
        </Title>
        <div style={{ fontSize: '16px', marginBottom: '16px' }}>
          您没有权限访问用户管理功能
        </div>
        <div style={{ fontSize: '14px' }}>
          只有管理员用户可以管理系统用户
        </div>
      </div>
    );
  }

  const getAuthHeaders = () => {
    const token = localStorage.getItem('auth_token');
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  };

  const loadUsers = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/admin/users`, {
        headers: getAuthHeaders()
      });
      
      if (!response.ok) {
        throw new Error('获取用户列表失败');
      }
      
      const data = await response.json();
      setUsers(data.users || []);
    } catch (error) {
      console.error('加载用户失败:', error);
      message.error('加载用户列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAddUser = () => {
    setEditingUser(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEditUser = (user: User) => {
    setEditingUser(user);
    form.setFieldsValue({
      username: user.username,
      email: user.email,
      display_name: user.display_name,
      is_active: user.is_active,
      role: user.role || 'user'
    });
    setModalVisible(true);
  };

  const handleDeleteUser = async (userId: number) => {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/users/${userId}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });
      
      if (!response.ok) {
        throw new Error('删除用户失败');
      }
      
      setUsers(users.filter(user => user.id !== userId));
      message.success('用户删除成功');
    } catch (error) {
      console.error('删除用户失败:', error);
      message.error('删除用户失败');
    }
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingUser) {
        // 更新用户
        const response = await fetch(`${API_BASE_URL}/admin/users/${editingUser.id}`, {
          method: 'PUT',
          headers: getAuthHeaders(),
          body: JSON.stringify(values)
        });
        
        if (!response.ok) {
          throw new Error('更新用户失败');
        }
        
        const updatedUser = await response.json();
        const updatedUsers = users.map(user => 
          user.id === editingUser.id ? updatedUser : user
        );
        setUsers(updatedUsers);
        message.success('用户更新成功');
      } else {
        // 添加用户
        const response = await fetch(`${API_BASE_URL}/admin/users`, {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify(values)
        });
        
        if (!response.ok) {
          throw new Error('添加用户失败');
        }
        
        const newUser = await response.json();
        setUsers([...users, newUser]);
        message.success('用户添加成功');
      }
      
      setModalVisible(false);
      form.resetFields();
    } catch (error) {
      console.error('操作失败:', error);
      message.error('操作失败');
    }
  };

  const handleModalCancel = () => {
    setModalVisible(false);
    form.resetFields();
  };

  const filteredUsers = users.filter(user =>
    user.username.toLowerCase().includes(searchText.toLowerCase()) ||
    user.email.toLowerCase().includes(searchText.toLowerCase()) ||
    (user.display_name && user.display_name.toLowerCase().includes(searchText.toLowerCase()))
  );

  const activeUsersCount = users.filter(user => user.is_active).length;
  const inactiveUsersCount = users.filter(user => !user.is_active).length;

  const columns = [
    {
      title: '用户信息',
      key: 'user_info',
      render: (record: User) => (
        <Space>
          <Avatar icon={<UserOutlined />} />
          <div>
            <div style={{ fontWeight: 'bold' }}>{record.display_name}</div>
            <div style={{ fontSize: '12px', color: '#666' }}>@{record.username}</div>
          </div>
        </Space>
      ),
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      render: (role: string) => (
        <Tag color={role === 'admin' ? 'red' : 'blue'}>
          {role === 'admin' ? '管理员' : '用户'}
        </Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'red'} icon={isActive ? <CheckCircleOutlined /> : <CloseCircleOutlined />}>
          {isActive ? '活跃' : '禁用'}
        </Tag>
      ),
    },
    {
      title: '最后登录',
      dataIndex: 'last_login',
      key: 'last_login',
      render: (lastLogin: Date | null) => (
        lastLogin ? new Date(lastLogin).toLocaleString() : '从未登录'
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (createdAt: Date) => new Date(createdAt).toLocaleDateString(),
    },
    {
      title: '操作',
      key: 'actions',
      render: (record: User) => (
        <Space>
          <Tooltip title="编辑用户">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => handleEditUser(record)}
              disabled={record.id === currentUser.id}
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这个用户吗？"
            description="删除后无法恢复"
            onConfirm={() => handleDeleteUser(record.id)}
            okText="确定"
            cancelText="取消"
            disabled={record.id === currentUser.id}
          >
            <Tooltip title="删除用户">
              <Button
                type="text"
                danger
                icon={<DeleteOutlined />}
                disabled={record.id === currentUser.id}
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      {/* 页面标题和统计 */}
      <div style={{ marginBottom: '24px' }}>
        <Title level={2} style={{ marginBottom: '16px' }}>
          <SettingOutlined style={{ marginRight: '8px' }} />
          用户管理
        </Title>
        
        <Row gutter={16}>
          <Col span={6}>
            <Card>
              <Statistic
                title="总用户数"
                value={users.length}
                prefix={<TeamOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="活跃用户"
                value={activeUsersCount}
                prefix={<CheckCircleOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="禁用用户"
                value={inactiveUsersCount}
                prefix={<CloseCircleOutlined />}
                valueStyle={{ color: '#ff4d4f' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="在线用户"
                value={activeUsersCount}
                prefix={<Badge status="success" />}
                valueStyle={{ color: '#722ed1' }}
              />
            </Card>
          </Col>
        </Row>
      </div>

      {/* 操作栏 */}
      <Card style={{ marginBottom: '16px' }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space>
              <Input
                placeholder="搜索用户..."
                prefix={<SearchOutlined />}
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                style={{ width: 300 }}
              />
            </Space>
          </Col>
          <Col>
            <Space>
              <Button
                icon={<ReloadOutlined />}
                onClick={loadUsers}
                loading={loading}
              >
                刷新
              </Button>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={handleAddUser}
              >
                添加用户
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 用户列表 */}
      <Card>
        <Table
          columns={columns}
          dataSource={filteredUsers}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
          }}
        />
      </Card>

      {/* 添加/编辑用户模态框 */}
      <Modal
        title={editingUser ? '编辑用户' : '添加用户'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
        width={600}
        okText="确定"
        cancelText="取消"
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{ is_active: true, role: 'user' }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="username"
                label="用户名"
                rules={[
                  { required: true, message: '请输入用户名' },
                  { min: 3, message: '用户名至少3个字符' },
                  { max: 20, message: '用户名最多20个字符' }
                ]}
              >
                <Input placeholder="请输入用户名" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="email"
                label="邮箱"
                rules={[
                  { required: true, message: '请输入邮箱' },
                  { type: 'email', message: '请输入有效的邮箱地址' }
                ]}
              >
                <Input placeholder="请输入邮箱" />
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item
            name="display_name"
            label="显示名称"
            rules={[
              { required: true, message: '请输入显示名称' },
              { max: 50, message: '显示名称最多50个字符' }
            ]}
          >
            <Input placeholder="请输入显示名称" />
          </Form.Item>

          {!editingUser && (
            <Form.Item
              name="password"
              label="密码"
              rules={[
                { required: true, message: '请输入密码' },
                { min: 6, message: '密码至少6个字符' }
              ]}
            >
              <Input.Password placeholder="请输入密码" />
            </Form.Item>
          )}

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="role"
                label="用户角色"
                rules={[{ required: true, message: '请选择用户角色' }]}
              >
                <Select placeholder="请选择用户角色">
                  <Option value="user">普通用户</Option>
                  <Option value="admin">管理员</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="is_active"
                label="用户状态"
                rules={[{ required: true, message: '请选择用户状态' }]}
              >
                <Select placeholder="请选择用户状态">
                  <Option value={true}>活跃</Option>
                  <Option value={false}>禁用</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
};

export default UserManagement;
