import React from 'react';
import { Menu } from 'antd';
import {
  CheckCircleOutlined,
  CalendarOutlined,
  FileTextOutlined,
  SettingOutlined,
  BarChartOutlined,
} from '@ant-design/icons';

export interface MenuItem {
  key: string;
  label: string;
  icon: React.ReactNode;
  disabled?: boolean;
}

interface SideMenuProps {
  selectedKey: string;
  onMenuSelect: (key: string) => void;
}

const SideMenu: React.FC<SideMenuProps> = ({ selectedKey, onMenuSelect }) => {
  const menuItems: MenuItem[] = [
    {
      key: 'tasks',
      label: '任务管理',
      icon: <CheckCircleOutlined />,
    },
    {
      key: 'calendar',
      label: '日程安排',
      icon: <CalendarOutlined />,
      disabled: true, // 暂时禁用，将来可以启用
    },
    {
      key: 'notes',
      label: '笔记管理',
      icon: <FileTextOutlined />,
      disabled: true, // 暂时禁用，将来可以启用
    },
    {
      key: 'analytics',
      label: '数据分析',
      icon: <BarChartOutlined />,
      disabled: true, // 暂时禁用，将来可以启用
    },
    {
      key: 'settings',
      label: '系统设置',
      icon: <SettingOutlined />,
      disabled: true, // 暂时禁用，将来可以启用
    },
  ];

  return (
    <Menu
      mode="inline"
      selectedKeys={[selectedKey]}
      style={{
        height: '100%',
        borderRight: 0,
        background: '#fff',
      }}
      items={menuItems.map(item => ({
        key: item.key,
        icon: item.icon,
        label: item.label,
        disabled: item.disabled,
      }))}
      onClick={({ key }) => onMenuSelect(key)}
    />
  );
};

export default SideMenu;
