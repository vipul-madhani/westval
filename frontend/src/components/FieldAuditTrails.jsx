import React, { useState, useEffect } from 'react';
import {
  Table, Button, Modal, Form, Input, Select, Tag, Space, Tabs,
  Card, Divider, Timeline, Badge, Spin, message, Popconfirm, DatePicker, InputNumber
} from 'antd';
import { LockOutlined, CheckCircleOutlined, FileTextOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import axios from 'axios';

const FieldAuditTrails = () => {
  const [activeTab, setActiveTab] = useState('audit');
  const [auditLogs, setAuditLogs] = useState([]);
  const [changeRequests, setChangeRequests] = useState([]);
  const [comments, setComments] = useState([]);
  const [risks, setRisks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [entityType, setEntityType] = useState('validation');
  const [entityId, setEntityId] = useState('');

  // Fetch audit logs
  const fetchAuditLogs = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`/api/audit/logs/${entityType}/${entityId}`);
      setAuditLogs(res.data.logs || []);
      message.success('Audit logs loaded');
    } catch (error) {
      message.error('Failed to load audit logs');
    } finally {
      setLoading(false);
    }
  };

  // Verify audit trail integrity
  const verifyTrail = async () => {
    try {
      const res = await axios.get(`/api/audit/verify/${entityType}/${entityId}`);
      if (res.data.valid) {
        message.success('✓ Audit trail integrity verified');
      } else {
        message.error(`✗ Integrity failed: ${res.data.message}`);
      }
    } catch (error) {
      message.error('Verification failed');
    }
  };

  // Create change request
  const createChangeRequest = async (values) => {
    try {
      const res = await axios.post('/api/audit/changes', {
        title: values.title,
        description: values.description,
        change_type: values.changeType,
        priority: values.priority
      });
      message.success(`Change Request ${res.data.change_number} created`);
      setModalVisible(false);
      fetchChangeRequests();
    } catch (error) {
      message.error('Failed to create change request');
    }
  };

  // Fetch change requests
  const fetchChangeRequests = async () => {
    try {
      const res = await axios.get('/api/audit/changes/pending');
      setChangeRequests(res.data.changes || []);
    } catch (error) {
      message.error('Failed to load change requests');
    }
  };

  // Create risk assessment
  const createRiskAssessment = async (values) => {
    try {
      const res = await axios.post('/api/audit/risks', {
        validation_id: parseInt(entityId),
        description: values.description,
        category: values.category,
        severity: values.severity,
        probability: values.probability
      });
      message.success(`Risk ${res.data.risk_number} (RPN: ${res.data.rpn}) created`);
      fetchRisks();
    } catch (error) {
      message.error('Failed to create risk');
    }
  };

  // Fetch risks
  const fetchRisks = async () => {
    try {
      const res = await axios.get(`/api/audit/risks/validation/${entityId}/high`);
      setRisks(res.data.risks || []);
    } catch (error) {
      message.error('Failed to load risks');
    }
  };

  // Audit logs columns
  const auditColumns = [
    { title: 'Field', dataIndex: 'field_name', key: 'field_name', width: 150 },
    {
      title: 'Old Value',
      dataIndex: 'old_value',
      key: 'old_value',
      render: (text) => <code style={{ fontSize: '11px' }}>{text?.substring(0, 50)}...</code>
    },
    {
      title: 'New Value',
      dataIndex: 'new_value',
      key: 'new_value',
      render: (text) => <code style={{ fontSize: '11px' }}>{text?.substring(0, 50)}...</code>
    },
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (date) => new Date(date).toLocaleString(),
      width: 180
    },
    {
      title: 'Status',
      dataIndex: 'approval_status',
      key: 'approval_status',
      render: (status) => (
        <Tag color={status === 'approved' ? 'green' : status === 'pending' ? 'orange' : 'red'}>
          {status.toUpperCase()}
        </Tag>
      )
    },
    {
      title: 'Change Reason',
      dataIndex: 'change_reason',
      key: 'change_reason'
    }
  ];

  // Change requests columns
  const crColumns = [
    { title: 'CR Number', dataIndex: 'number', key: 'number', width: 120 },
    { title: 'Title', dataIndex: 'title', key: 'title' },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === 'closed' ? 'green' : status === 'draft' ? 'blue' : 'orange'}>
          {status.toUpperCase()}
        </Tag>
      )
    }
  ];

  // Risks columns
  const riskColumns = [
    { title: 'Risk ID', dataIndex: 'risk_id', key: 'risk_id', width: 100 },
    { title: 'Description', dataIndex: 'description', key: 'description' },
    {
      title: 'RPN',
      dataIndex: 'rpn',
      key: 'rpn',
      render: (rpn) => (
        <Badge
          count={rpn}
          style={{
            backgroundColor: rpn >= 100 ? '#ff4d4f' : rpn >= 50 ? '#faad14' : '#52c41a'
          }}
        />
      )
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === 'closed' ? 'green' : status === 'mitigated' ? 'blue' : 'red'}>
          {status.toUpperCase()}
        </Tag>
      )
    }
  ];

  return (
    <div style={{ padding: '20px' }}>
      <Card title="Field Audit Trails & Change Management" extra={<LockOutlined />}>
        <Divider>Entity Selection</Divider>
        <Form layout="inline" style={{ marginBottom: '20px' }}>
          <Form.Item label="Entity Type">
            <Select value={entityType} onChange={setEntityType} style={{ width: 150 }}>
              <Select.Option value="validation">Validation</Select.Option>
              <Select.Option value="protocol">Protocol</Select.Option>
              <Select.Option value="test">Test</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item label="Entity ID">
            <InputNumber value={entityId} onChange={setEntityId} style={{ width: 150 }} />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" onClick={fetchAuditLogs} loading={loading}>
                Load Audit Logs
              </Button>
              <Popconfirm
                title="Verify Integrity"
                description="This will verify the SHA-256 hash chain integrity. Continue?"
                onConfirm={verifyTrail}
              >
                <Button icon={<CheckCircleOutlined />}>Verify Trail</Button>
              </Popconfirm>
            </Space>
          </Form.Item>
        </Form>

        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: 'audit',
              label: 'Audit Logs',
              children: (
                <Spin spinning={loading}>
                  <Table
                    columns={auditColumns}
                    dataSource={auditLogs}
                    pagination={{ pageSize: 10 }}
                    rowKey="id"
                  />
                </Spin>
              )
            },
            {
              key: 'changes',
              label: 'Change Requests',
              children: (
                <>
                  <Button type="primary" style={{ marginBottom: '15px' }} onClick={() => setModalVisible(true)}>
                    Create Change Request
                  </Button>
                  <Table columns={crColumns} dataSource={changeRequests} rowKey="id" />
                </>
              )
            },
            {
              key: 'risks',
              label: 'Risk Assessments',
              children: (
                <Table columns={riskColumns} dataSource={risks} pagination={{ pageSize: 10 }} rowKey="id" />
              )
            }
          ]}
        />
      </Card>

      <Modal
        title="Create Change Request"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
      >
        <Form layout="vertical" onFinish={createChangeRequest}>
          <Form.Item name="title" label="Title" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="description" label="Description" rules={[{ required: true }]}>
            <Input.TextArea rows={4} />
          </Form.Item>
          <Form.Item name="changeType" label="Change Type" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="minor">Minor</Select.Option>
              <Select.Option value="major">Major</Select.Option>
              <Select.Option value="emergency">Emergency</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="priority" label="Priority" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="low">Low</Select.Option>
              <Select.Option value="medium">Medium</Select.Option>
              <Select.Option value="high">High</Select.Option>
              <Select.Option value="critical">Critical</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              Create
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default FieldAuditTrails;
