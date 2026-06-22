import { Routes, Route, Navigate } from 'react-router-dom'
import { Spin } from 'antd'
import { useAuth } from './store/AuthContext'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Reports from './pages/Reports'
import Departments from './pages/Departments'
import Units from './pages/Units'
import Employees from './pages/Employees'
import Products from './pages/Products'
import Materials from './pages/Materials'
import Suppliers from './pages/Suppliers'
import MaterialReceipts from './pages/MaterialReceipts'
import Inventory from './pages/Inventory'
import Customers from './pages/Customers'
import FinishedProducts from './pages/FinishedProducts'
import Dispatch from './pages/Dispatch'
import AppLayout from './components/Layout/AppLayout'

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />
  return user ? children : <Navigate to="/login" replace />
}

export default function App() {
  const { user, loading } = useAuth()
  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="reports" element={<Reports />} />
        <Route path="departments" element={<Departments />} />
        <Route path="units" element={<Units />} />
        <Route path="employees" element={<Employees />} />
        <Route path="products" element={<Products />} />
        <Route path="materials" element={<Materials />} />
        <Route path="suppliers" element={<Suppliers />} />
        <Route path="material-receipts" element={<MaterialReceipts />} />
        <Route path="inventory" element={<Inventory />} />
        <Route path="customers" element={<Customers />} />
        <Route path="finished-products" element={<FinishedProducts />} />
        <Route path="dispatch" element={<Dispatch />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
