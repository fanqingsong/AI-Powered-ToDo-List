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
  LoginOutlined,
} from '@ant-design/icons';
import { AuthService, UserLogin } from '../services/authApi';

const { Title, Text, Link } = Typography;

interface LoginFormProps {
  onLoginSuccess: (user: any) => void;
  onSwitchToRegister: () => void;
}

const LoginForm: React.FC<LoginFormProps> = ({ onLoginSuccess, onSwitchToRegister }) => {
  const [loading, setLoading] = useState(false);
  const authService = AuthService.getInstance();

  const handleLogin = async (values: UserLogin) => {
    setLoading(true);
    try {
      const user = await authService.login(values);
      message.success('登录成功！');
      onLoginSuccess(user);
    } catch (error: any) {
      console.error('Login error:', error);
      if (error.response?.status === 401) {
        message.error('用户名或密码错误');
      } else {
        message.error('登录失败，请稍后重试');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card style={{ width: 400, margin: '0 auto' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div style={{ textAlign: 'center' }}>
          <LoginOutlined style={{ fontSize: '48px', color: '#1890ff', marginBottom: '16px' }} />
          <Title level={2} style={{ margin: 0 }}>
            登录
          </Title>
          <Text type="secondary">
            欢迎回到 AI Native 智能工作台
          </Text>
        </div>

        <Form
          name="login"
          onFinish={handleLogin}
          autoComplete="off"
          size="large"
        >
          <Form.Item
            name="username"
            rules={[
              { required: true, message: '请输入用户名' },
              { min: 3, message: '用户名至少3个字符' },
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="用户名"
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

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              size="large"
            >
              登录
            </Button>
          </Form.Item>
        </Form>

        <Divider>
          <Text type="secondary">或</Text>
        </Divider>

        <div style={{ textAlign: 'center' }}>
          <Text type="secondary">
            还没有账户？{' '}
            <Link onClick={onSwitchToRegister}>
              立即注册
            </Link>
          </Text>
        </div>
      </Space>
    </Card>
  );
};

export default LoginForm;
