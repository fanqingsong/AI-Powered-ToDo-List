/**
 * 智能搜索组件
 * 提供基于向量数据库的智能搜索功能
 */

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Input, 
  Button, 
  Card, 
  List, 
  Typography, 
  Space, 
  Tag, 
  Select, 
  Switch, 
  Spin, 
  Alert, 
  Tooltip,
  Divider,
  Row,
  Col,
  Statistic,
  message
} from 'antd';
import { 
  SearchOutlined, 
  BulbOutlined, 
  ReloadOutlined, 
  HeartOutlined,
  BookOutlined,
  TagOutlined,
  ClockCircleOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';
import { smartSearchApi, SmartSearchRequest, SmartSearchResponse, SearchStats } from '../services/smartSearchApi';
import { Note, NoteCategory } from '../services/noteApi';
import dayjs from 'dayjs';

const { Search } = Input;
const { Option } = Select;
const { Title, Text, Paragraph } = Typography;

interface SmartSearchProps {
  onNoteSelect?: (note: Note) => void;
  onNoteEdit?: (note: Note) => void;
  onNoteDelete?: (noteId: number) => void;
}

const SmartSearch: React.FC<SmartSearchProps> = ({
  onNoteSelect,
  onNoteEdit,
  onNoteDelete
}) => {
  // 状态管理
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Note[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchStats, setSearchStats] = useState<SearchStats | null>(null);
  const [searchEnabled, setSearchEnabled] = useState(false);
  
  // 搜索参数
  const [searchParams, setSearchParams] = useState<Partial<SmartSearchRequest>>({
    limit: 10,
    include_archived: false
  });

  // 初始化
  useEffect(() => {
    checkSearchHealth();
    loadSearchStats();
  }, []);

  // 检查搜索服务健康状态
  const checkSearchHealth = async () => {
    try {
      const health = await smartSearchApi.healthCheck();
      setSearchEnabled(health.search_enabled);
      
      if (!health.search_enabled) {
        message.warning('智能搜索服务暂不可用，请稍后重试');
      }
    } catch (error) {
      console.error('检查搜索服务健康状态失败:', error);
      setSearchEnabled(false);
    }
  };

  // 加载搜索统计信息
  const loadSearchStats = async () => {
    try {
      const stats = await smartSearchApi.getSearchStats();
      setSearchStats(stats);
    } catch (error) {
      console.error('加载搜索统计失败:', error);
    }
  };

  // 执行智能搜索
  const performSearch = useCallback(async (query: string) => {
    if (!query.trim() || !searchEnabled) return;

    setLoading(true);
    try {
      const request: SmartSearchRequest = {
        query: query.trim(),
        ...searchParams
      };

      const response: SmartSearchResponse = await smartSearchApi.smartSearch(request);
      setSearchResults(response.notes);
      setSuggestions(response.suggestions || []);
      
      message.success(`找到 ${response.total} 个相关笔记`);
    } catch (error) {
      console.error('智能搜索失败:', error);
      message.error('搜索失败，请稍后重试');
      setSearchResults([]);
      setSuggestions([]);
    } finally {
      setLoading(false);
    }
  }, [searchParams, searchEnabled]);

  // 获取搜索建议
  const getSuggestions = useCallback(async (query: string) => {
    if (!query.trim() || !searchEnabled) return;

    try {
      const suggestions = await smartSearchApi.getSearchSuggestions({
        query: query.trim(),
        limit: 5
      });
      setSuggestions(suggestions);
    } catch (error) {
      console.error('获取搜索建议失败:', error);
    }
  }, [searchEnabled]);

  // 搜索输入处理
  const handleSearch = (value: string) => {
    setSearchQuery(value);
    performSearch(value);
  };

  // 搜索建议点击
  const handleSuggestionClick = (suggestion: string) => {
    setSearchQuery(suggestion);
    performSearch(suggestion);
  };

  // 重新索引
  const handleReindex = async () => {
    try {
      setLoading(true);
      const result = await smartSearchApi.reindexUserNotes();
      
      if (result.status === 'completed') {
        message.success(`重新索引完成！成功 ${result.success_count} 个，失败 ${result.failed_count} 个`);
        loadSearchStats();
      } else {
        message.error('重新索引失败');
      }
    } catch (error) {
      console.error('重新索引失败:', error);
      message.error('重新索引失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  // 渲染笔记项
  const renderNoteItem = (note: Note) => (
    <List.Item
      key={note.id}
      actions={[
        <Tooltip title="查看详情">
          <Button 
            type="text" 
            icon={<InfoCircleOutlined />}
            onClick={() => onNoteSelect?.(note)}
          />
        </Tooltip>,
        <Tooltip title="编辑笔记">
          <Button 
            type="text" 
            icon={<BookOutlined />}
            onClick={() => onNoteEdit?.(note)}
          />
        </Tooltip>
      ]}
    >
      <List.Item.Meta
        title={
          <Space>
            <Text strong>{note.title}</Text>
            {note.is_pinned && <Tag color="gold" icon={<HeartOutlined />}>置顶</Tag>}
            {note.is_archived && <Tag color="default">归档</Tag>}
          </Space>
        }
        description={
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <Paragraph 
              ellipsis={{ rows: 2, expandable: true }}
              style={{ margin: 0 }}
            >
              {note.content}
            </Paragraph>
            <Space size="small">
              <Tag color="blue">{note.category}</Tag>
              {note.tags.map(tag => (
                <Tag key={tag} color="green" icon={<TagOutlined />}>
                  {tag}
                </Tag>
              ))}
              <Text type="secondary" style={{ fontSize: '12px' }}>
                <ClockCircleOutlined /> {dayjs(note.updated_at).format('YYYY-MM-DD HH:mm')}
              </Text>
              <Text type="secondary" style={{ fontSize: '12px' }}>
                {note.word_count} 字
              </Text>
            </Space>
          </Space>
        }
      />
    </List.Item>
  );

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>
        <SearchOutlined /> 智能搜索
      </Title>
      
      {/* 搜索状态提示 */}
      {!searchEnabled && (
        <Alert
          message="智能搜索服务暂不可用"
          description="请检查向量数据库连接状态，或联系管理员"
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {/* 搜索统计信息 */}
      {searchStats && (
        <Card size="small" style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={6}>
              <Statistic 
                title="总笔记数" 
                value={searchStats.total_notes}
                prefix={<BookOutlined />}
              />
            </Col>
            <Col span={6}>
              <Statistic 
                title="总字数" 
                value={searchStats.total_words}
                suffix="字"
              />
            </Col>
            <Col span={6}>
              <Statistic 
                title="置顶笔记" 
                value={searchStats.pinned_notes}
                prefix={<HeartOutlined />}
              />
            </Col>
            <Col span={6}>
              <Statistic 
                title="向量数据库" 
                value={searchStats.vector_db_status === 'connected' ? '正常' : '异常'}
                valueStyle={{ 
                  color: searchStats.vector_db_status === 'connected' ? '#3f8600' : '#cf1322' 
                }}
              />
            </Col>
          </Row>
        </Card>
      )}

      {/* 搜索控制面板 */}
      <Card title="搜索设置" size="small" style={{ marginBottom: 16 }}>
        <Space wrap>
          <div>
            <Text>结果数量：</Text>
            <Select
              value={searchParams.limit}
              onChange={(value) => setSearchParams(prev => ({ ...prev, limit: value }))}
              style={{ width: 80 }}
            >
              <Option value={5}>5</Option>
              <Option value={10}>10</Option>
              <Option value={20}>20</Option>
              <Option value={50}>50</Option>
            </Select>
          </div>
          
          <div>
            <Text>分类：</Text>
            <Select
              value={searchParams.category}
              onChange={(value) => setSearchParams(prev => ({ ...prev, category: value }))}
              allowClear
              style={{ width: 120 }}
            >
              <Option value={NoteCategory.PERSONAL}>个人笔记</Option>
              <Option value={NoteCategory.WORK}>工作笔记</Option>
              <Option value={NoteCategory.STUDY}>学习笔记</Option>
              <Option value={NoteCategory.MEETING}>会议笔记</Option>
              <Option value={NoteCategory.OTHER}>其他</Option>
            </Select>
          </div>
          
          <div>
            <Text>包含归档：</Text>
            <Switch
              checked={searchParams.include_archived}
              onChange={(checked) => setSearchParams(prev => ({ ...prev, include_archived: checked }))}
            />
          </div>
          
          <Button 
            icon={<ReloadOutlined />}
            onClick={handleReindex}
            loading={loading}
          >
            重新索引
          </Button>
        </Space>
      </Card>

      {/* 搜索输入框 */}
      <Card>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Search
            placeholder="输入搜索内容，支持语义搜索..."
            value={searchQuery}
            onChange={(e) => {
              const value = e.target.value;
              setSearchQuery(value);
              if (value.trim()) {
                getSuggestions(value);
              } else {
                setSuggestions([]);
              }
            }}
            onSearch={handleSearch}
            enterButton={<SearchOutlined />}
            size="large"
            disabled={!searchEnabled}
          />

          {/* 搜索建议 */}
          {suggestions.length > 0 && (
            <div>
              <Text type="secondary">
                <BulbOutlined /> 搜索建议：
              </Text>
              <Space wrap style={{ marginTop: 8 }}>
                {suggestions.map((suggestion, index) => (
                  <Tag
                    key={index}
                    color="blue"
                    style={{ cursor: 'pointer' }}
                    onClick={() => handleSuggestionClick(suggestion)}
                  >
                    {suggestion}
                  </Tag>
                ))}
              </Space>
            </div>
          )}

          <Divider />

          {/* 搜索结果 */}
          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <Spin size="large" />
              <div style={{ marginTop: 16 }}>
                <Text type="secondary">正在搜索中...</Text>
              </div>
            </div>
          ) : searchResults.length > 0 ? (
            <div>
              <Title level={4}>
                搜索结果 ({searchResults.length})
              </Title>
              <List
                dataSource={searchResults}
                renderItem={renderNoteItem}
                pagination={{
                  pageSize: 5,
                  showSizeChanger: false,
                  showQuickJumper: true
                }}
              />
            </div>
          ) : searchQuery ? (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <Text type="secondary">未找到相关笔记</Text>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <Text type="secondary">请输入搜索内容</Text>
            </div>
          )}
        </Space>
      </Card>
    </div>
  );
};

export default SmartSearch;
