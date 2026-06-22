import { useState, useEffect, useCallback } from 'react'
import { Table, Button, Modal, Form, Input, Select, Space, message, Typography, Tag, Popconfirm, Rate } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons'
import { useAuth } from '../store/AuthContext'
import api from '../services/api'

export default function Suppliers() {
  const { user } = useAuth()
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [materialModalOpen, setMaterialModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [materials, setMaterials] = useState([])
  const [form] = Form.useForm()
  const [matForm] = Form.useForm()
  const [selectedSupplier, setSelectedSupplier] = useState(null)

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const res = await api.get('/suppliers')
      setData(res.data)
    } catch {
      message.error('Failed to fetch suppliers')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetch() }, [fetch])

  const handleSubmit = async (values) => {
    try {
      if (editing) {
        await api.put(`/suppliers/${editing.supplier_id}`, values)
        message.success('Supplier updated')
      } else {
        await api.post('/suppliers', values)
        message.success('Supplier created')
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
      await api.delete(`/suppliers/${id}`)
      message.success('Supplier deactivated')
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

  const openMaterials = async (supplier) => {
    setSelectedSupplier(supplier)
    try {
      const res = await api.get(`/suppliers/${supplier.supplier_id}/materials`)
      setMaterials(res.data)
    } catch {
      setMaterials([])
    }
    setMaterialModalOpen(true)
  }

  const columns = [
    { title: 'Code', dataIndex: 'supplier_code', key: 'supplier_code', width: 100 },
    { title: 'Name', dataIndex: 'supplier_name', key: 'supplier_name' },
    { title: 'Contact', dataIndex: 'contact_person', key: 'contact_person', width: 130 },
    { title: 'City', dataIndex: 'city', key: 'city', width: 100 },
    { title: 'Rating', dataIndex: 'rating', key: 'rating', width: 120,
      render: (v) => v ? <Rate disabled defaultValue={v} allowHalf /> : '-',
    },
    { title: 'Active', dataIndex: 'is_active', key: 'is_active', width: 80,
      render: (v) => <Tag color={v ? 'green' : 'red'}>{v ? 'Yes' : 'No'}</Tag>,
    },
    {
      title: 'Actions', key: 'actions', width: 180,
      render: (_, r) => (
        <Space>
          <Button size="small" onClick={() => openMaterials(r)}>Materials</Button>
          {user?.role !== 'report_viewer' && (
            <>
              <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(r)} />
              <Popconfirm title="Deactivate?" onConfirm={() => handleDelete(r.supplier_id)}>
                <Button size="small" danger icon={<DeleteOutlined />} />
              </Popconfirm>
            </>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Typography.Title level={4} style={{ margin: 0 }}>Suppliers</Typography.Title>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetch}>Refresh</Button>
          {user?.role !== 'report_viewer' && (
            <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>Add Supplier</Button>
          )}
        </Space>
      </div>

      <Table rowKey="supplier_id" columns={columns} dataSource={data} loading={loading} pagination={{ pageSize: 20 }} size="middle" />

      <Modal title={editing ? 'Edit Supplier' : 'Add Supplier'} open={modalOpen}
        onCancel={() => { setModalOpen(false); setEditing(null); form.resetFields() }}
        onOk={() => form.submit()} width={700} destroyOnClose>
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="supplier_code" label="Code" rules={[{ required: true }]} style={{ width: '50%' }}>
              <Input />
            </Form.Item>
            <Form.Item name="supplier_name" label="Name" rules={[{ required: true }]} style={{ width: '50%' }}>
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
            <Form.Item name="rating" label="Rating (1-5)" style={{ width: '50%' }}>
              <Input type="number" min={1} max={5} step={0.1} />
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

      <Modal title={`Materials supplied by ${selectedSupplier?.supplier_name || ''}`}
        open={materialModalOpen} onCancel={() => setMaterialModalOpen(false)}
        footer={null} width={600}>
        <Table rowKey="supplier_material_id" dataSource={materials}
          columns={[
            { title: 'Material', dataIndex: 'material_name', key: 'material_name' },
            { title: 'Unit Price', dataIndex: 'unit_price', key: 'unit_price',
              render: (v) => v ? `₹${v.toLocaleString()}` : '-',
            },
            { title: 'Quality', dataIndex: 'quality_rating', key: 'quality_rating',
              render: (v) => v ? <Rate disabled defaultValue={v} allowHalf /> : '-',
            },
            { title: 'Preferred', dataIndex: 'is_preferred', key: 'is_preferred',
              render: (v) => v ? <Tag color="blue">Yes</Tag> : <Tag>No</Tag>,
            },
          ]}
          pagination={false} size="small" />
      </Modal>
    </div>
  )
}
