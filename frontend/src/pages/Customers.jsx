import { useState, useEffect, useCallback } from 'react'
import { Table, Button, Modal, Form, Input, Select, Space, message, Typography, Tag, Popconfirm } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons'
import { useAuth } from '../store/AuthContext'
import api from '../services/api'

export default function Customers() {
  const { user } = useAuth()
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form] = Form.useForm()

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const res = await api.get('/dispatch/customers')
      setData(res.data)
    } catch {
      message.error('Failed to fetch customers')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetch() }, [fetch])

  const handleSubmit = async (values) => {
    try {
      if (editing) {
        await api.put(`/dispatch/customers/${editing.customer_id}`, values)
        message.success('Customer updated')
      } else {
        await api.post('/dispatch/customers', values)
        message.success('Customer created')
      }
      setModalOpen(false)
      form.resetFields()
      setEditing(null)
      fetch()
    } catch (err) {
      message.error(err.response?.data?.detail || 'Operation failed')
    }
  }

  const handleDelete = async (id) => {
    try {
      await api.delete(`/dispatch/customers/${id}`)
      message.success('Customer deactivated')
      fetch()
    } catch {
      message.error('Failed to deactivate')
    }
  }

  const openEdit = (record) => {
    setEditing(record)
    form.setFieldsValue(record)
    setModalOpen(true)
  }

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    setModalOpen(true)
  }

  const columns = [
    { title: 'Code', dataIndex: 'customer_code', key: 'customer_code', width: 100 },
    { title: 'Name', dataIndex: 'customer_name', key: 'customer_name' },
    { title: 'Contact', dataIndex: 'contact_person', key: 'contact_person', width: 130 },
    { title: 'City', dataIndex: 'city', key: 'city', width: 100 },
    { title: 'Credit Limit', dataIndex: 'credit_limit', key: 'credit_limit', width: 110,
      render: (v) => v ? `₹${v.toLocaleString()}` : '-',
    },
    { title: 'Active', dataIndex: 'is_active', key: 'is_active', width: 80,
      render: (v) => <Tag color={v ? 'green' : 'red'}>{v ? 'Yes' : 'No'}</Tag>,
    },
    {
      title: 'Actions', key: 'actions', width: 120,
      render: (_, r) => user?.role !== 'report_viewer' && (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(r)} />
          <Popconfirm title="Deactivate this customer?" onConfirm={() => handleDelete(r.customer_id)}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Typography.Title level={4} style={{ margin: 0 }}>Customers</Typography.Title>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetch}>Refresh</Button>
          {user?.role !== 'report_viewer' && (
            <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>Add Customer</Button>
          )}
        </Space>
      </div>

      <Table rowKey="customer_id" columns={columns} dataSource={data} loading={loading}
        pagination={{ pageSize: 20 }} size="middle" />

      <Modal title={editing ? 'Edit Customer' : 'Add Customer'} open={modalOpen}
        onCancel={() => { setModalOpen(false); setEditing(null); form.resetFields() }}
        onOk={() => form.submit()} width={700} destroyOnClose>
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="customer_code" label="Code" rules={[{ required: true }]} style={{ width: '50%' }}>
              <Input />
            </Form.Item>
            <Form.Item name="customer_name" label="Name" rules={[{ required: true }]} style={{ width: '50%' }}>
              <Input />
            </Form.Item>
          </Space>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="contact_person" label="Contact Person" style={{ width: '50%' }}>
              <Input />
            </Form.Item>
            <Form.Item name="email" label="Email" style={{ width: '50%' }}>
              <Input type="email" />
            </Form.Item>
          </Space>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="phone" label="Phone" style={{ width: '50%' }}>
              <Input />
            </Form.Item>
            <Form.Item name="gst_no" label="GST No" style={{ width: '50%' }}>
              <Input />
            </Form.Item>
          </Space>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="city" label="City" style={{ width: '50%' }}>
              <Input />
            </Form.Item>
            <Form.Item name="state" label="State" style={{ width: '50%' }}>
              <Input />
            </Form.Item>
          </Space>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="pincode" label="Pincode" style={{ width: '50%' }}>
              <Input />
            </Form.Item>
            <Form.Item name="credit_limit" label="Credit Limit" style={{ width: '50%' }}>
              <Input type="number" step="0.01" />
            </Form.Item>
          </Space>
          <Form.Item name="address" label="Address">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="is_active" label="Active">
            <Select>
              <Select.Option value={true}>Active</Select.Option>
              <Select.Option value={false}>Inactive</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
