import { useState, useEffect, useCallback } from 'react'
import {
  Table, Button, Modal, Form, Input, Select, Space, message, Typography, Tag, Popconfirm,
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons'
import { useAuth } from '../store/AuthContext'
import api from '../services/api'

const categories = ['Semis', 'Long', 'Flat', 'ByProduct', 'Service']
const groups = ['Bloom', 'Billet', 'TMT', 'WireRod', 'Angle', 'Channel', ' Beam']

export default function Products() {
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
      const [prodRes, uomRes] = await Promise.all([
        api.get('/products'),
        api.get('/uom'),
      ])
      setData(prodRes.data)
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
        await api.put(`/products/${editing.product_id}`, values)
        message.success('Product updated')
      } else {
        await api.post('/products', values)
        message.success('Product created')
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
      await api.delete(`/products/${id}`)
      message.success('Product deactivated')
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
    { title: 'Code', dataIndex: 'product_code', key: 'product_code', width: 100 },
    { title: 'Name', dataIndex: 'product_name', key: 'product_name' },
    { title: 'Category', dataIndex: 'product_category', key: 'product_category', width: 100,
      render: (v) => <Tag>{v}</Tag>,
    },
    { title: 'Group', dataIndex: 'product_group', key: 'product_group', width: 100 },
    { title: 'Grade', dataIndex: 'grade', key: 'grade', width: 100 },
    { title: 'Size', dataIndex: 'size_spec', key: 'size_spec', width: 90 },
    { title: 'Active', dataIndex: 'is_active', key: 'is_active', width: 80,
      render: (v) => <Tag color={v ? 'green' : 'red'}>{v ? 'Yes' : 'No'}</Tag>,
    },
    {
      title: 'Actions', key: 'actions', width: 120,
      render: (_, r) => user?.role !== 'report_viewer' && (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(r)} />
          <Popconfirm title="Deactivate this product?" onConfirm={() => handleDelete(r.product_id)}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Typography.Title level={4} style={{ margin: 0 }}>Product Catalog</Typography.Title>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetch}>Refresh</Button>
          {user?.role !== 'report_viewer' && <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>Add Product</Button>}
        </Space>
      </div>

      <Table rowKey="product_id" columns={columns} dataSource={data} loading={loading} pagination={{ pageSize: 20 }} size="middle" />

      <Modal
        title={editing ? 'Edit Product' : 'Add Product'}
        open={modalOpen}
        onCancel={() => { setModalOpen(false); setEditing(null); form.resetFields() }}
        onOk={() => form.submit()}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="product_code" label="Code" rules={[{ required: true }]} style={{ width: '50%' }}>
              <Input />
            </Form.Item>
            <Form.Item name="product_name" label="Name" rules={[{ required: true }]} style={{ width: '50%' }}>
              <Input />
            </Form.Item>
          </Space>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="product_category" label="Category" rules={[{ required: true }]} style={{ width: '50%' }}>
              <Select>{categories.map((c) => <Select.Option key={c} value={c}>{c}</Select.Option>)}</Select>
            </Form.Item>
            <Form.Item name="product_group" label="Group" style={{ width: '50%' }}>
              <Select allowClear>{groups.map((g) => <Select.Option key={g} value={g}>{g}</Select.Option>)}</Select>
            </Form.Item>
          </Space>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="grade" label="Grade" style={{ width: '50%' }}>
              <Input />
            </Form.Item>
            <Form.Item name="size_spec" label="Size Spec" style={{ width: '50%' }}>
              <Input />
            </Form.Item>
          </Space>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="standard" label="Standard" style={{ width: '50%' }}>
              <Input />
            </Form.Item>
            <Form.Item name="uom_id" label="UOM" style={{ width: '50%' }}>
              <Select allowClear placeholder="Select UOM">
                {uoms.map((u) => <Select.Option key={u.uom_id} value={u.uom_id}>{u.uom_code}</Select.Option>)}
              </Select>
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
