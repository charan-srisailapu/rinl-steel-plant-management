import { useNavigate, useLocation } from 'react-router-dom'
import { Menu } from 'antd'
import {
  DashboardOutlined,
  ApartmentOutlined,
  TeamOutlined,
  ToolOutlined,
  InboxOutlined,
  ExperimentOutlined,
  BarChartOutlined,
  ShoppingCartOutlined,
  CarryOutOutlined,
  ContainerOutlined,
  UserOutlined,
  NodeIndexOutlined,
} from '@ant-design/icons'

const menuItems = [
  { key: '/', icon: <DashboardOutlined />, label: 'Dashboard' },
  { key: '/reports', icon: <BarChartOutlined />, label: 'Reports & Analytics' },
  { key: 'div1', type: 'divider' },
  { key: '/departments', icon: <ApartmentOutlined />, label: 'Departments' },
  { key: '/units', icon: <ToolOutlined />, label: 'Production Units' },
  { key: '/employees', icon: <TeamOutlined />, label: 'Employees' },
  { key: '/products', icon: <InboxOutlined />, label: 'Products' },
  { key: '/materials', icon: <ExperimentOutlined />, label: 'Materials' },
  { key: 'div2', type: 'divider' },
  {
    key: 'supply-chain', icon: <ShoppingCartOutlined />, label: 'Supply Chain',
    children: [
      { key: '/suppliers', icon: <CarryOutOutlined />, label: 'Suppliers' },
      { key: '/material-receipts', icon: <ContainerOutlined />, label: 'Material Receipts' },
      { key: '/inventory', icon: <ExperimentOutlined />, label: 'Inventory' },
    ],
  },
  {
    key: 'sales', icon: <UserOutlined />, label: 'Sales & Dispatch',
    children: [
      { key: '/customers', icon: <TeamOutlined />, label: 'Customers' },
      { key: '/finished-products', icon: <InboxOutlined />, label: 'Finished Products' },
      { key: '/dispatch', icon: <NodeIndexOutlined />, label: 'Dispatch' },
    ],
  },
]

export default function AppSidebar() {
  const navigate = useNavigate()
  const location = useLocation()

  const findOpenKeys = () => {
    const path = location.pathname
    if (['/suppliers', '/material-receipts', '/inventory'].includes(path)) return ['supply-chain']
    if (['/customers', '/finished-products', '/dispatch'].includes(path)) return ['sales']
    return []
  }

  return (
    <div>
      <div
        style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
          fontWeight: 'bold',
          fontSize: 16,
          borderBottom: '1px solid rgba(255,255,255,0.1)',
        }}
      >
        RINL Steel DB
      </div>
      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[location.pathname]}
        defaultOpenKeys={findOpenKeys()}
        items={menuItems}
        onClick={({ key }) => key.startsWith('/') && navigate(key)}
      />
    </div>
  )
}
