"use client";

import { useAssistantInstructions, useAssistantTool, AssistantRuntimeProvider, useEdgeRuntime } from "@assistant-ui/react";
import { Thread } from "@assistant-ui/react";
import { AuthService } from "../services/authApi";
import { Typography, Button, Avatar, Badge, Tooltip } from "antd";
import { 
  RobotOutlined, 
  UserOutlined, 
  CopyOutlined, 
  ReloadOutlined,
  VerticalAlignBottomOutlined
} from "@ant-design/icons";
import { useState } from "react";

const { Title, Text } = Typography;

// 美化的消息气泡组件
function MessageBubble({ 
  content, 
  isUser, 
  timestamp 
}: { 
  content: string; 
  isUser: boolean; 
  timestamp?: string; 
}) {
  return (
    <div 
      className="message-bubble"
      style={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        marginBottom: '16px'
      }}
    >
      <div
        style={{
          maxWidth: '80%',
          padding: '12px 16px',
          borderRadius: isUser ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
          background: isUser 
            ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
            : 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
          color: 'white',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          position: 'relative',
          wordWrap: 'break-word',
          transition: 'all 0.2s ease'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'scale(1.02)';
          e.currentTarget.style.boxShadow = '0 6px 16px rgba(0, 0, 0, 0.2)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'scale(1)';
          e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Avatar 
            size="small" 
            icon={isUser ? <UserOutlined /> : <RobotOutlined />}
            style={{ 
              backgroundColor: 'rgba(255,255,255,0.2)',
              border: '2px solid rgba(255,255,255,0.3)',
              transition: 'all 0.2s ease'
            }}
          />
          <div>
            <div style={{ fontSize: '14px', lineHeight: '1.4' }}>
              {content}
            </div>
            {timestamp && (
              <div style={{ 
                fontSize: '11px', 
                opacity: 0.7, 
                marginTop: '4px',
                textAlign: 'right'
              }}>
                {timestamp}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function AssistantContent() {
  const [messageCount] = useState(0);

  // 设置助手指令
  useAssistantInstructions("你是一个智能任务管理助手，可以帮助用户管理任务、安排日程、导航页面等。");

  // 刷新任务列表工具
  useAssistantTool({
    toolName: "refresh_task_list",
    description: "刷新前端任务列表，获取最新的任务数据",
    parameters: {},
    execute: async () => {
      console.log('🔄 执行刷新任务列表工具');
      // 触发自定义事件来刷新任务列表
      const event = new CustomEvent('refreshTaskList', {
        detail: { timestamp: Date.now() }
      });
      window.dispatchEvent(event);
      return "任务列表已刷新";
    },
  });

  // 页面导航工具
  useAssistantTool({
    toolName: "navigate_to_page",
    description: "导航到指定页面",
    parameters: {
      type: "object",
      properties: {
        page_key: {
          type: "string",
          description: "页面标识符 (settings, tasks, calendar, notes, analytics)",
          enum: ["settings", "tasks", "calendar", "notes", "analytics"]
        }
      },
      required: ["page_key"]
    },
    execute: async (params: { page_key: string }) => {
      console.log('🧭 执行页面导航工具:', params.page_key);
      
      const pageNames = {
        'settings': '系统设置',
        'tasks': '任务管理',
        'calendar': '日程安排',
        'notes': '笔记管理',
        'analytics': '数据分析'
      };
      
      const pageName = pageNames[params.page_key as keyof typeof pageNames] || params.page_key;
      
      return `已成功导航到${pageName}页面。`;
    },
  });

  // 显示通知工具
  useAssistantTool({
    toolName: "show_notification",
    description: "在前端显示通知消息",
    parameters: {
      type: "object",
      properties: {
        message: {
          type: "string",
          description: "通知消息内容"
        },
        type: {
          type: "string",
          description: "通知类型",
          enum: ["success", "info", "warning", "error"],
          default: "info"
        }
      },
      required: ["message"]
    },
    execute: async (params: { message: string; type?: string }) => {
      console.log('🔔 执行显示通知工具:', params.message, params.type);
      return `已显示${params.type || 'info'}类型的通知: ${params.message}`;
    },
  });

  return (
    <div style={{
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      borderRadius: '16px',
      overflow: 'hidden',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
    }}>
      {/* 头部 */}
      <div style={{
        padding: '16px 20px',
        background: 'rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Avatar 
            icon={<RobotOutlined />} 
            style={{ 
              background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
              border: '2px solid rgba(255,255,255,0.3)'
            }}
          />
          <div>
            <Title level={5} style={{ color: 'white', margin: 0, fontSize: '16px' }}>
              AI 智能助手
            </Title>
            <Text style={{ color: 'rgba(255,255,255,0.8)', fontSize: '12px' }}>
              任务管理专家
            </Text>
          </div>
        </div>
        <Badge 
          count={messageCount} 
          style={{ backgroundColor: '#52c41a' }}
        />
      </div>

      {/* 对话区域 */}
      <div style={{
        flex: 1,
        padding: '20px',
        overflowY: 'auto',
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(5px)'
      }}>
        <Thread
          assistantMessage={{ 
            components: { 
              Text: ({ text }: { text: string }) => (
                <MessageBubble 
                  content={text} 
                  isUser={false} 
                  timestamp={new Date().toLocaleTimeString()}
                />
              )
            } 
          }}
        />
        
        {/* 输入提示 */}
        <div style={{
          marginTop: '20px',
          padding: '16px',
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '12px',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          textAlign: 'center'
        }}>
          <Text style={{ color: 'rgba(255,255,255,0.8)', fontSize: '14px' }}>
            💡 试试说："添加任务：学习新技能" 或 "查看我的任务"
          </Text>
        </div>
      </div>

      {/* 底部操作栏 */}
      <div style={{
        padding: '16px 20px',
        background: 'rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(10px)',
        borderTop: '1px solid rgba(255, 255, 255, 0.2)',
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
      }}>
        <Tooltip title="复制对话">
          <Button 
            type="text" 
            icon={<CopyOutlined />} 
            style={{ color: 'rgba(255,255,255,0.8)' }}
          />
        </Tooltip>
        <Tooltip title="刷新">
          <Button 
            type="text" 
            icon={<ReloadOutlined />} 
            style={{ color: 'rgba(255,255,255,0.8)' }}
          />
        </Tooltip>
        <Tooltip title="滚动到底部">
          <Button 
            type="text" 
            icon={<VerticalAlignBottomOutlined />} 
            style={{ color: 'rgba(255,255,255,0.8)' }}
          />
        </Tooltip>
        <div style={{ flex: 1 }} />
        <Text style={{ color: 'rgba(255,255,255,0.6)', fontSize: '12px' }}>
          v1.0.0
        </Text>
      </div>
    </div>
  );
}

export function AssistantUIWithTools() {
  // 获取 API 基础 URL，确保以 /api 开头
  const baseApiUrl = import.meta.env.VITE_API_URL || "";
  const apiUrl = baseApiUrl.endsWith("/api") 
    ? baseApiUrl 
    : baseApiUrl 
      ? `${baseApiUrl}/api` 
      : "/api";
  
  const authService = AuthService.getInstance();
  
  // 获取认证头
  const getAuthHeaders = (): Record<string, string> => {
    const token = authService.getToken();
    if (token) {
      return {
        'Authorization': `Bearer ${token}`,
      };
    }
    return {};
  };
  
  const runtime = useEdgeRuntime({
    api: `${apiUrl}/chat`,  // 完整路径：/api/chat
    unstable_AISDKInterop: true,
    headers: getAuthHeaders(),
  });

  return (
    <>
      {/* 添加 CSS 动画样式 */}
      <style>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes pulse {
          0% {
            transform: scale(1);
          }
          50% {
            transform: scale(1.05);
          }
          100% {
            transform: scale(1);
          }
        }
        
        .assistant-container {
          height: 100%;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 16px;
          overflow: hidden;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .assistant-container:hover {
          box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
          transform: translateY(-2px);
          transition: all 0.3s ease;
        }
        
        .message-bubble {
          animation: fadeInUp 0.3s ease-out;
        }
        
        .typing-indicator {
          animation: pulse 1.5s infinite;
        }
        
        .glass-effect {
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.2);
        }
      `}</style>
      
      <div className="assistant-container">
        <AssistantRuntimeProvider runtime={runtime}>
          <AssistantContent />
        </AssistantRuntimeProvider>
      </div>
    </>
  );
}

export default AssistantUIWithTools;