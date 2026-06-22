import { useState, useEffect } from 'react'
import { Card, Form, Input, Button, Typography, message, Alert } from 'antd'
import { UserOutlined, LockOutlined, WarningOutlined } from '@ant-design/icons'
import { useAuth } from '../store/AuthContext'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import EmberEffect from '../components/EmberEffect'
import './Login.css'

export default function Login() {
  const [loading, setLoading] = useState(false)
  const [backendDown, setBackendDown] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

useEffect(() => {
  setBackendDown(false)
}, [])

  const onFinish = async (values) => {
    setLoading(true)
    try {
      await login(values.username, values.password)
      message.success('Login successful')
      navigate('/')
    } catch (err) {
      if (!err.response) {
        message.error('Cannot reach backend server. Make sure the backend is running on port 8001.')
      } else {
        message.error(err.response?.data?.detail || 'Login failed')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-wrapper">
      <div className="login-bg" />
      <div className="login-overlay" />
      <EmberEffect />

      <Card className="login-card">
        {backendDown && (
          <Alert
            type="error"
            showIcon
            message="Backend Unreachable"
            description="The backend server does not appear to be running. Start it with start_backend.bat or run: uvicorn app.main:app --host 0.0.0.0 --port 8001"
            style={{ marginBottom: 16 }}
          />
        )}
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <WarningOutlined style={{ fontSize: 48, color: '#003366' }} />
          <Typography.Title level={3} style={{ margin: '8px 0 0' }}>
            RINL Steel Plant
          </Typography.Title>
          <Typography.Text type="secondary">
            Centralized Database System
          </Typography.Text>
        </div>
        <Form layout="vertical" onFinish={onFinish} autoComplete="off">
          <Form.Item name="username" rules={[{ required: true, message: 'Enter username' }]}>
            <Input prefix={<UserOutlined />} placeholder="Username" size="large" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: 'Enter password' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="Password" size="large" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block size="large">
              Login
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}
