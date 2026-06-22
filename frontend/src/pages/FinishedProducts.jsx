import { useState, useEffect, useCallback } from 'react'
import { Table, Button, Space, message, Typography, Tag, InputNumber } from 'antd'
import { ReloadOutlined, EditOutlined } from '@ant-design/icons'
import { useAuth } from '../store/AuthContext'
import api from '../services/api'

export default function FinishedProducts() {
  const { user } = useAuth()
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [editPrice, setEditPrice] = useState(null)

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const res = await api.get('/dispatch/products')
      setData(res.data)
    } catch {
      message.error('Failed to fetch finished products')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetch() }, [fetch])

  const updatePrice = async (id) => {
    try {
      await api.put(`/dispatch/products/${id}`, { selling_price: editPrice })
      message.success('Price updated')
      setEditingId(null)
      fetch()
    } catch {
      message.error('Failed to update')
    }
  }

  const columns = [
    { title: 'Code', dataIndex: 'product_code', key: 'product_code', width: 110 },
    { title: 'Name', dataIndex: 'product_name', key: 'product_name' },
    { title: 'Category', dataIndex: 'category_name', key: 'category_name', width: 100,
      render: (v) => <Tag>{v}</Tag>,
    },
    { title: 'Grade', dataIndex: 'grade', key: 'grade', width: 100 },
    { title: 'Size', dataIndex: 'size_spec', key: 'size_spec', width: 80 },
    { title: 'UOM', dataIndex: 'uom_code', key: 'uom_code', width: 60 },
    {
      title: 'Selling Price', dataIndex: 'selling_price', key: 'selling_price', width: 140,
      render: (v, r) => {
        if (editingId === r.product_id) {
          return (
            <Space>
              <InputNumber size="small" value={editPrice} onChange={setEditPrice}
                formatter={(val) => `₹ ${val}`} parser={(val) => val?.replace('₹ ', '')} style={{ width: 100 }} />
              <Button size="small" type="primary" onClick={() => updatePrice(r.product_id)}>Save</Button>
              <Button size="small" onClick={() => setEditingId(null)}>Cancel</Button>
            </Space>
          )
        }
        return (
          <Space>
            <span>{v ? `₹${v.toLocaleString()}` : '-'}</span>
            {user?.role !== 'report_viewer' && (
              <Button size="small" icon={<EditOutlined />} onClick={() => { setEditingId(r.product_id); setEditPrice(v || 0) }} />
            )}
          </Space>
        )
      },
    },
    {
      title: 'Stock Qty', dataIndex: 'stock_qty', key: 'stock_qty', width: 100,
      render: (v) => {
        const color = v > 1000 ? 'green' : v > 100 ? 'orange' : 'red'
        return <span style={{ fontWeight: 'bold', color }}>{v?.toLocaleString()}</span>
      },
    },
    { title: 'Active', dataIndex: 'is_active', key: 'is_active', width: 80,
      render: (v) => <Tag color={v ? 'green' : 'red'}>{v ? 'Yes' : 'No'}</Tag>,
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Typography.Title level={4} style={{ margin: 0 }}>Finished Products Inventory</Typography.Title>
        <Button icon={<ReloadOutlined />} onClick={fetch}>Refresh</Button>
      </div>

      <Table rowKey="product_id" columns={columns} dataSource={data} loading={loading}
        pagination={{ pageSize: 20 }} size="middle" />
    </div>
  )
}
