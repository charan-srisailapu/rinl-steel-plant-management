import { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    if (token && savedUser) {
      setUser(JSON.parse(savedUser))
    }
    setLoading(false)
  }, [])

const login = async (username, password) => {
  console.log("AUTH LOGIN START")

  try {
    const res = await api.post('/auth/login', {
      username,
      password
    })

    console.log("AUTH RESPONSE", res.data)

    const { access_token, user: userData } = res.data

    localStorage.setItem('token', access_token)
    localStorage.setItem('user', JSON.stringify(userData))

    setUser(userData)

    return userData
  } catch (err) {
    console.error("AUTH ERROR", err)
    console.error("AUTH RESPONSE", err.response)
    console.error("AUTH MESSAGE", err.message)


    throw err
  }
}

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
