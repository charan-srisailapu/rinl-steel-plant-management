import { useState, useEffect } from 'react'
import { Row, Col, Card, Statistic, Typography, Spin, Alert, Table, Tag } from 'antd'
import {
  ApartmentOutlined, TeamOutlined, InboxOutlined, ExperimentOutlined,
  ToolOutlined, RiseOutlined, FallOutlined,
} from '@ant-design/icons'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell,
} from 'recharts'
import api from '../services/api'

const COLORS = ['#003366', '#006699', '#009900', '#cc6600', '#990000', '#663399', '#339966', '#996633']

export default function Reports() {
  const [summary, setSummary] = useState(null)
  const [monthlyProd, setMonthlyProd] = useState([])
  const [weeklyTrend, setWeeklyTrend] = useState([])
  const [prodByCategory, setProdByCategory] = useState([])
  const [capacity, setCapacity] = useState([])
  const [deptDist, setDeptDist] = useState([])
  const [empByDept, setEmpByDept] = useState([])
  const [prodByCatDist, setProdByCatDist] = useState([])
  const [matByType, setMatByType] = useState([])
  const [unitsByType, setUnitsByType] = useState([])
  const [dailyProd, setDailyProd] = useState([])
  const [shiftProd, setShiftProd] = useState([])
  const [supplierPerf, setSupplierPerf] = useState([])
  const [productStock, setProductStock] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true)
      setError(null)
      try {
        const [
          s, mp, wt, pc, cap, dd, ebd, pbcd, mbt, ubt, dp, sp, sup, ps,
        ] = await Promise.all([
          api.get('/reports/summary'),
          api.get('/reports/production/monthly?months=6'),
          api.get('/reports/production/weekly?weeks=12'),
          api.get('/reports/production/by-category?months=6'),
          api.get('/reports/production/capacity'),
          api.get('/reports/master/departments'),
          api.get('/reports/master/employees-by-dept'),
          api.get('/reports/master/products-by-category'),
          api.get('/reports/master/materials-by-type'),
          api.get('/reports/master/units-by-type'),
          api.get('/reports/production/daily?days=30'),
          api.get('/reports/production/shift-productivity?days=30'),
          api.get('/suppliers/performance/summary'),
          api.get('/reports/product-stock'),
        ])
        setSummary(s.data)
        setMonthlyProd(mp.data)
        setWeeklyTrend(wt.data)
        setProdByCategory(pc.data)
        setCapacity(cap.data)
        setDeptDist(dd.data)
        setEmpByDept(ebd.data)
        setProdByCatDist(pbcd.data)
        setMatByType(mbt.data)
        setUnitsByType(ubt.data)
        setDailyProd(dp.data)
        setShiftProd(sp.data)
        setSupplierPerf(sup.data)
        setProductStock(ps.data)
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load reports')
      } finally {
        setLoading(false)
      }
    }
    fetchAll()
  }, [])

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />
  if (error) return <Alert type="error" message="Error" description={error} showIcon />

  const summaryCards = summary ? [
    { title: 'Departments', value: summary.total_departments, icon: <ApartmentOutlined />, color: '#003366' },
    { title: 'Production Units', value: summary.total_units, icon: <ToolOutlined />, color: '#006699' },
    { title: 'Employees', value: summary.total_employees, icon: <TeamOutlined />, color: '#009900' },
    { title: 'Products', value: summary.total_products, icon: <InboxOutlined />, color: '#cc6600' },
    { title: 'Materials', value: summary.total_materials, icon: <ExperimentOutlined />, color: '#990000' },
    { title: 'This Month Prod.', value: summary.this_month_production?.toLocaleString() || 'N/A', icon: <RiseOutlined />, color: '#339966' },
    { title: 'Last Month Prod.', value: summary.last_month_production?.toLocaleString() || 'N/A', icon: <FallOutlined />, color: '#996633' },
  ] : []

  const categories = [...new Set(monthlyProd.map((d) => d.category))]
  const months = [...new Set(monthlyProd.map((d) => `${d.month} ${d.year}`))]
  const monthlyChartData = months.map((m) => {
    const entry = { month: m }
    categories.forEach((cat) => {
      const found = monthlyProd.find((d) => `${d.month} ${d.year}` === m && d.category === cat)
      entry[cat] = found ? found.total_quantity : 0
    })
    return entry
  })

  const weeklyCategories = [...new Set(weeklyTrend.map((d) => d.product_category))]
  const weeklyChartData = weeklyTrend.reduce((acc, curr) => {
    const label = curr.week_start.slice(5, 10)
    let existing = acc.find((e) => e.week === label)
    if (!existing) {
      existing = { week: label }
      acc.push(existing)
    }
    existing[curr.product_category] = (existing[curr.product_category] || 0) + curr.total_quantity
    return acc
  }, [])

  const capacityData = capacity.map((d) => ({
    name: d.unit_code,
    capacity: d.capacity_tpa || 0,
    actual: d.actual_production,
    pct: d.utilization_pct || 0,
  }))

  const dailyProdData = dailyProd.reduce((acc, curr) => {
    let existing = acc.find((e) => e.date === curr.record_date)
    if (!existing) {
      existing = { date: curr.record_date }
      acc.push(existing)
    }
    existing[curr.product_category] = (existing[curr.product_category] || 0) + curr.total_quantity
    return acc
  }, [])

  const dailyProdCategories = [...new Set(dailyProd.map((d) => d.product_category))]

  const CustomPieLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
    const RADIAN = Math.PI / 180
    const radius = innerRadius + (outerRadius - innerRadius) * 1.4
    const x = cx + radius * Math.cos(-midAngle * RADIAN)
    const y = cy + radius * Math.sin(-midAngle * RADIAN)
    return (
      <text x={x} y={y} fill="#333" textAnchor={x > cx ? 'start' : 'end'} dominantBaseline="central" fontSize={11}>
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    )
  }

  const capacityColumns = [
    { title: 'Unit', dataIndex: 'name', key: 'name', width: 80 },
    { title: 'Capacity (TPA)', dataIndex: 'capacity', key: 'capacity', width: 110, render: (v) => v ? v.toLocaleString() : '-' },
    { title: 'Actual (12mo)', dataIndex: 'actual', key: 'actual', width: 110, render: (v) => v.toLocaleString() },
    { title: 'Utilization', dataIndex: 'pct', key: 'pct', render: (v) => v ? `${v}%` : 'N/A' },
    {
      title: 'Progress', key: 'progress',
      render: (_, r) => (
        <div style={{ width: 200, height: 20, background: '#f0f0f0', borderRadius: 4, overflow: 'hidden' }}>
          <div style={{
            width: `${Math.min(r.pct || 0, 100)}%`, height: '100%',
            background: (r.pct || 0) > 80 ? '#52c41a' : (r.pct || 0) > 50 ? '#faad14' : '#f5222d',
            transition: 'width 0.5s',
          }} />
        </div>
      ),
    },
  ]

  const productStockColumns = [
    { title: 'Product', dataIndex: 'product_name', key: 'product_name' },
    { title: 'Category', dataIndex: 'category_name', key: 'category_name', width: 100 },
    { title: 'Stock Qty', dataIndex: 'stock_qty', key: 'stock_qty', width: 100,
      render: (v) => <span style={{ fontWeight: 'bold' }}>{v?.toLocaleString()}</span>,
    },
    { title: 'UOM', dataIndex: 'uom_code', key: 'uom_code', width: 60 },
    { title: 'Selling Price', dataIndex: 'selling_price', key: 'selling_price', width: 110,
      render: (v) => v ? `₹${v.toLocaleString()}` : '-',
    },
  ]

  const supplierPerfColumns = [
    { title: 'Supplier', dataIndex: 'supplier_name', key: 'supplier_name' },
    { title: 'Code', dataIndex: 'supplier_code', key: 'supplier_code', width: 90 },
    { title: 'Receipts', dataIndex: 'total_receipts', key: 'total_receipts', width: 80 },
    { title: 'Total Qty', dataIndex: 'total_quantity', key: 'total_quantity', width: 100,
      render: (v) => v?.toLocaleString(),
    },
    { title: 'Avg Quality', dataIndex: 'avg_quality_score', key: 'avg_quality_score', width: 100,
      render: (v) => v ? `${v.toFixed(1)}%` : '-',
    },
    { title: 'Rating', dataIndex: 'rating', key: 'rating', width: 80 },
  ]

  const shiftProdData = shiftProd.map((d) => ({
    name: d.shift_code,
    total: d.total_quantity,
    avg: d.avg_quantity || 0,
    count: d.record_count,
  }))

  return (
    <div>
      <Typography.Title level={4}>Analytics & Reports</Typography.Title>

      {/* Summary Cards */}
      <Row gutter={[12, 12]} style={{ marginBottom: 20 }}>
        {summaryCards.map((card) => (
          <Col xs={12} sm={8} lg={6} xl={3} key={card.title}>
            <Card size="small" hoverable>
              <Statistic
                title={card.title}
                value={card.value}
                prefix={<span style={{ color: card.color }}>{card.icon}</span>}
                valueStyle={{ fontSize: 20 }}
              />
            </Card>
          </Col>
        ))}
      </Row>

      {/* Row 1: Monthly Production Bar + Weekly Trend Line */}
      <Row gutter={[16, 16]} style={{ marginBottom: 20 }}>
        <Col xs={24} lg={12}>
          <Card title="Monthly Production by Category (6 months)" size="small">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={monthlyChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" fontSize={10} />
                <YAxis fontSize={11} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                {categories.map((cat, i) => (
                  <Bar key={cat} dataKey={cat} fill={COLORS[i % COLORS.length]} stackId="a" />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Weekly Production Trend (12 weeks)" size="small">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={weeklyChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="week" fontSize={10} />
                <YAxis fontSize={11} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                {weeklyCategories.map((cat, i) => (
                  <Line key={cat} type="monotone" dataKey={cat} stroke={COLORS[i % COLORS.length]} strokeWidth={2} dot={false} />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Row 2: Production by Category Pie + Department Distribution Pie + Products by Category Pie */}
      <Row gutter={[16, 16]} style={{ marginBottom: 20 }}>
        <Col xs={24} lg={8}>
          <Card title="Production by Category (6 months)" size="small">
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={prodByCategory}
                  dataKey="count"
                  nameKey="category"
                  cx="50%" cy="50%" outerRadius={90}
                  label={CustomPieLabel}
                >
                  {prodByCategory.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: 11 }} />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Departments by Type" size="small">
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={deptDist}
                  dataKey="count"
                  nameKey="category"
                  cx="50%" cy="50%" outerRadius={90}
                  label={CustomPieLabel}
                >
                  {deptDist.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: 11 }} />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Products by Category" size="small">
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={prodByCatDist}
                  dataKey="count"
                  nameKey="category"
                  cx="50%" cy="50%" outerRadius={90}
                  label={CustomPieLabel}
                >
                  {prodByCatDist.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: 11 }} />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Row 3: Capacity Utilization */}
      <Row gutter={[16, 16]} style={{ marginBottom: 20 }}>
        <Col xs={24}>
          <Card title="Production Unit Capacity Utilization (Worm Chart - Last 12 Months)" size="small">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={capacityData} layout="vertical" barSize={16}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" fontSize={11} />
                <YAxis dataKey="name" type="category" width={80} fontSize={11} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Bar dataKey="actual" fill="#006699" name="Actual Production" />
                <Bar dataKey="capacity" fill="#cc6600" name="Capacity (TPA)" />
              </BarChart>
            </ResponsiveContainer>
            <Table columns={capacityColumns} dataSource={capacityData} rowKey="name" pagination={false} size="small" style={{ marginTop: 12 }} />
          </Card>
        </Col>
      </Row>

      {/* Row 4: Daily Production Line + Shift Productivity Bar + Supplier Performance Table */}
      <Row gutter={[16, 16]} style={{ marginBottom: 20 }}>
        <Col xs={24} lg={12}>
          <Card title="Daily Production (Last 30 Days)" size="small">
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={dailyProdData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" fontSize={9} tickFormatter={(v) => v.slice(5)} />
                <YAxis fontSize={11} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                {dailyProdCategories.map((cat, i) => (
                  <Line key={cat} type="monotone" dataKey={cat} stroke={COLORS[i % COLORS.length]} strokeWidth={1.5} dot={false} />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Shift Productivity (Last 30 Days)" size="small">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={shiftProdData} barSize={40}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" fontSize={11} />
                <YAxis fontSize={11} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Bar dataKey="total" fill="#003366" name="Total Qty" />
                <Bar dataKey="avg" fill="#009900" name="Avg Qty" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Row 5: Supplier Performance Table + Product Stock Table */}
      <Row gutter={[16, 16]} style={{ marginBottom: 20 }}>
        <Col xs={24} lg={12}>
          <Card title="Supplier Performance Summary" size="small">
            <Table columns={supplierPerfColumns} dataSource={supplierPerf} rowKey="supplier_id" pagination={false} size="small" />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Finished Product Stock" size="small">
            <Table columns={productStockColumns} dataSource={productStock} rowKey="product_code" pagination={false} size="small" />
          </Card>
        </Col>
      </Row>

      {/* Row 6: Employees by Dept + Materials by Type + Units by Type */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={8}>
          <Card title="Employees by Department" size="small">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={empByDept} layout="vertical" barSize={12}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" fontSize={11} />
                <YAxis dataKey="category" type="category" width={70} fontSize={10} />
                <Tooltip />
                <Bar dataKey="count" fill="#009900" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Materials by Type" size="small">
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={matByType}
                  dataKey="count"
                  nameKey="category"
                  cx="50%" cy="50%" outerRadius={90}
                  label={CustomPieLabel}
                >
                  {matByType.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: 11 }} />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Production Units by Type" size="small">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={unitsByType} barSize={20}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" fontSize={10} />
                <YAxis fontSize={11} />
                <Tooltip />
                <Bar dataKey="count" fill="#663399" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>
    </div>
  )
}
