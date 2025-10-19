import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Select,
  Spin,
  Alert,
  Tabs,
  Progress,
  Tag,
  Space,
  Typography,
  Divider
} from 'antd';
import {
  BarChartOutlined,
  CheckCircleOutlined,
  FileTextOutlined,
  CalendarOutlined,
  UserOutlined,
  TrophyOutlined,
  FireOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { analyticsApi, AnalyticsOverview, TimeRange } from '../services/analyticsApi';

const { Title, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

const AnalyticsManager: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analyticsData, setAnalyticsData] = useState<AnalyticsOverview | null>(null);
  const [timeRange, setTimeRange] = useState<TimeRange>('month');

  // 颜色配置
  const colors = {
    primary: '#1890ff',
    success: '#52c41a',
    warning: '#faad14',
    error: '#f5222d',
    purple: '#722ed1',
    cyan: '#13c2c2',
    orange: '#fa8c16',
    pink: '#eb2f96'
  };

  const chartColors = [
    colors.primary,
    colors.success,
    colors.warning,
    colors.error,
    colors.purple,
    colors.cyan,
    colors.orange,
    colors.pink
  ];

  useEffect(() => {
    fetchAnalyticsData();
  }, [timeRange]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await analyticsApi.getAnalyticsOverview(timeRange, true);
      
      if (response.success && response.data) {
        setAnalyticsData(response.data);
      } else {
        setError(response.error || '获取数据失败');
      }
    } catch (err) {
      setError('网络错误，请稍后重试');
      console.error('Error fetching analytics data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTimeRangeChange = (value: TimeRange) => {
    setTimeRange(value);
  };

  const formatTimeRange = (range: TimeRange) => {
    const rangeMap = {
      today: '今日',
      week: '本周',
      month: '本月',
      quarter: '本季度',
      year: '本年',
      all: '全部'
    };
    return rangeMap[range];
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: '16px' }}>正在加载分析数据...</div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        message="数据加载失败"
        description={error}
        type="error"
        showIcon
        action={
          <button onClick={fetchAnalyticsData} style={{ marginLeft: '16px' }}>
            重试
          </button>
        }
      />
    );
  }

  if (!analyticsData) {
    return (
      <Alert
        message="暂无数据"
        description="当前时间段内没有数据可供分析"
        type="info"
        showIcon
      />
    );
  }

  const { task_analytics, note_analytics, schedule_analytics, user_activity, productivity_metrics } = analyticsData;

  // 任务完成趋势图数据
  const taskTrendData = task_analytics.tasks_by_day.map(item => ({
    date: item.period,
    已完成: item.completed,
    待完成: item.pending,
    总计: item.total
  }));

  // 笔记分类饼图数据
  const noteCategoryData = note_analytics.notes_by_category.map((item, index) => ({
    name: item.category,
    value: item.count,
    color: chartColors[index % chartColors.length]
  }));

  // 日程优先级柱状图数据
  const schedulePriorityData = schedule_analytics.schedules_by_priority.map(item => ({
    priority: item.priority,
    count: item.count
  }));

  // 用户活动趋势数据
  const userActivityData = user_activity.user_activity_by_day.map(item => ({
    date: item.period,
    新用户: item.new_users
  }));

  return (
    <div style={{ padding: '24px' }}>
      {/* 页面标题和筛选器 */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '24px'
      }}>
        <div>
          <Title level={2} style={{ margin: 0 }}>
            <BarChartOutlined style={{ marginRight: '8px', color: colors.primary }} />
            数据分析
          </Title>
          <Text type="secondary">管理和分析您的工作数据，提高工作效率</Text>
        </div>
        <Select
          value={timeRange}
          onChange={handleTimeRangeChange}
          style={{ width: 120 }}
        >
          <Option value="today">今日</Option>
          <Option value="week">本周</Option>
          <Option value="month">本月</Option>
          <Option value="quarter">本季度</Option>
          <Option value="year">本年</Option>
          <Option value="all">全部</Option>
        </Select>
      </div>

      {/* 生产力指标卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="今日完成任务"
              value={productivity_metrics.tasks_completed_today}
              prefix={<CheckCircleOutlined style={{ color: colors.success }} />}
              valueStyle={{ color: colors.success }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="今日创建笔记"
              value={productivity_metrics.notes_created_today}
              prefix={<FileTextOutlined style={{ color: colors.primary }} />}
              valueStyle={{ color: colors.primary }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="今日完成日程"
              value={productivity_metrics.schedules_completed_today}
              prefix={<CalendarOutlined style={{ color: colors.warning }} />}
              valueStyle={{ color: colors.warning }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="生产力评分"
              value={productivity_metrics.productivity_score}
              suffix="/ 100"
              prefix={<TrophyOutlined style={{ color: colors.purple }} />}
              valueStyle={{ color: colors.purple }}
            />
          </Card>
        </Col>
      </Row>

      {/* 详细统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} md={8}>
          <Card title="任务统计" extra={<CheckCircleOutlined />}>
            <Row gutter={16}>
              <Col span={12}>
                <Statistic
                  title="总任务数"
                  value={task_analytics.total_tasks}
                  valueStyle={{ color: colors.primary }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="完成率"
                  value={task_analytics.completion_rate}
                  suffix="%"
                  valueStyle={{ color: colors.success }}
                />
              </Col>
            </Row>
            <Divider />
            <div>
              <Text strong>平均完成时间：</Text>
              <Text>
                {task_analytics.average_completion_time 
                  ? `${task_analytics.average_completion_time} 小时`
                  : '暂无数据'
                }
              </Text>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8}>
          <Card title="笔记统计" extra={<FileTextOutlined />}>
            <Row gutter={16}>
              <Col span={12}>
                <Statistic
                  title="总笔记数"
                  value={note_analytics.total_notes}
                  valueStyle={{ color: colors.primary }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="总字数"
                  value={note_analytics.total_words}
                  valueStyle={{ color: colors.success }}
                />
              </Col>
            </Row>
            <Divider />
            <div>
              <Text strong>平均字数：</Text>
              <Text>{note_analytics.average_words_per_note} 字/篇</Text>
            </div>
            <div style={{ marginTop: '8px' }}>
              <Space>
                <Tag color="blue">置顶: {note_analytics.pinned_notes}</Tag>
                <Tag color="orange">归档: {note_analytics.archived_notes}</Tag>
              </Space>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8}>
          <Card title="日程统计" extra={<CalendarOutlined />}>
            <Row gutter={16}>
              <Col span={12}>
                <Statistic
                  title="总日程数"
                  value={schedule_analytics.total_schedules}
                  valueStyle={{ color: colors.primary }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="完成率"
                  value={schedule_analytics.completion_rate}
                  suffix="%"
                  valueStyle={{ color: colors.success }}
                />
              </Col>
            </Row>
            <Divider />
            <div>
              <Text strong>平均时长：</Text>
              <Text>
                {schedule_analytics.average_duration 
                  ? `${schedule_analytics.average_duration} 小时`
                  : '暂无数据'
                }
              </Text>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 图表分析 */}
      <Card title="数据可视化分析" style={{ marginBottom: '24px' }}>
        <Tabs defaultActiveKey="tasks">
          <TabPane tab="任务趋势" key="tasks">
            <div style={{ height: '400px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={taskTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="已完成" 
                    stroke={colors.success} 
                    strokeWidth={2}
                    dot={{ fill: colors.success, strokeWidth: 2, r: 4 }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="待完成" 
                    stroke={colors.warning} 
                    strokeWidth={2}
                    dot={{ fill: colors.warning, strokeWidth: 2, r: 4 }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="总计" 
                    stroke={colors.primary} 
                    strokeWidth={2}
                    dot={{ fill: colors.primary, strokeWidth: 2, r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </TabPane>
          
          <TabPane tab="笔记分类" key="notes">
            <div style={{ height: '400px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={noteCategoryData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={120}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {noteCategoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </TabPane>
          
          <TabPane tab="日程优先级" key="schedules">
            <div style={{ height: '400px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={schedulePriorityData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="priority" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="count" fill={colors.primary} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </TabPane>
          
          <TabPane tab="用户活动" key="users">
            <div style={{ height: '400px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={userActivityData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Area 
                    type="monotone" 
                    dataKey="新用户" 
                    stroke={colors.purple} 
                    fill={colors.purple}
                    fillOpacity={0.3}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </TabPane>
        </Tabs>
      </Card>

      {/* 生产力指标详情 */}
      <Card title="生产力指标详情">
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={8}>
            <div style={{ textAlign: 'center' }}>
              <Progress
                type="circle"
                percent={productivity_metrics.productivity_score}
                strokeColor={colors.primary}
                format={percent => `${percent}分`}
              />
              <div style={{ marginTop: '16px' }}>
                <Text strong>生产力评分</Text>
              </div>
            </div>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '48px', color: colors.warning, marginBottom: '8px' }}>
                <FireOutlined />
              </div>
              <div>
                <Text strong>连续活跃</Text>
              </div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: colors.warning }}>
                {productivity_metrics.streak_days} 天
              </div>
            </div>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '48px', color: colors.success, marginBottom: '8px' }}>
                <ClockCircleOutlined />
              </div>
              <div>
                <Text strong>今日工作时长</Text>
              </div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: colors.success }}>
                {productivity_metrics.total_work_time_today} 小时
              </div>
            </div>
          </Col>
        </Row>
        
        <Divider />
        
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <div>
              <Text strong>周目标完成进度：</Text>
              <Progress 
                percent={productivity_metrics.weekly_goal_progress} 
                strokeColor={colors.success}
                style={{ marginTop: '8px' }}
              />
            </div>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default AnalyticsManager;
