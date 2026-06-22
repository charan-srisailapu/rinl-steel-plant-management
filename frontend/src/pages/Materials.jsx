import { useState, useEffect, useCallback } from 'react'
import {
  Table, Button, Modal, Form, Input, Select, InputNumber, Space, message, Typography, Tag, Popconfirm,
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons'
import { useAuth } from '../store/AuthContext'
import api from '../services/api'

const types = ['Raw', 'Consumable', 'Spare', 'Fuel', 'Refractory', 'Chemical', 'Packaging']
const groups = ['IronOre', 'Coal', 'FerroAlloy', 'Flux', 'Coke', 'Electrode', 'Brick', 'Gas', 'SparePart', 'Other']

export default function Materials() {
  const { user } = useAuth()
  const [data, setData] = useState([])
  const [uoms, setUoms] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form] = Form.useForm()

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const [matRes, uomRes] = await Promise.all([
        api.get('/materials'),
        api.get('/uom'),
      ])
      setData(matRes.data)
      setUoms(uomRes.data || [])
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
        await api.put(`/materials/${editing.material_id}`, values)
        message.success('Material updated')
      } else {
        await api.post('/materials', values)
        message.success('Material created')
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
      await api.delete(`/materials/${id}`)
      message.success('Material deactivated')
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
    { title: 'Code', dataIndex: 'material_code', key: 'material_code', width: 100 },
    { title: 'Name', dataIndex: 'material_name', key: 'material_name' },
    { title: 'Type', dataIndex: 'material_type', key: 'material_type', width: 110,
      render: (v) => <Tag color={v === 'Raw' ? 'blue' : v === 'Fuel' ? 'orange' : 'default'}>{v}</Tag>,
    },
    { title: 'Group', dataIndex: 'material_group', key: 'material_group', width: 100 },
    { title: 'Reorder Level', dataIndex: 'reorder_level', key: 'reorder_level', width: 120,
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
          <Popconfirm title="Deactivate this material?" onConfirm={() => handleDelete(r.material_id)}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Typography.Title level={4} style={{ margin: 0 }}>Materials Master</Typography.Title>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetch}>Refresh</Button>
          {user?.role !== 'report_viewer' && <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>Add Material</Button>}
        </Space>
      </div>

      <Table rowKey="material_id" columns={columns} dataSource={data} loading={loading} pagination={{ pageSize: 20 }} size="middle" />

      <Modal
        title={editing ? 'Edit Material' : 'Add Material'}
        open={modalOpen}
        onCancel={() => { setModalOpen(false); setEditing(null); form.resetFields() }}
        onOk={() => form.submit()}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="material_code" label="Code" rules={[{ required: true }]} style={{ width: '50%' }}>
              <Input />
            </Form.Item>
            <Form.Item name="material_name" label="Name" rules={[{ required: true }]} style={{ width: '50%' }}>
              <Input />
            </Form.Item>
          </Space>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="material_type" label="Type" rules={[{ required: true }]} style={{ width: '50%' }}>
              <Select>{types.map((t) => <Select.Option key={t} value={t}>{t}</Select.Option>)}</Select>
            </Form.Item>
            <Form.Item name="material_group" label="Group" style={{ width: '50%' }}>
              <Select allowClear>{groups.map((g) => <Select.Option key={g} value={g}>{g}</Select.Option>)}</Select>
            </Form.Item>
          </Space>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="uom_id" label="UOM" style={{ width: '50%' }}>
              <Select allowClear placeholder="Select UOM">
                {uoms.map((u) => <Select.Option key={u.uom_id} value={u.uom_id}>{u.uom_code}</Select.Option>)}
              </Select>
            </Form.Item>
            <Form.Item name="reorder_level" label="Reorder Level" style={{ width: '50%' }}>
              <InputNumber style={{ width: '100%' }} min={0} />
            </Form.Item>
          </Space>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="lead_time_days" label="Lead Time (Days)" style={{ width: '50%' }}>
              <InputNumber style={{ width: '100%' }} min={1} />
            </Form.Item>
          </Space>
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
