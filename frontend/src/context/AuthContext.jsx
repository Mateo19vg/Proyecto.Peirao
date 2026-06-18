import React, { createContext, useContext, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login as apiLogin, register as apiRegister, logout as apiLogout, isAuthenticated } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [isAuth, setIsAuth] = useState(isAuthenticated())
  const navigate = useNavigate()

  const login = async (username, password) => {
    await apiLogin(username, password)
    setIsAuth(true)
  }

  const register = async (username, password, email) => {
    return apiRegister(username, password, email)
  }

  const logout = () => {
    setIsAuth(false)
    apiLogout() 
  }

  return (
    <AuthContext.Provider value={{ isAuth, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)