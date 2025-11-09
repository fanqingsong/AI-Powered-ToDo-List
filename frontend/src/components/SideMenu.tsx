import React from 'react';
import { Menu } from 'antd';
import {
  CheckCircleOutlined,
  CalendarOutlined,
  FileTextOutlined,
  SettingOutlined,
  BarChartOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
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
  collapsed?: boolean;
  onToggleCollapse?: () => void;
}

const SideMenu: React.FC<SideMenuProps> = ({ selectedKey, onMenuSelect, collapsed = false, onToggleCollapse }) => {
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
      disabled: false, // 启用日程安排功能
    },
    {
      key: 'notes',
      label: '笔记管理',
      icon: <FileTextOutlined />,
      disabled: false, // 启用笔记管理功能
    },
    {
      key: 'analytics',
      label: '数据分析',
      icon: <BarChartOutlined />,
      disabled: false, // 启用数据分析功能
    },
    {
      key: 'settings',
      label: '系统设置',
      icon: <SettingOutlined />,
      disabled: false, // 启用系统设置功能
    },
  ];

  return (
    <div style={{ 
      padding: collapsed ? '40px 12px 24px 12px' : '40px 24px 24px 24px',
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
    }}>
      {/* Logo区域 */}
      <div style={{
        marginBottom: '40px',
        textAlign: 'center',
        position: 'relative'
      }}>
        {!collapsed ? (
          <>
            <div style={{
              fontSize: '24px',
              fontWeight: 'bold',
              color: '#fff',
              marginBottom: '8px',
              textShadow: '0 2px 4px rgba(0,0,0,0.3)'
            }}>
              ⚡ AI Native
            </div>
            <div style={{
              fontSize: '14px',
              color: 'rgba(255,255,255,0.8)',
              fontWeight: '500'
            }}>
              智能工作台
            </div>
          </>
        ) : (
          <div style={{
            fontSize: '28px',
            fontWeight: 'bold',
            color: '#fff',
            textShadow: '0 2px 4px rgba(0,0,0,0.3)'
          }}>
            ⚡
          </div>
        )}
        {/* 切换按钮 */}
        {onToggleCollapse && (
          <div
            onClick={onToggleCollapse}
            style={{
              position: 'absolute',
              top: '0',
              right: collapsed ? '0' : '-8px',
              width: '32px',
              height: '32px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              borderRadius: '6px',
              background: 'rgba(255,255,255,0.1)',
              transition: 'all 0.3s ease',
              color: '#fff',
              fontSize: '16px'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255,255,255,0.2)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255,255,255,0.1)';
            }}
          >
            {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          </div>
        )}
      </div>

      {/* 菜单项 */}
      <div style={{ flex: 1 }}>
        {menuItems.map((item, index) => (
          <div
            key={item.key}
            onClick={() => !item.disabled && onMenuSelect(item.key)}
            title={collapsed ? item.label : undefined}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: collapsed ? 'center' : 'flex-start',
              padding: collapsed ? '16px' : '16px 20px',
              marginBottom: '8px',
              borderRadius: '12px',
              cursor: item.disabled ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              background: selectedKey === item.key 
                ? 'rgba(255,255,255,0.2)' 
                : 'transparent',
              border: selectedKey === item.key 
                ? '1px solid rgba(255,255,255,0.3)' 
                : '1px solid transparent',
              backdropFilter: selectedKey === item.key ? 'blur(10px)' : 'none',
              boxShadow: selectedKey === item.key 
                ? '0 4px 20px rgba(0,0,0,0.1)' 
                : 'none',
              transform: selectedKey === item.key ? (collapsed ? 'scale(1.1)' : 'translateX(4px)') : 'none',
              opacity: item.disabled ? 0.5 : 1,
              animationDelay: `${index * 0.1}s`,
              animation: 'slideInFromLeft 0.6s ease-out forwards'
            }}
            onMouseEnter={(e) => {
              if (!item.disabled && selectedKey !== item.key) {
                e.currentTarget.style.background = 'rgba(255,255,255,0.1)';
                e.currentTarget.style.transform = collapsed ? 'scale(1.1)' : 'translateX(4px)';
                e.currentTarget.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
              }
            }}
            onMouseLeave={(e) => {
              if (!item.disabled && selectedKey !== item.key) {
                e.currentTarget.style.background = 'transparent';
                e.currentTarget.style.transform = 'none';
                e.currentTarget.style.boxShadow = 'none';
              }
            }}
          >
            <div style={{
              fontSize: '20px',
              color: selectedKey === item.key ? '#fff' : 'rgba(255,255,255,0.8)',
              marginRight: collapsed ? '0' : '16px',
              transition: 'all 0.3s ease',
              transform: selectedKey === item.key ? 'scale(1.1)' : 'scale(1)'
            }}>
              {item.icon}
            </div>
            {!collapsed && (
              <div style={{
                fontSize: '16px',
                fontWeight: selectedKey === item.key ? '600' : '500',
                color: selectedKey === item.key ? '#fff' : 'rgba(255,255,255,0.9)',
                transition: 'all 0.3s ease',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis'
              }}>
                {item.label}
              </div>
            )}
            {!collapsed && item.disabled && (
              <div style={{
                marginLeft: 'auto',
                fontSize: '12px',
                color: 'rgba(255,255,255,0.6)',
                fontStyle: 'italic'
              }}>
                即将推出
              </div>
            )}
          </div>
        ))}
      </div>

      {/* 底部装饰 */}
      {!collapsed && (
        <div style={{
          marginTop: 'auto',
          padding: '20px 0',
          textAlign: 'center',
          borderTop: '1px solid rgba(255,255,255,0.2)'
        }}>
          <div style={{
            fontSize: '12px',
            color: 'rgba(255,255,255,0.6)',
            marginBottom: '8px'
          }}>
            Powered by AI
          </div>
          <div style={{
            width: '40px',
            height: '2px',
            background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent)',
            margin: '0 auto',
            borderRadius: '1px'
          }} />
        </div>
      )}

    </div>
  );
};

export default SideMenu;
