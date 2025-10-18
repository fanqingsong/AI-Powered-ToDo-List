import React, { useState } from 'react';
import {
  Dropdown,
  Button,
  Space,
  Typography,
  Avatar,
  Menu,
  Modal,
  Form,
  Input,
  message,
} from 'antd';
import {
  UserOutlined,
  LogoutOutlined,
  SettingOutlined,
  EditOutlined,
} from '@ant-design/icons';
import { AuthService, User } from '../services/authApi';

const { Text } = Typography;

interface UserInfoProps {
  user: User;
  onLogout: () => void;
  onUserUpdate: (user: User) => void;
}

const UserInfo: React.FC<UserInfoProps> = ({ user, onLogout, onUserUpdate }) => {
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [editLoading, setEditLoading] = useState(false);
  const [form] = Form.useForm();
  const authService = AuthService.getInstance();

  const handleEditProfile = () => {
    form.setFieldsValue({
      display_name: user.display_name || '',
      email: user.email,
    });
    setEditModalVisible(true);
  };

  const handleUpdateProfile = async (values: any) => {
    setEditLoading(true);
    try {
      const token = authService.getToken();
      if (!token) {
        message.error('未找到认证令牌');
        return;
      }

      const updatedUser = await authService.updateUser(token, values);
      onUserUpdate(updatedUser);
      setEditModalVisible(false);
      message.success('个人信息更新成功');
    } catch (error: any) {
      console.error('Update profile error:', error);
      message.error('更新失败，请稍后重试');
    } finally {
      setEditLoading(false);
    }
  };

  const menu = (
    <Menu>
      <Menu.Item key="profile" icon={<UserOutlined />} onClick={handleEditProfile}>
        编辑资料
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item key="logout" icon={<LogoutOutlined />} onClick={onLogout}>
        退出登录
      </Menu.Item>
    </Menu>
  );

  return (
    <>
      <Dropdown overlay={menu} placement="bottomRight" arrow>
        <Button type="text" style={{ color: '#fff' }}>
          <Space>
            <Avatar 
              size="small" 
              icon={<UserOutlined />} 
              style={{ backgroundColor: '#1890ff' }}
            />
            <Text style={{ color: '#fff' }}>
              {user.display_name || user.username}
            </Text>
          </Space>
        </Button>
      </Dropdown>

      <Modal
        title="编辑资料"
        open={editModalVisible}
        onCancel={() => setEditModalVisible(false)}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleUpdateProfile}
        >
          <Form.Item
            name="display_name"
            label="显示名称"
            rules={[
              { max: 100, message: '显示名称最多100个字符' },
            ]}
          >
            <Input placeholder="请输入显示名称" />
          </Form.Item>

          <Form.Item
            name="email"
            label="邮箱"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' },
            ]}
          >
            <Input placeholder="请输入邮箱" />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setEditModalVisible(false)}>
                取消
              </Button>
              <Button type="primary" htmlType="submit" loading={editLoading}>
                保存
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};

export default UserInfo;
