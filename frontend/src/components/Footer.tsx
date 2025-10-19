import React from 'react';
import { Layout, Typography, Space, Divider } from 'antd';
import { 
  ThunderboltOutlined, 
  GithubOutlined, 
  HeartOutlined,
  CopyrightOutlined 
} from '@ant-design/icons';

const { Footer: AntFooter } = Layout;
const { Text, Link } = Typography;

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <AntFooter style={{ 
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '24px 24px',
      textAlign: 'center',
      borderTop: '1px solid rgba(255,255,255,0.1)',
      boxShadow: '0 -2px 12px rgba(0,0,0,0.1)'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* 主要内容区域 */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: '16px',
          flexWrap: 'wrap',
          gap: '16px'
        }}>
          {/* 左侧：品牌信息 */}
          <Space align="center">
            <ThunderboltOutlined style={{ fontSize: '20px', color: '#fff' }} />
            <Text style={{ color: '#fff', fontSize: '16px', fontWeight: '500' }}>
              AI Native 智能工作台
            </Text>
          </Space>

          {/* 中间：链接区域 */}
          <Space size="large" wrap>
            <Link 
              href="#" 
              style={{ color: 'rgba(255,255,255,0.8)' }}
              onMouseEnter={(e) => e.currentTarget.style.color = '#fff'}
              onMouseLeave={(e) => e.currentTarget.style.color = 'rgba(255,255,255,0.8)'}
            >
              帮助中心
            </Link>
            <Link 
              href="#" 
              style={{ color: 'rgba(255,255,255,0.8)' }}
              onMouseEnter={(e) => e.currentTarget.style.color = '#fff'}
              onMouseLeave={(e) => e.currentTarget.style.color = 'rgba(255,255,255,0.8)'}
            >
              隐私政策
            </Link>
            <Link 
              href="#" 
              style={{ color: 'rgba(255,255,255,0.8)' }}
              onMouseEnter={(e) => e.currentTarget.style.color = '#fff'}
              onMouseLeave={(e) => e.currentTarget.style.color = 'rgba(255,255,255,0.8)'}
            >
              服务条款
            </Link>
            <Link 
              href="#" 
              style={{ color: 'rgba(255,255,255,0.8)' }}
              onMouseEnter={(e) => e.currentTarget.style.color = '#fff'}
              onMouseLeave={(e) => e.currentTarget.style.color = 'rgba(255,255,255,0.8)'}
            >
              联系我们
            </Link>
          </Space>

          {/* 右侧：社交媒体和状态 */}
          <Space align="center">
            <Text style={{ color: 'rgba(255,255,255,0.8)', fontSize: '12px' }}>
              <HeartOutlined style={{ color: '#ff6b6b', marginRight: '4px' }} />
              Made with AI
            </Text>
            <Divider type="vertical" style={{ borderColor: 'rgba(255,255,255,0.3)' }} />
            <Link 
              href="https://github.com" 
              target="_blank" 
              style={{ color: 'rgba(255,255,255,0.8)' }}
              onMouseEnter={(e) => e.currentTarget.style.color = '#fff'}
              onMouseLeave={(e) => e.currentTarget.style.color = 'rgba(255,255,255,0.8)'}
            >
              <GithubOutlined style={{ fontSize: '16px' }} />
            </Link>
          </Space>
        </div>

        {/* 分隔线 */}
        <Divider style={{ borderColor: 'rgba(255,255,255,0.2)', margin: '16px 0' }} />

        {/* 底部版权信息 */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '8px'
        }}>
          <Text style={{ color: 'rgba(255,255,255,0.7)', fontSize: '12px' }}>
            <CopyrightOutlined style={{ marginRight: '4px' }} />
            {currentYear} AI Native. All rights reserved.
          </Text>
          
          <Space size="small">
            <Text style={{ color: 'rgba(255,255,255,0.7)', fontSize: '12px' }}>
              版本 v1.0.0
            </Text>
            <Divider type="vertical" style={{ borderColor: 'rgba(255,255,255,0.3)' }} />
            <Text style={{ color: 'rgba(255,255,255,0.7)', fontSize: '12px' }}>
              系统状态: 
              <span style={{ color: '#52c41a', marginLeft: '4px' }}>
                ● 正常
              </span>
            </Text>
          </Space>
        </div>
      </div>
    </AntFooter>
  );
};

export default Footer;
