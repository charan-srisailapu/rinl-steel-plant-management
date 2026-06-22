import { useState, useEffect } from 'react'
import { Row, Col, Card, Statistic, Typography, Table, Tag, Alert } from 'antd'
import {
  ApartmentOutlined, TeamOutlined, InboxOutlined, ExperimentOutlined,
  ToolOutlined, WarningOutlined, CarOutlined,
} from '@ant-design/icons'
import api from '../services/api'

export default function Dashboard() {
  const [counts, setCounts] = useState({})
  const [reorderItems, setReorderItems] = useState([])
  const [recentDispatches, setRecentDispatches] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [depts, units, emps, prods, mats, reorder, dispatch] = await Promise.all([
          api.get('/departments'),
          api.get('/units'),
          api.get('/employees'),
          api.get('/products'),
          api.get('/materials'),
          api.get('/inventory/reorder-items'),
          api.get('/dispatch/summary/recent?days=30'),
        ])
        setCounts({
          departments: depts.data.length,
          units: units.data.length,
          employees: emps.data.length,
          products: prods.data.length,
          materials: mats.data.length,
        })
        setReorderItems(reorder.data || [])
        setRecentDispatches(dispatch.data || [])
      } catch {
        setCounts({
          departments: 'N/A', units: 'N/A', employees: 'N/A',
          products: 'N/A', materials: 'N/A',
        })
      } finally {
        setLoading(false)
      }
    }
    fetchAll()
  }, [])

  const cards = [
    { title: 'Departments', value: counts.departments, icon: <ApartmentOutlined />, color: '#003366' },
    { title: 'Production Units', value: counts.units, icon: <ToolOutlined />, color: '#006699' },
    { title: 'Employees', value: counts.employees, icon: <TeamOutlined />, color: '#009900' },
    { title: 'Products', value: counts.products, icon: <InboxOutlined />, color: '#cc6600' },
    { title: 'Materials', value: counts.materials, icon: <ExperimentOutlined />, color: '#990000' },
  ]

  const statusColors = { Dispatched: 'blue', 'In Transit': 'orange', Delivered: 'green', Cancelled: 'red' }

  const dispatchColumns = [
    { title: 'Date', dataIndex: 'dispatch_date', key: 'dispatch_date', width: 100 },
    { title: 'Invoice', dataIndex: 'invoice_no', key: 'invoice_no', width: 110 },
    { title: 'Customer', dataIndex: 'customer_name', key: 'customer_name' },
    { title: 'Amount', dataIndex: 'total_amount', key: 'total_amount', width: 110,
      render: (v) => v ? `₹${v.toLocaleString()}` : '-',
    },
    { title: 'Status', dataIndex: 'delivery_status', key: 'delivery_status', width: 100,
      render: (v) => <Tag color={statusColors[v]}>{v}</Tag>,
    },
  ]

  return (
    <div>
      <Typography.Title level={4}>Dashboard</Typography.Title>

      {reorderItems.length > 0 && (
        <Alert
          type="warning"
          showIcon
          icon={<WarningOutlined />}
          message={<strong>{reorderItems.length} material(s) below reorder level</strong>}
          description={reorderItems.map((item) => item.material_name).join(', ')}
          style={{ marginBottom: 16 }}
          closable
        />
      )}

      <Row gutter={[16, 16]} style={{ marginBottom: 20 }}>
        {cards.map((card) => (
          <Col xs={24} sm={12} lg={6} key={card.title}>
            <Card loading={loading} hoverable>
              <Statistic
                title={card.title}
                value={card.value}
                prefix={<span style={{ color: card.color }}>{card.icon}</span>}
              />
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24}>
          <Card
            title={<span><CarOutlined style={{ marginRight: 8 }} />Recent Dispatches (Last 30 Days)</span>}
            size="small"
          >
            <Table
              rowKey="invoice_no"
              columns={dispatchColumns}
              dataSource={recentDispatches}
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
      </Row>
    </div>
  )
}
