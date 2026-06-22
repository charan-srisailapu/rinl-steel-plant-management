import { useState, useEffect, useCallback } from 'react'
import { Table, Button, Tag, Space, message, Typography, Tabs, Badge, Modal, Form, Input, Select, DatePicker, InputNumber } from 'antd'
import { ReloadOutlined, WarningOutlined, PlusOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import api from '../services/api'

export default function Inventory() {
  const [stockData, setStockData] = useState([])
  const [txnData, setTxnData] = useState([])
  const [loading, setLoading] = useState(false)
  const [txnLoading, setTxnLoading] = useState(false)
  const [reorderCount, setReorderCount] = useState(0)
  const [materials, setMaterials] = useState([])
  const [modalOpen, setModalOpen] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [form] = Form.useForm()

  const fetchStock = useCallback(async () => {
    setLoading(true)
    try {
      const res = await api.get('/inventory/stock')
      setStockData(res.data)
      setReorderCount(res.data.filter((d) => d.status === 'REORDER').length)
    } catch {
      message.error('Failed to fetch stock status')
    } finally {
      setLoading(false)
    }
  }, [])

  const fetchTxns = useCallback(async () => {
    setTxnLoading(true)
    try {
      const res = await api.get('/inventory/transactions')
      setTxnData(res.data)
    } catch {
      message.error('Failed to fetch transactions')
    } finally {
      setTxnLoading(false)
    }
  }, [])

  useEffect(() => { fetchStock() }, [fetchStock])
  useEffect(() => { fetchTxns() }, [fetchTxns])

  useEffect(() => {
    api.get('/materials').then(r => setMaterials(r.data)).catch(() => {})
  }, [])

  const handleAdd = async () => {
    try {
      const values = await form.validateFields()
      setSubmitting(true)
      const payload = {
        transaction_date: values.transaction_date.format('YYYY-MM-DD'),
        material_id: values.material_id,
        transaction_type: values.transaction_type,
        quantity: values.quantity,
        reference_type: values.reference_type || null,
        remarks: values.remarks || null,
      }
      await api.post('/inventory/transactions', payload)
      message.success('Transaction added')
      setModalOpen(false)
      form.resetFields()
      fetchStock()
      fetchTxns()
    } catch {
      // validation error or request failure
    } finally {
      setSubmitting(false)
    }
  }

  const stockColumns = [
    { title: 'Material', dataIndex: 'material_name', key: 'material_name' },
    { title: 'Code', dataIndex: 'material_code', key: 'material_code', width: 100 },
    { title: 'Type', dataIndex: 'material_type', key: 'material_type', width: 100,
      render: (v) => <Tag>{v}</Tag>,
    },
    { title: 'UOM', dataIndex: 'uom_code', key: 'uom_code', width: 70 },
    { title: 'Received', dataIndex: 'total_received', key: 'total_received', width: 100,
      render: (v) => v?.toLocaleString(),
    },
    { title: 'Consumed', dataIndex: 'total_consumed', key: 'total_consumed', width: 100,
      render: (v) => v?.toLocaleString(),
    },
    { title: 'Net Stock', dataIndex: 'net_stock', key: 'net_stock', width: 100,
      render: (v, r) => {
        const color = r.status === 'REORDER' ? 'red' : r.status === 'LOW' ? 'orange' : 'green'
        return <span style={{ fontWeight: 'bold', color }}>{v?.toLocaleString()}</span>
      },
    },
    { title: 'Reorder Level', dataIndex: 'reorder_level', key: 'reorder_level', width: 100,
      render: (v) => v?.toLocaleString() || '-',
    },
    { title: 'Status', dataIndex: 'status', key: 'status', width: 100,
      render: (v) => {
        const colors = { REORDER: 'red', LOW: 'orange', OK: 'green' }
        return <Tag color={colors[v]}>{v}</Tag>
      },
    },
  ]

  const txnColumns = [
    { title: 'Date', dataIndex: 'transaction_date', key: 'transaction_date', width: 110 },
    { title: 'Material', dataIndex: 'material_name', key: 'material_name' },
    { title: 'Type', dataIndex: 'transaction_type', key: 'transaction_type', width: 100,
      render: (v) => {
        const colors = { IN: 'green', OUT: 'red', ADJUSTMENT: 'orange' }
        return <Tag color={colors[v]}>{v}</Tag>
      },
    },
    { title: 'Qty', dataIndex: 'quantity', key: 'quantity', width: 100,
      render: (v, r) => (
        <span style={{ color: r.transaction_type === 'IN' ? 'green' : 'red', fontWeight: 'bold' }}>
          {r.transaction_type === 'IN' ? '+' : '-'}{v?.toLocaleString()}
        </span>
      ),
    },
    { title: 'Reference', dataIndex: 'reference_type', key: 'reference_type', width: 100 },
    { title: 'Remarks', dataIndex: 'remarks', key: 'remarks' },
    { title: 'Recorded By', dataIndex: 'creator_name', key: 'creator_name', width: 120 },
  ]

  const tabItems = [
    {
      key: 'stock',
      label: (
        <Badge count={reorderCount} size="small" offset={[6, -2]}>
          <span>Stock Status</span>
        </Badge>
      ),
      children: (
        <div>
          {reorderCount > 0 && (
            <div style={{ background: '#fff2f0', border: '1px solid #ffccc7', borderRadius: 6, padding: '8px 16px', marginBottom: 16 }}>
              <WarningOutlined style={{ color: '#ff4d4f', marginRight: 8 }} />
              <strong>{reorderCount} material(s)</strong> need reordering (below reorder level).
            </div>
          )}
          <Table rowKey="material_id" columns={stockColumns} dataSource={stockData}
            loading={loading} pagination={{ pageSize: 20 }} size="middle" />
        </div>
      ),
    },
    {
      key: 'txn',
      label: 'Transaction Log',
      children: (
        <div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 12 }}>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
              Add Transaction
            </Button>
          </div>
          <Table rowKey="transaction_id" columns={txnColumns} dataSource={txnData}
            loading={txnLoading} pagination={{ pageSize: 20 }} size="middle" />
        </div>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Typography.Title level={4} style={{ margin: 0 }}>Inventory Management</Typography.Title>
        <Button icon={<ReloadOutlined />} onClick={() => { fetchStock(); fetchTxns() }}>Refresh</Button>
      </div>
      <Tabs items={tabItems} />

      <Modal
        title="Add Inventory Transaction"
        open={modalOpen}
        onOk={handleAdd}
        onCancel={() => { setModalOpen(false); form.resetFields() }}
        confirmLoading={submitting}
        okText="Add"
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="transaction_date" label="Date" rules={[{ required: true, message: 'Select date' }]}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="material_id" label="Material" rules={[{ required: true, message: 'Select material' }]}>
            <Select
              placeholder="Select material"
              options={materials.map(m => ({ label: `${m.material_name} (${m.material_code})`, value: m.material_id }))}
            />
          </Form.Item>
          <Form.Item name="transaction_type" label="Type" rules={[{ required: true, message: 'Select type' }]}>
            <Select
              options={[
                { label: 'Incoming (IN)', value: 'IN' },
                { label: 'Outgoing (OUT)', value: 'OUT' },
                { label: 'Adjustment', value: 'ADJUSTMENT' },
              ]}
            />
          </Form.Item>
          <Form.Item name="quantity" label="Quantity" rules={[{ required: true, message: 'Enter quantity' }]}>
            <InputNumber style={{ width: '100%' }} min={0} step={0.01} />
          </Form.Item>
          <Form.Item name="reference_type" label="Reference Type">
            <Select allowClear placeholder="Optional">
              <Select.Option value="RECEIPT">RECEIPT</Select.Option>
              <Select.Option value="CONSUMPTION">CONSUMPTION</Select.Option>
              <Select.Option value="ADJUST">ADJUST</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="remarks" label="Remarks">
            <Input.TextArea rows={2} placeholder="Optional notes" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
