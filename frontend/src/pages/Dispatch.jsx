import { useState, useEffect, useCallback } from 'react'
import { Table, Button, Modal, Form, Input, Select, DatePicker, Space, message, Typography, Tag, Popconfirm } from 'antd'
import { PlusOutlined, ReloadOutlined, EyeOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { useAuth } from '../store/AuthContext'
import api from '../services/api'

export default function Dispatch() {
  const { user } = useAuth()
  const [data, setData] = useState([])
  const [customers, setCustomers] = useState([])
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [detailOpen, setDetailOpen] = useState(false)
  const [selectedDispatch, setSelectedDispatch] = useState(null)
  const [form] = Form.useForm()

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const [dispRes, custRes] = await Promise.all([
        api.get('/dispatch'),
        api.get('/dispatch/customers'),
      ])
      setData(dispRes.data)
      setCustomers(custRes.data)
    } catch {
      message.error('Failed to fetch dispatches')
    } finally {
      setLoading(false)
    }
  }, [])

  const fetchProducts = useCallback(async () => {
    try {
      const res = await api.get('/dispatch/products')
      setProducts(res.data)
    } catch {
      message.error('Failed to fetch products')
    }
  }, [])

  useEffect(() => { fetch() }, [fetch])
  useEffect(() => { fetchProducts() }, [fetchProducts])

  const handleSubmit = async (values) => {
    const items = values.items || []
    const payload = {
      ...values,
      dispatch_date: dayjs(values.dispatch_date).format('YYYY-MM-DD'),
      total_amount: items.reduce((sum, item) => sum + (item.quantity || 0) * (item.unit_price || 0), 0),
      items: items.map((item) => ({
        product_id: item.product_id,
        quantity: item.quantity,
        unit_price: item.unit_price,
      })),
    }
    try {
      await api.post('/dispatch', payload)
      message.success('Dispatch created')
      setModalOpen(false)
      form.resetFields()
      fetch()
    } catch (err) {
      message.error(err.response?.data?.detail || 'Operation failed')
    }
  }

  const updateStatus = async (id, status) => {
    try {
      await api.put(`/dispatch/${id}`, { delivery_status: status })
      message.success(`Status updated to ${status}`)
      fetch()
    } catch {
      message.error('Failed to update status')
    }
  }

  const viewDetail = (record) => {
    setSelectedDispatch(record)
    setDetailOpen(true)
  }

  const statusColors = {
    Dispatched: 'blue',
    'In Transit': 'orange',
    Delivered: 'green',
    Cancelled: 'red',
  }

  const columns = [
    { title: 'Date', dataIndex: 'dispatch_date', key: 'dispatch_date', width: 110 },
    { title: 'Invoice', dataIndex: 'invoice_no', key: 'invoice_no', width: 120 },
    { title: 'Customer', dataIndex: 'customer_name', key: 'customer_name' },
    { title: 'Mode', dataIndex: 'dispatch_mode', key: 'dispatch_mode', width: 80 },
    { title: 'Amount', dataIndex: 'total_amount', key: 'total_amount', width: 120,
      render: (v) => v ? `₹${v.toLocaleString()}` : '-',
    },
    {
      title: 'Status', dataIndex: 'delivery_status', key: 'delivery_status', width: 120,
      render: (v) => <Tag color={statusColors[v]}>{v}</Tag>,
    },
    {
      title: 'Actions', key: 'actions', width: 240,
      render: (_, r) => (
        <Space>
          <Button size="small" icon={<EyeOutlined />} onClick={() => viewDetail(r)}>View</Button>
          {user?.role !== 'report_viewer' && r.delivery_status !== 'Cancelled' && r.delivery_status !== 'Delivered' && (
            <Select size="small" value={r.delivery_status} onChange={(v) => updateStatus(r.dispatch_id, v)}
              style={{ width: 120 }}>
              <Select.Option value="Dispatched">Dispatched</Select.Option>
              <Select.Option value="In Transit">In Transit</Select.Option>
              <Select.Option value="Delivered">Delivered</Select.Option>
              <Select.Option value="Cancelled">Cancelled</Select.Option>
            </Select>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Typography.Title level={4} style={{ margin: 0 }}>Dispatch Management</Typography.Title>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetch}>Refresh</Button>
          {user?.role !== 'report_viewer' && (
            <Button type="primary" icon={<PlusOutlined />} onClick={() => { form.resetFields(); fetchProducts(); setModalOpen(true) }}>
              New Dispatch
            </Button>
          )}
        </Space>
      </div>

      <Table rowKey="dispatch_id" columns={columns} dataSource={data} loading={loading}
        pagination={{ pageSize: 20 }} size="middle" />

      <Modal title="Create Dispatch" open={modalOpen} onCancel={() => { setModalOpen(false); form.resetFields() }}
        onOk={() => form.submit()} width={800} destroyOnClose>
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="dispatch_date" label="Dispatch Date" rules={[{ required: true }]} style={{ width: '50%' }}>
              <DatePicker style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item name="invoice_no" label="Invoice No" rules={[{ required: true }]} style={{ width: '50%' }}>
              <Input />
            </Form.Item>
          </Space>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="customer_id" label="Customer" rules={[{ required: true }]} style={{ width: '50%' }}>
              <Select showSearch filterOption={(input, option) => option.children?.toLowerCase().includes(input.toLowerCase())}>
                {customers.filter(c => c.is_active).map((c) => (
                  <Select.Option key={c.customer_id} value={c.customer_id}>{c.customer_name}</Select.Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item name="dispatch_mode" label="Mode" rules={[{ required: true }]} style={{ width: '50%' }}>
              <Select>
                <Select.Option value="Road">Road</Select.Option>
                <Select.Option value="Rail">Rail</Select.Option>
                <Select.Option value="Sea">Sea</Select.Option>
              </Select>
            </Form.Item>
          </Space>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="vehicle_no" label="Vehicle No" style={{ width: '50%' }}>
              <Input />
            </Form.Item>
            <Form.Item name="driver_name" label="Driver Name" style={{ width: '50%' }}>
              <Input />
            </Form.Item>
          </Space>

          <Typography.Text strong>Dispatch Items</Typography.Text>
          <Form.List name="items">
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...rest }) => (
                  <Space key={key} style={{ width: '100%', marginTop: 8 }} align="baseline">
                    <Form.Item {...rest} name={[name, 'product_id']} rules={[{ required: true, message: 'Required' }]}>
                      <Select placeholder="Product" style={{ width: 250 }} showSearch
                        filterOption={(input, option) => option.children?.toLowerCase().includes(input.toLowerCase())}>
                        {products.filter(p => p.is_active).map((p) => (
                          <Select.Option key={p.product_id} value={p.product_id}>
                            {p.product_code} - {p.product_name}
                          </Select.Option>
                        ))}
                      </Select>
                    </Form.Item>
                    <Form.Item {...rest} name={[name, 'quantity']} rules={[{ required: true, message: 'Required' }]}>
                      <Input type="number" step="0.01" placeholder="Qty" style={{ width: 100 }} />
                    </Form.Item>
                    <Form.Item {...rest} name={[name, 'unit_price']} rules={[{ required: true, message: 'Required' }]}>
                      <Input type="number" step="0.01" placeholder="Price" style={{ width: 120 }} />
                    </Form.Item>
                    <Button type="text" danger onClick={() => remove(name)}>Remove</Button>
                  </Space>
                ))}
                <Button type="dashed" onClick={() => add()} block style={{ marginTop: 8 }}>+ Add Item</Button>
              </>
            )}
          </Form.List>

          <Form.Item name="notes" label="Notes" style={{ marginTop: 16 }}>
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>

      <Modal title={`Dispatch #${selectedDispatch?.invoice_no || ''}`} open={detailOpen}
        onCancel={() => setDetailOpen(false)} footer={null} width={700}>
        {selectedDispatch && (
          <div>
            <Space direction="vertical" style={{ width: '100%' }} size="small">
              <Typography.Text><strong>Date:</strong> {selectedDispatch.dispatch_date}</Typography.Text>
              <Typography.Text><strong>Customer:</strong> {selectedDispatch.customer_name}</Typography.Text>
              <Typography.Text><strong>Mode:</strong> {selectedDispatch.dispatch_mode}</Typography.Text>
              <Typography.Text><strong>Vehicle:</strong> {selectedDispatch.vehicle_no || '-'}</Typography.Text>
              <Typography.Text><strong>Driver:</strong> {selectedDispatch.driver_name || '-'}</Typography.Text>
              <Typography.Text><strong>Status:</strong> <Tag color={statusColors[selectedDispatch.delivery_status]}>{selectedDispatch.delivery_status}</Tag></Typography.Text>
              <Typography.Text><strong>Total:</strong> ₹{(selectedDispatch.total_amount || 0).toLocaleString()}</Typography.Text>
              {selectedDispatch.notes && <Typography.Text><strong>Notes:</strong> {selectedDispatch.notes}</Typography.Text>}
            </Space>
            <Typography.Title level={5} style={{ marginTop: 16 }}>Items</Typography.Title>
            <Table rowKey="dispatch_item_id" dataSource={selectedDispatch.items || []} pagination={false} size="small"
              columns={[
                { title: 'Product', dataIndex: 'product_name', key: 'product_name' },
                { title: 'Code', dataIndex: 'product_code', key: 'product_code', width: 100 },
                { title: 'Qty', dataIndex: 'quantity', key: 'quantity', width: 80,
                  render: (v) => v?.toLocaleString(),
                },
                { title: 'Unit Price', dataIndex: 'unit_price', key: 'unit_price', width: 100,
                  render: (v) => `₹${v?.toLocaleString()}`,
                },
                { title: 'Total', dataIndex: 'total_price', key: 'total_price', width: 100,
                  render: (v) => `₹${(v || 0).toLocaleString()}`,
                },
              ]} />
          </div>
        )}
      </Modal>
    </div>
  )
}
