import { useState, useEffect, useCallback } from 'react'
import {
  Table, Button, Modal, Form, Input, Select, DatePicker, Space, message, Typography, Tag, Popconfirm,
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { useAuth } from '../store/AuthContext'
import api from '../services/api'

export default function Employees() {
  const { user } = useAuth()
  const [data, setData] = useState([])
  const [depts, setDepts] = useState([])
  const [units, setUnits] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form] = Form.useForm()

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const [empRes, deptRes, unitRes] = await Promise.all([
        api.get('/employees'),
        api.get('/departments'),
        api.get('/units'),
      ])
      setData(empRes.data)
      setDepts(deptRes.data)
      setUnits(unitRes.data)
    } catch {
      message.error('Failed to fetch data')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetch() }, [fetch])

  const handleSubmit = async (values) => {
    const payload = { ...values }
    if (payload.date_of_birth) payload.date_of_birth = dayjs(payload.date_of_birth).format('YYYY-MM-DD')
    if (payload.date_of_joining) payload.date_of_joining = dayjs(payload.date_of_joining).format('YYYY-MM-DD')

    try {
      if (editing) {
        await api.put(`/employees/${editing.emp_id}`, payload)
        message.success('Employee updated')
      } else {
        await api.post('/employees', payload)
        message.success('Employee created')
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
      await api.delete(`/employees/${id}`)
      message.success('Employee deactivated')
      fetch()
    } catch {
      message.error('Failed to deactivate')
    }
  }

  const openEdit = (record) => {
    setEditing(record)
    form.setFieldsValue({
      ...record,
      date_of_birth: record.date_of_birth ? dayjs(record.date_of_birth) : null,
      date_of_joining: record.date_of_joining ? dayjs(record.date_of_joining) : null,
    })
    setModalOpen(true)
  }

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    setModalOpen(true)
  }

  const columns = [
    { title: 'EMP #', dataIndex: 'emp_number', key: 'emp_number', width: 100 },
    { title: 'Name', dataIndex: 'full_name', key: 'full_name' },
    { title: 'Department', dataIndex: 'dept_id', key: 'dept_id', width: 120,
      render: (id) => depts.find((d) => d.dept_id === id)?.dept_code || id,
    },
    { title: 'Email', dataIndex: 'email', key: 'email', width: 200 },
    { title: 'Active', dataIndex: 'is_active', key: 'is_active', width: 80,
      render: (v) => <Tag color={v ? 'green' : 'red'}>{v ? 'Yes' : 'No'}</Tag>,
    },
    {
      title: 'Actions', key: 'actions', width: 120,
      render: (_, r) => user?.role !== 'report_viewer' && (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(r)} />
          <Popconfirm title="Deactivate this employee?" onConfirm={() => handleDelete(r.emp_id)}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Typography.Title level={4} style={{ margin: 0 }}>Employees</Typography.Title>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetch}>Refresh</Button>
          {user?.role !== 'report_viewer' && <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>Add Employee</Button>}
        </Space>
      </div>

      <Table rowKey="emp_id" columns={columns} dataSource={data} loading={loading} pagination={{ pageSize: 20 }} size="middle" />

      <Modal
        title={editing ? 'Edit Employee' : 'Add Employee'}
        open={modalOpen}
        onCancel={() => { setModalOpen(false); setEditing(null); form.resetFields() }}
        onOk={() => form.submit()}
        width={640}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="emp_number" label="Employee #" rules={[{ required: true }]} style={{ width: 180 }}>
              <Input />
            </Form.Item>
            <Form.Item name="full_name" label="Full Name" rules={[{ required: true }]} style={{ flex: 1 }}>
              <Input />
            </Form.Item>
          </Space>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="dept_id" label="Department" rules={[{ required: true }]} style={{ width: '50%' }}>
              <Select>
                {depts.map((d) => (
                  <Select.Option key={d.dept_id} value={d.dept_id}>{d.dept_code} - {d.dept_name}</Select.Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item name="designation_id" label="Designation" style={{ width: '50%' }}>
              <Input placeholder="e.g. Manager, Technician" />
            </Form.Item>
          </Space>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="date_of_birth" label="Date of Birth" style={{ width: '50%' }}>
              <DatePicker style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item name="date_of_joining" label="Date of Joining" style={{ width: '50%' }}>
              <DatePicker style={{ width: '100%' }} />
            </Form.Item>
          </Space>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="email" label="Email" style={{ width: '50%' }}>
              <Input />
            </Form.Item>
            <Form.Item name="phone" label="Phone" style={{ width: '50%' }}>
              <Input />
            </Form.Item>
          </Space>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="unit_id" label="Unit" style={{ width: '50%' }}>
              <Select allowClear placeholder="Assign to unit">
                {units.map((u) => (
                  <Select.Option key={u.unit_id} value={u.unit_id}>{u.unit_code} - {u.unit_name}</Select.Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item name="shift_id" label="Shift" style={{ width: '50%' }}>
              <Select allowClear placeholder="Select shift">
                {['A - Morning', 'B - Afternoon', 'C - Night', 'G - General'].map((s) => (
                  <Select.Option key={s[0]} value={s[0]}>{s}</Select.Option>
                ))}
              </Select>
            </Form.Item>
          </Space>
          <Form.Item name="address" label="Address">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="gender" label="Gender">
            <Select allowClear>
              <Select.Option value="M">Male</Select.Option>
              <Select.Option value="F">Female</Select.Option>
              <Select.Option value="O">Other</Select.Option>
            </Select>
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
