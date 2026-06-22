import { useState, useEffect, useCallback } from 'react'
import {
  Table, Button, Modal, Form, Input, Select, InputNumber, Space, message, Typography, Tag, Popconfirm,
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons'
import { useAuth } from '../store/AuthContext'
import api from '../services/api'

const unitTypes = ['Furnace', 'Converter', 'Caster', 'Mill', 'Kiln', 'Boiler', 'Turbine', 'Crane', 'Other']

export default function Units() {
  const { user } = useAuth()
  const [data, setData] = useState([])
  const [depts, setDepts] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form] = Form.useForm()

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const [unitsRes, deptsRes] = await Promise.all([
        api.get('/units'),
        api.get('/departments'),
      ])
      setData(unitsRes.data)
      setDepts(deptsRes.data)
    } catch {
      message.error('Failed to fetch data')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetch() }, [fetch])

  const handleSubmit = async (values) => {
    try {
      if (editing) {
        await api.put(`/units/${editing.unit_id}`, values)
        message.success('Unit updated')
      } else {
        await api.post('/units', values)
        message.success('Unit created')
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
      await api.delete(`/units/${id}`)
      message.success('Unit deactivated')
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
    { title: 'Code', dataIndex: 'unit_code', key: 'unit_code', width: 100 },
    { title: 'Name', dataIndex: 'unit_name', key: 'unit_name' },
    { title: 'Type', dataIndex: 'unit_type', key: 'unit_type', width: 110 },
    {
      title: 'Capacity (TPA)', dataIndex: 'capacity_tpa', key: 'capacity_tpa', width: 140,
      render: (v) => v ? v.toLocaleString() : '-',
    },
    { title: 'Active', dataIndex: 'is_active', key: 'is_active', width: 80,
      render: (v) => <Tag color={v ? 'green' : 'red'}>{v ? 'Yes' : 'No'}</Tag>,
    },
    {
      title: 'Actions', key: 'actions', width: 120,
      render: (_, r) => user?.role !== 'report_viewer' && (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(r)} />
          <Popconfirm title="Deactivate this unit?" onConfirm={() => handleDelete(r.unit_id)}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Typography.Title level={4} style={{ margin: 0 }}>Production Units</Typography.Title>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetch}>Refresh</Button>
          {user?.role !== 'report_viewer' && <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>Add Unit</Button>}
        </Space>
      </div>

      <Table rowKey="unit_id" columns={columns} dataSource={data} loading={loading} pagination={{ pageSize: 20 }} size="middle" />

      <Modal
        title={editing ? 'Edit Unit' : 'Add Unit'}
        open={modalOpen}
        onCancel={() => { setModalOpen(false); setEditing(null); form.resetFields() }}
        onOk={() => form.submit()}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="unit_code" label="Code" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="unit_name" label="Name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="dept_id" label="Department" rules={[{ required: true }]}>
            <Select>
              {depts.map((d) => (
                <Select.Option key={d.dept_id} value={d.dept_id}>{d.dept_code} - {d.dept_name}</Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="unit_type" label="Type" rules={[{ required: true }]}>
            <Select>
              {unitTypes.map((t) => <Select.Option key={t} value={t}>{t}</Select.Option>)}
            </Select>
          </Form.Item>
          <Form.Item name="capacity_tpa" label="Capacity (TPA)">
            <InputNumber style={{ width: '100%' }} min={0} />
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
