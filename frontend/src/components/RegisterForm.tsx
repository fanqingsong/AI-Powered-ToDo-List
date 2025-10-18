import React, { useState } from 'react';
import {
  Form,
  Input,
  Button,
  Card,
  Typography,
  Space,
  message,
  Divider,
} from 'antd';
import {
  UserOutlined,
  LockOutlined,
  MailOutlined,
  UserAddOutlined,
} from '@ant-design/icons';
import { AuthService, UserCreate } from '../services/authApi';

const { Title, Text, Link } = Typography;

interface RegisterFormProps {
  onRegisterSuccess: (user: any) => void;
  onSwitchToLogin: () => void;
}

const RegisterForm: React.FC<RegisterFormProps> = ({ onRegisterSuccess, onSwitchToLogin }) => {
  const [loading, setLoading] = useState(false);
  const authService = AuthService.getInstance();

  const handleRegister = async (values: UserCreate & { confirmPassword: string }) => {
    if (values.password !== values.confirmPassword) {
      message.error('两次输入的密码不一致');
      return;
    }

    setLoading(true);
    try {
      const { confirmPassword, ...userData } = values;
      const user = await authService.register(userData);
      message.success('注册成功！');
      onRegisterSuccess(user);
    } catch (error: any) {
      console.error('Register error:', error);
      if (error.response?.status === 400) {
        const errorMsg = error.response.data?.detail || '注册失败';
        message.error(errorMsg);
      } else {
        message.error('注册失败，请稍后重试');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card style={{ width: 400, margin: '0 auto' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div style={{ textAlign: 'center' }}>
          <UserAddOutlined style={{ fontSize: '48px', color: '#52c41a', marginBottom: '16px' }} />
          <Title level={2} style={{ margin: 0 }}>
            注册
          </Title>
          <Text type="secondary">
            创建您的 AI Native 智能工作台账户
          </Text>
        </div>

        <Form
          name="register"
          onFinish={handleRegister}
          autoComplete="off"
          size="large"
        >
          <Form.Item
            name="username"
            rules={[
              { required: true, message: '请输入用户名' },
              { min: 3, message: '用户名至少3个字符' },
              { max: 50, message: '用户名最多50个字符' },
              { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线' },
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="用户名"
            />
          </Form.Item>

          <Form.Item
            name="email"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' },
            ]}
          >
            <Input
              prefix={<MailOutlined />}
              placeholder="邮箱"
            />
          </Form.Item>

          <Form.Item
            name="display_name"
            rules={[
              { max: 100, message: '显示名称最多100个字符' },
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="显示名称（可选）"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: '请输入密码' },
              { min: 6, message: '密码至少6个字符' },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
            />
          </Form.Item>

          <Form.Item
            name="confirmPassword"
            rules={[
              { required: true, message: '请确认密码' },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="确认密码"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              size="large"
            >
              注册
            </Button>
          </Form.Item>
        </Form>

        <Divider>
          <Text type="secondary">或</Text>
        </Divider>

        <div style={{ textAlign: 'center' }}>
          <Text type="secondary">
            已有账户？{' '}
            <Link onClick={onSwitchToLogin}>
              立即登录
            </Link>
          </Text>
        </div>
      </Space>
    </Card>
  );
};

export default RegisterForm;
