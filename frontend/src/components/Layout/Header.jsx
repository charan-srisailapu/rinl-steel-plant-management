import { Layout, Button, Dropdown, Space, Typography } from 'antd'
import { LogoutOutlined, UserOutlined } from '@ant-design/icons'
import { useAuth } from '../../store/AuthContext'

const { Header } = Layout

export default function AppHeader() {
  const { user, logout } = useAuth()

  return (
    <Header
      style={{
        background: '#fff',
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid #f0f0f0',
      }}
    >
      <Typography.Title level={4} style={{ margin: 0, color: '#003366' }}>
        RINL Steel Plant
      </Typography.Title>
      <Dropdown
        menu={{
          items: [
            { key: 'role', label: `Role: ${user?.role}`, disabled: true },
            { type: 'divider' },
            {
              key: 'logout',
              icon: <LogoutOutlined />,
              label: 'Logout',
              onClick: logout,
            },
          ],
        }}
      >
        <Button type="text" icon={<UserOutlined />}>
          <Space>{user?.username}</Space>
        </Button>
      </Dropdown>
    </Header>
  )
}
