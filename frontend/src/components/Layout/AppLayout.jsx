import { Outlet } from 'react-router-dom'
import { Layout } from 'antd'
import AppSidebar from './Sidebar'
import AppHeader from './Header'

const { Content, Sider } = Layout

export default function AppLayout() {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider breakpoint="lg" collapsedWidth="0" theme="dark">
        <AppSidebar />
      </Sider>
      <Layout>
        <AppHeader />
        <Content style={{ margin: 16, padding: 24, background: '#fff', borderRadius: 8 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
