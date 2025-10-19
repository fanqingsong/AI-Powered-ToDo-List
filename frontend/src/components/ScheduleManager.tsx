import React, { useState, useEffect } from 'react';
import {
  Card,
  Button,
  Modal,
  Form,
  Input,
  DatePicker,
  TimePicker,
  Switch,
  Select,
  Space,
  message,
  Row,
  Col,
  List,
  Tag,
  Popconfirm,
  Typography,
  Divider,
  Badge,
  Calendar,
  Tooltip,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  CalendarOutlined,
  ClockCircleOutlined,
  EnvironmentOutlined,
} from '@ant-design/icons';
import { scheduleApi, Schedule, ScheduleCreate, ScheduleUpdate } from '../services/scheduleApi';
import dayjs, { Dayjs } from 'dayjs';
import 'dayjs/locale/zh-cn';
import locale from 'antd/es/date-picker/locale/zh_CN';

dayjs.locale('zh-cn');

const { TextArea } = Input;
const { Option } = Select;
const { Title, Text } = Typography;

const ScheduleManager: React.FC = () => {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingSchedule, setEditingSchedule] = useState<Schedule | null>(null);
  const [form] = Form.useForm();
  const [selectedDate, setSelectedDate] = useState<Dayjs>(dayjs());
  const [viewMode, setViewMode] = useState<'calendar' | 'list'>('calendar');

  // 颜色选项
  const colorOptions = [
    { value: '#1890ff', label: '蓝色', color: '#1890ff' },
    { value: '#52c41a', label: '绿色', color: '#52c41a' },
    { value: '#faad14', label: '橙色', color: '#faad14' },
    { value: '#f5222d', label: '红色', color: '#f5222d' },
    { value: '#722ed1', label: '紫色', color: '#722ed1' },
    { value: '#13c2c2', label: '青色', color: '#13c2c2' },
  ];

  // 加载日程数据
  const loadSchedules = async () => {
    setLoading(true);
    try {
      const startOfMonth = selectedDate.startOf('month');
      const endOfMonth = selectedDate.endOf('month');
      const data = await scheduleApi.getSchedulesByDateRange(
        startOfMonth.format('YYYY-MM-DD'),
        endOfMonth.format('YYYY-MM-DD')
      );
      setSchedules(data);
    } catch (error) {
      message.error('加载日程失败');
      console.error('Load schedules error:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSchedules();
  }, [selectedDate]);

  // 打开创建/编辑模态框
  const openModal = (schedule?: Schedule) => {
    if (schedule) {
      setEditingSchedule(schedule);
      form.setFieldsValue({
        title: schedule.title,
        description: schedule.description,
        start_time: dayjs(schedule.start_time),
        end_time: dayjs(schedule.end_time),
        is_all_day: schedule.is_all_day,
        location: schedule.location,
        color: schedule.color,
      });
    } else {
      setEditingSchedule(null);
      form.resetFields();
      // 设置默认时间为当前时间
      const now = dayjs();
      form.setFieldsValue({
        start_time: now,
        end_time: now.add(1, 'hour'),
        color: '#1890ff',
      });
    }
    setModalVisible(true);
  };

  // 关闭模态框
  const closeModal = () => {
    setModalVisible(false);
    setEditingSchedule(null);
    form.resetFields();
  };

  // 提交表单
  const handleSubmit = async (values: any) => {
    try {
      const scheduleData: ScheduleCreate | ScheduleUpdate = {
        title: values.title,
        description: values.description,
        start_time: values.start_time.toISOString(),
        end_time: values.end_time.toISOString(),
        is_all_day: values.is_all_day || false,
        location: values.location,
        color: values.color,
      };

      if (editingSchedule) {
        await scheduleApi.updateSchedule(editingSchedule.id, scheduleData);
        message.success('日程更新成功');
      } else {
        await scheduleApi.createSchedule(scheduleData as ScheduleCreate);
        message.success('日程创建成功');
      }

      closeModal();
      loadSchedules();
    } catch (error) {
      message.error(editingSchedule ? '更新日程失败' : '创建日程失败');
      console.error('Submit schedule error:', error);
    }
  };

  // 删除日程
  const handleDelete = async (scheduleId: number) => {
    try {
      await scheduleApi.deleteSchedule(scheduleId);
      message.success('日程删除成功');
      loadSchedules();
    } catch (error) {
      message.error('删除日程失败');
      console.error('Delete schedule error:', error);
    }
  };

  // 日历单元格渲染
  const dateCellRender = (value: Dayjs) => {
    const daySchedules = schedules.filter(schedule => {
      const scheduleDate = dayjs(schedule.start_time);
      return scheduleDate.isSame(value, 'day');
    });

    return (
      <div style={{ maxHeight: '100px', overflow: 'hidden' }}>
        {daySchedules.map(schedule => (
          <div
            key={schedule.id}
            style={{
              background: schedule.color,
              color: 'white',
              padding: '2px 4px',
              margin: '1px 0',
              borderRadius: '2px',
              fontSize: '12px',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
            title={schedule.title}
          >
            {schedule.title}
          </div>
        ))}
      </div>
    );
  };

  // 获取今日日程
  const getTodaySchedules = () => {
    const today = dayjs();
    return schedules.filter(schedule => 
      dayjs(schedule.start_time).isSame(today, 'day')
    );
  };

  const todaySchedules = getTodaySchedules();

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <div style={{ marginBottom: '24px' }}>
          <Row justify="space-between" align="middle">
            <Col>
              <Title level={2} style={{ margin: 0 }}>
                <CalendarOutlined style={{ marginRight: '8px' }} />
                日程安排
              </Title>
            </Col>
            <Col>
              <Space>
                <Button
                  type={viewMode === 'calendar' ? 'primary' : 'default'}
                  onClick={() => setViewMode('calendar')}
                >
                  日历视图
                </Button>
                <Button
                  type={viewMode === 'list' ? 'primary' : 'default'}
                  onClick={() => setViewMode('list')}
                >
                  列表视图
                </Button>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => openModal()}
                >
                  添加日程
                </Button>
              </Space>
            </Col>
          </Row>
        </div>

        {/* 今日日程概览 */}
        {todaySchedules.length > 0 && (
          <Card size="small" style={{ marginBottom: '24px' }}>
            <Title level={4}>今日日程</Title>
            <List
              size="small"
              dataSource={todaySchedules}
              renderItem={schedule => (
                <List.Item>
                  <Space>
                    <div
                      style={{
                        width: '12px',
                        height: '12px',
                        borderRadius: '50%',
                        backgroundColor: schedule.color,
                      }}
                    />
                    <Text strong>{schedule.title}</Text>
                    <Text type="secondary">
                      {dayjs(schedule.start_time).format('HH:mm')} - {dayjs(schedule.end_time).format('HH:mm')}
                    </Text>
                    {schedule.location && (
                      <Text type="secondary">
                        <EnvironmentOutlined /> {schedule.location}
                      </Text>
                    )}
                  </Space>
                </List.Item>
              )}
            />
          </Card>
        )}

        {/* 日历视图 */}
        {viewMode === 'calendar' && (
          <Calendar
            value={selectedDate}
            onChange={setSelectedDate}
            dateCellRender={dateCellRender}
            locale={locale}
            onSelect={(date) => {
              setSelectedDate(date);
            }}
          />
        )}

        {/* 列表视图 */}
        {viewMode === 'list' && (
          <List
            loading={loading}
            dataSource={schedules}
            renderItem={schedule => (
              <List.Item
                actions={[
                  <Button
                    type="text"
                    icon={<EditOutlined />}
                    onClick={() => openModal(schedule)}
                  />,
                  <Popconfirm
                    title="确定要删除这个日程吗？"
                    onConfirm={() => handleDelete(schedule.id)}
                    okText="确定"
                    cancelText="取消"
                  >
                    <Button
                      type="text"
                      danger
                      icon={<DeleteOutlined />}
                    />
                  </Popconfirm>,
                ]}
              >
                <List.Item.Meta
                  avatar={
                    <div
                      style={{
                        width: '16px',
                        height: '16px',
                        borderRadius: '50%',
                        backgroundColor: schedule.color,
                      }}
                    />
                  }
                  title={
                    <Space>
                      <Text strong>{schedule.title}</Text>
                      {schedule.is_all_day && <Tag color="blue">全天</Tag>}
                    </Space>
                  }
                  description={
                    <Space direction="vertical" size="small">
                      <Space>
                        <ClockCircleOutlined />
                        <Text>
                          {dayjs(schedule.start_time).format('YYYY-MM-DD HH:mm')} - {dayjs(schedule.end_time).format('HH:mm')}
                        </Text>
                      </Space>
                      {schedule.description && <Text type="secondary">{schedule.description}</Text>}
                      {schedule.location && (
                        <Space>
                          <EnvironmentOutlined />
                          <Text type="secondary">{schedule.location}</Text>
                        </Space>
                      )}
                    </Space>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </Card>

      {/* 创建/编辑模态框 */}
      <Modal
        title={editingSchedule ? '编辑日程' : '创建日程'}
        open={modalVisible}
        onCancel={closeModal}
        onOk={() => form.submit()}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="title"
            label="标题"
            rules={[{ required: true, message: '请输入日程标题' }]}
          >
            <Input placeholder="请输入日程标题" />
          </Form.Item>

          <Form.Item
            name="description"
            label="描述"
          >
            <TextArea rows={3} placeholder="请输入日程描述" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="start_time"
                label="开始时间"
                rules={[{ required: true, message: '请选择开始时间' }]}
              >
                <DatePicker
                  showTime
                  style={{ width: '100%' }}
                  placeholder="选择开始时间"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="end_time"
                label="结束时间"
                rules={[{ required: true, message: '请选择结束时间' }]}
              >
                <DatePicker
                  showTime
                  style={{ width: '100%' }}
                  placeholder="选择结束时间"
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="is_all_day"
            label="全天事件"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            name="location"
            label="地点"
          >
            <Input placeholder="请输入地点" />
          </Form.Item>

          <Form.Item
            name="color"
            label="颜色"
            initialValue="#1890ff"
          >
            <Select>
              {colorOptions.map(option => (
                <Option key={option.value} value={option.value}>
                  <Space>
                    <div
                      style={{
                        width: '12px',
                        height: '12px',
                        borderRadius: '50%',
                        backgroundColor: option.color,
                      }}
                    />
                    {option.label}
                  </Space>
                </Option>
              ))}
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ScheduleManager;
