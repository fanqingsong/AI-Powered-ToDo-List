import React, { useState, useEffect } from 'react';
import {
  Card,
  Button,
  Input,
  Select,
  Space,
  Table,
  Tag,
  Modal,
  Form,
  message,
  Popconfirm,
  Tooltip,
  Badge,
  Row,
  Col,
  Statistic,
  Typography,
  Divider,
  Empty,
  Spin,
  Tabs,
  List,
  Avatar,
  Alert
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  PushpinOutlined,
  InboxOutlined,
  TagOutlined,
  FileTextOutlined,
  BarChartOutlined,
  ClockCircleOutlined,
  BookOutlined,
  BulbOutlined,
  TeamOutlined,
  FileOutlined,
  MoreOutlined
} from '@ant-design/icons';
import { noteApiService, Note, NoteCategory, CreateNoteRequest, UpdateNoteRequest, SearchNoteRequest, NoteStatsResponse } from '../services/noteApi';
import SmartSearch from './SmartSearch';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;
const { TabPane } = Tabs;

const NoteManager: React.FC = () => {
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<NoteStatsResponse | null>(null);
  const [searchParams, setSearchParams] = useState<SearchNoteRequest>({
    page: 1,
    page_size: 20,
    sort_by: 'updated_at',
    sort_order: 'desc'
  });
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [form] = Form.useForm();
  const [activeTab, setActiveTab] = useState('list');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // 检查认证状态
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const user = localStorage.getItem('user');
    setIsAuthenticated(!!(token && user));
  }, []);

  // 分类选项
  const categoryOptions = [
    { value: NoteCategory.PERSONAL, label: '个人笔记', icon: <FileTextOutlined /> },
    { value: NoteCategory.WORK, label: '工作笔记', icon: <TeamOutlined /> },
    { value: NoteCategory.STUDY, label: '学习笔记', icon: <BookOutlined /> },
    { value: NoteCategory.IDEA, label: '想法笔记', icon: <BulbOutlined /> },
    { value: NoteCategory.MEETING, label: '会议笔记', icon: <ClockCircleOutlined /> },
    { value: NoteCategory.OTHER, label: '其他', icon: <FileOutlined /> }
  ];

  // 获取分类标签颜色
  const getCategoryColor = (category: NoteCategory) => {
    const colorMap: Record<NoteCategory, string> = {
      [NoteCategory.PERSONAL]: 'blue',
      [NoteCategory.WORK]: 'green',
      [NoteCategory.STUDY]: 'purple',
      [NoteCategory.IDEA]: 'orange',
      [NoteCategory.MEETING]: 'red',
      [NoteCategory.OTHER]: 'gray'
    };
    return colorMap[category] || 'default';
  };

  // 获取分类标签
  const getCategoryLabel = (category: NoteCategory) => {
    const option = categoryOptions.find(opt => opt.value === category);
    return option?.label || category;
  };

  // 加载笔记列表
  const loadNotes = async () => {
    setLoading(true);
    try {
      const response = await noteApiService.searchNotes(searchParams);
      setNotes(response.notes);
      setTotal(response.total);
      setCurrentPage(response.page);
    } catch (error: any) {
      message.error(error.message);
    } finally {
      setLoading(false);
    }
  };

  // 加载统计信息
  const loadStats = async () => {
    try {
      const statsData = await noteApiService.getNoteStats();
      setStats(statsData);
    } catch (error: any) {
      console.error('加载统计信息失败:', error);
    }
  };

  // 加载置顶笔记
  const loadPinnedNotes = async () => {
    try {
      const pinnedNotes = await noteApiService.getPinnedNotes();
      return pinnedNotes;
    } catch (error: any) {
      console.error('加载置顶笔记失败:', error);
      return [];
    }
  };

  // 加载最近笔记
  const loadRecentNotes = async () => {
    try {
      const recentNotes = await noteApiService.getRecentNotes(7, 10);
      return recentNotes;
    } catch (error: any) {
      console.error('加载最近笔记失败:', error);
      return [];
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      loadNotes();
      loadStats();
    }
  }, [searchParams, isAuthenticated]);

  // 处理搜索
  const handleSearch = (values: any) => {
    setSearchParams(prev => ({
      ...prev,
      ...values,
      page: 1
    }));
  };

  // 处理分页
  const handlePageChange = (page: number, pageSize?: number) => {
    setSearchParams(prev => ({
      ...prev,
      page,
      page_size: pageSize || prev.page_size
    }));
  };

  // 处理排序
  const handleTableChange = (pagination: any, filters: any, sorter: any) => {
    if (sorter.field) {
      setSearchParams(prev => ({
        ...prev,
        sort_by: sorter.field,
        sort_order: sorter.order === 'ascend' ? 'asc' : 'desc',
        page: 1
      }));
    }
  };

  // 打开创建/编辑模态框
  const openModal = (note?: Note) => {
    if (note) {
      setSelectedNote(note);
      setIsEditing(true);
      form.setFieldsValue({
        title: note.title,
        content: note.content,
        category: note.category,
        tags: note.tags,
        is_pinned: note.is_pinned,
        is_archived: note.is_archived
      });
    } else {
      setSelectedNote(null);
      setIsEditing(false);
      form.resetFields();
    }
    setIsModalVisible(true);
  };

  // 关闭模态框
  const closeModal = () => {
    setIsModalVisible(false);
    setSelectedNote(null);
    setIsEditing(false);
    form.resetFields();
  };

  // 保存笔记
  const handleSave = async (values: any) => {
    try {
      if (isEditing && selectedNote) {
        const updateData: UpdateNoteRequest = {
          title: values.title,
          content: values.content,
          category: values.category,
          tags: values.tags || [],
          is_pinned: values.is_pinned || false,
          is_archived: values.is_archived || false
        };
        await noteApiService.updateNote(selectedNote.id, updateData);
        message.success('笔记更新成功');
      } else {
        const createData: CreateNoteRequest = {
          title: values.title,
          content: values.content,
          category: values.category,
          tags: values.tags || [],
          is_pinned: values.is_pinned || false,
          is_archived: values.is_archived || false
        };
        await noteApiService.createNote(createData);
        message.success('笔记创建成功');
      }
      closeModal();
      loadNotes();
      loadStats();
    } catch (error: any) {
      message.error(error.message);
    }
  };

  // 删除笔记
  const handleDelete = async (noteId: number) => {
    try {
      await noteApiService.deleteNote(noteId);
      message.success('笔记删除成功');
      loadNotes();
      loadStats();
    } catch (error: any) {
      message.error(error.message);
    }
  };

  // 切换置顶状态
  const handleTogglePin = async (noteId: number) => {
    try {
      await noteApiService.togglePin(noteId);
      message.success('置顶状态已更新');
      loadNotes();
      loadStats();
    } catch (error: any) {
      message.error(error.message);
    }
  };

  // 切换归档状态
  const handleToggleArchive = async (noteId: number) => {
    try {
      await noteApiService.toggleArchive(noteId);
      message.success('归档状态已更新');
      loadNotes();
      loadStats();
    } catch (error: any) {
      message.error(error.message);
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      sorter: true,
      render: (text: string, record: Note) => (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Text strong>{text}</Text>
            {record.is_pinned && <PushpinOutlined style={{ color: '#1890ff' }} />}
            {record.is_archived && <InboxOutlined style={{ color: '#999' }} />}
          </div>
          <div style={{ fontSize: '12px', color: '#999', marginTop: 4 }}>
            {record.word_count} 字 · {dayjs(record.updated_at).format('YYYY-MM-DD HH:mm')}
          </div>
        </div>
      )
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 120,
      render: (category: NoteCategory) => (
        <Tag color={getCategoryColor(category)}>
          {getCategoryLabel(category)}
        </Tag>
      )
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      width: 200,
      render: (tags: string[]) => (
        <div>
          {tags?.slice(0, 3).map(tag => (
            <Tag key={tag} size="small">{tag}</Tag>
          ))}
          {tags && tags.length > 3 && (
            <Tag size="small">+{tags.length - 3}</Tag>
          )}
        </div>
      )
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      render: (text: any, record: Note) => (
        <Space size="small">
          <Tooltip title="编辑">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => openModal(record)}
            />
          </Tooltip>
          <Tooltip title={record.is_pinned ? '取消置顶' : '置顶'}>
            <Button
              type="text"
              icon={<PushpinOutlined />}
              onClick={() => handleTogglePin(record.id)}
              style={{ color: record.is_pinned ? '#1890ff' : undefined }}
            />
          </Tooltip>
          <Tooltip title={record.is_archived ? '取消归档' : '归档'}>
            <Button
              type="text"
              icon={<InboxOutlined />}
              onClick={() => handleToggleArchive(record.id)}
              style={{ color: record.is_archived ? '#1890ff' : undefined }}
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这个笔记吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Tooltip title="删除">
              <Button
                type="text"
                danger
                icon={<DeleteOutlined />}
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      )
    }
  ];

  // 如果未认证，显示认证提示
  if (!isAuthenticated) {
    return (
      <div style={{ padding: '24px' }}>
        <div style={{ marginBottom: '24px' }}>
          <Title level={2} style={{ margin: 0, display: 'flex', alignItems: 'center', gap: 12 }}>
            <FileTextOutlined />
            笔记管理
          </Title>
          <Text type="secondary">管理和组织您的笔记，提高工作效率</Text>
        </div>
        
        <Alert
          message="需要登录"
          description="请先登录以使用笔记管理功能。请刷新页面并登录。"
          type="warning"
          showIcon
          action={
            <Button size="small" onClick={() => window.location.reload()}>
              刷新页面
            </Button>
          }
        />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <Title level={2} style={{ margin: 0, display: 'flex', alignItems: 'center', gap: 12 }}>
          <FileTextOutlined />
          笔记管理
        </Title>
        <Text type="secondary">管理和组织您的笔记，提高工作效率</Text>
      </div>

      {/* 统计卡片 */}
      {stats && (
        <Row gutter={16} style={{ marginBottom: '24px' }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="总笔记数"
                value={stats.total_notes}
                prefix={<FileTextOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="总字数"
                value={stats.total_words}
                prefix={<EditOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="置顶笔记"
                value={stats.pinned_notes}
                prefix={<PushpinOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="最近7天"
                value={stats.recent_notes}
                prefix={<ClockCircleOutlined />}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* 搜索和操作栏 */}
      <Card style={{ marginBottom: '24px' }}>
        <Form
          layout="inline"
          onFinish={handleSearch}
          style={{ marginBottom: '16px' }}
        >
          <Form.Item name="query" style={{ width: 300 }}>
            <Input
              placeholder="搜索笔记标题或内容..."
              prefix={<SearchOutlined />}
              allowClear
            />
          </Form.Item>
          <Form.Item name="category">
            <Select
              placeholder="选择分类"
              style={{ width: 150 }}
              allowClear
            >
              {categoryOptions.map(option => (
                <Option key={option.value} value={option.value}>
                  {option.icon} {option.label}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="is_pinned">
            <Select
              placeholder="置顶状态"
              style={{ width: 120 }}
              allowClear
            >
              <Option value={true}>已置顶</Option>
              <Option value={false}>未置顶</Option>
            </Select>
          </Form.Item>
          <Form.Item name="is_archived">
            <Select
              placeholder="归档状态"
              style={{ width: 120 }}
              allowClear
            >
              <Option value={true}>已归档</Option>
              <Option value={false}>未归档</Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" icon={<SearchOutlined />}>
                搜索
              </Button>
              <Button onClick={() => {
                setSearchParams({
                  page: 1,
                  page_size: 20,
                  sort_by: 'updated_at',
                  sort_order: 'desc'
                });
                form.resetFields();
              }}>
                重置
              </Button>
            </Space>
          </Form.Item>
        </Form>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Space>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => openModal()}
            >
              新建笔记
            </Button>
          </Space>
          <Text type="secondary">
            共 {total} 条笔记
          </Text>
        </div>
      </Card>

      {/* 笔记列表和智能搜索 */}
      <Card>
        <Tabs 
          activeKey={activeTab} 
          onChange={setActiveTab}
          items={[
            {
              key: 'list',
              label: (
                <span>
                  <FileTextOutlined />
                  笔记列表
                </span>
              ),
              children: (
                <Table
                  columns={columns}
                  dataSource={notes}
                  rowKey="id"
                  loading={loading}
                  pagination={{
                    current: currentPage,
                    total: total,
                    pageSize: searchParams.page_size,
                    showSizeChanger: true,
                    showQuickJumper: true,
                    showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
                    onChange: handlePageChange
                  }}
                  onChange={handleTableChange}
                  locale={{
                    emptyText: (
                      <Empty
                        image={Empty.PRESENTED_IMAGE_SIMPLE}
                        description="暂无笔记"
                      >
                        <Button type="primary" icon={<PlusOutlined />} onClick={() => openModal()}>
                          创建第一个笔记
                        </Button>
                      </Empty>
                    )
                  }}
                />
              )
            },
            {
              key: 'smart-search',
              label: (
                <span>
                  <SearchOutlined />
                  智能搜索
                </span>
              ),
              children: (
                <SmartSearch
                  onNoteSelect={(note) => {
                    setSelectedNote(note);
                    setIsEditing(true);
                    openModal();
                  }}
                  onNoteEdit={(note) => {
                    setSelectedNote(note);
                    setIsEditing(true);
                    openModal();
                  }}
                  onNoteDelete={(noteId) => {
                    handleDelete(noteId);
                  }}
                />
              )
            }
          ]}
        />
      </Card>

      {/* 创建/编辑模态框 */}
      <Modal
        title={isEditing ? '编辑笔记' : '新建笔记'}
        open={isModalVisible}
        onCancel={closeModal}
        footer={null}
        width={800}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSave}
          initialValues={{
            category: NoteCategory.PERSONAL,
            is_pinned: false,
            is_archived: false
          }}
        >
          <Form.Item
            name="title"
            label="标题"
            rules={[{ required: true, message: '请输入笔记标题' }]}
          >
            <Input placeholder="请输入笔记标题" />
          </Form.Item>
          
          <Form.Item
            name="category"
            label="分类"
            rules={[{ required: true, message: '请选择笔记分类' }]}
          >
            <Select placeholder="请选择笔记分类">
              {categoryOptions.map(option => (
                <Option key={option.value} value={option.value}>
                  {option.icon} {option.label}
                </Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item
            name="content"
            label="内容"
            rules={[{ required: true, message: '请输入笔记内容' }]}
          >
            <TextArea
              placeholder="请输入笔记内容..."
              rows={12}
              showCount
              maxLength={10000}
            />
          </Form.Item>
          
          <Form.Item
            name="tags"
            label="标签"
            extra="用逗号分隔多个标签"
          >
            <Select
              mode="tags"
              placeholder="添加标签"
              style={{ width: '100%' }}
            />
          </Form.Item>
          
          <Form.Item>
            <Space>
              <Form.Item name="is_pinned" valuePropName="checked" style={{ margin: 0 }}>
                <input type="checkbox" /> 置顶
              </Form.Item>
              <Form.Item name="is_archived" valuePropName="checked" style={{ margin: 0 }}>
                <input type="checkbox" /> 归档
              </Form.Item>
            </Space>
          </Form.Item>
          
          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={closeModal}>
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                {isEditing ? '更新' : '创建'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default NoteManager;
