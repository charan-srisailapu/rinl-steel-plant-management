import { useState, useEffect, useCallback } from 'react'
import { Table, Button, Modal, Form, Input, Select, DatePicker, Space, message, Typography, Tag } from 'antd'
import { PlusOutlined, ReloadOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { useAuth } from '../store/AuthContext'
import api from '../services/api'

export default function MaterialReceipts() {
  const { user } = useAuth()
  const [data, setData] = useState([])
  const [suppliers, setSuppliers] = useState([])
  const [materials, setMaterials] = useState([])
  const [employees, setEmployees] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [form] = Form.useForm()

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const [recRes, supRes, matRes, empRes] = await Promise.all([
        api.get('/suppliers/receipts'),
        api.get('/suppliers'),
        api.get('/materials'),
        api.get('/employees'),
      ])
      setData(recRes.data)
      setSuppliers(supRes.data)
      setMaterials(matRes.data)
      setEmployees(empRes.data)
    } catch {
      message.error('Failed to fetch receipts')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetch() }, [fetch])

  const handleSubmit = async (values) => {
    const payload = {
      ...values,
      receipt_date: dayjs(values.receipt_date).format('YYYY-MM-DD'),
    }
    try {
      await api.post('/suppliers/receipts', payload)
      message.success('Receipt recorded')
      setModalOpen(false)
      form.resetFields()
      fetch()
    } catch (err) {
      message.error(err.response?.data?.detail || 'Operation failed')
    }
  }

  const columns = [
    { title: 'Date', dataIndex: 'receipt_date', key: 'receipt_date', width: 110 },
    { title: 'Invoice', dataIndex: 'invoice_no', key: 'invoice_no', width: 120 },
    { title: 'Supplier', dataIndex: 'supplier_name', key: 'supplier_name' },
    { title: 'Material', dataIndex: 'material_name', key: 'material_name' },
    { title: 'Qty', dataIndex: 'quantity', key: 'quantity', width: 100,
      render: (v) => v?.toLocaleString(),
    },
    { title: 'Unit Price', dataIndex: 'unit_price', key: 'unit_price', width: 100,
      render: (v) => v ? `₹${v.toLocaleString()}` : '-',
    },
    { title: 'Quality', dataIndex: 'quality_score', key: 'quality_score', width: 90,
      render: (v) => v ? `${v}%` : '-',
    },
    { title: 'Received By', dataIndex: 'receiver_name', key: 'receiver_name', width: 120 },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Typography.Title level={4} style={{ margin: 0 }}>Material Receipts</Typography.Title>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetch}>Refresh</Button>
          {user?.role !== 'report_viewer' && (
            <Button type="primary" icon={<PlusOutlined />} onClick={() => { form.resetFields(); setModalOpen(true) }}>
              Record Receipt
            </Button>
          )}
        </Space>
      </div>

      <Table rowKey="receipt_id" columns={columns} dataSource={data} loading={loading}
        pagination={{ pageSize: 20 }} size="middle" />

      <Modal title="Record Material Receipt" open={modalOpen}
        onCancel={() => { setModalOpen(false); form.resetFields() }}
        onOk={() => form.submit()} width={600} destroyOnClose>
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="receipt_date" label="Receipt Date" rules={[{ required: true }]} style={{ width: '50%' }}>
              <DatePicker style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item name="invoice_no" label="Invoice No" style={{ width: '50%' }}>
              <Input />
            </Form.Item>
          </Space>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="supplier_id" label="Supplier" rules={[{ required: true }]} style={{ width: '50%' }}>
              <Select showSearch filterOption={(input, option) => option.children?.toLowerCase().includes(input.toLowerCase())}>
                {suppliers.filter(s => s.is_active).map((s) => (
                  <Select.Option key={s.supplier_id} value={s.supplier_id}>{s.supplier_name}</Select.Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item name="material_id" label="Material" rules={[{ required: true }]} style={{ width: '50%' }}>
              <Select showSearch filterOption={(input, option) => option.children?.toLowerCase().includes(input.toLowerCase())}>
                {materials.filter(m => m.is_active).map((m) => (
                  <Select.Option key={m.material_id} value={m.material_id}>{m.material_name}</Select.Option>
                ))}
              </Select>
            </Form.Item>
          </Space>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="quantity" label="Quantity" rules={[{ required: true }]} style={{ width: '50%' }}>
              <Input type="number" step="0.01" />
            </Form.Item>
            <Form.Item name="unit_price" label="Unit Price" style={{ width: '50%' }}>
              <Input type="number" step="0.01" />
            </Form.Item>
          </Space>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="quality_score" label="Quality Score %" style={{ width: '50%' }}>
              <Input type="number" min={0} max={100} />
            </Form.Item>
            <Form.Item name="received_by" label="Received By" style={{ width: '50%' }}>
              <Select allowClear showSearch filterOption={(input, option) => option.children?.toLowerCase().includes(input.toLowerCase())}>
                {employees.filter(e => e.is_active).map((e) => (
                  <Select.Option key={e.emp_id} value={e.emp_id}>{e.full_name}</Select.Option>
                ))}
              </Select>
            </Form.Item>
          </Space>
          <Form.Item name="notes" label="Notes">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
