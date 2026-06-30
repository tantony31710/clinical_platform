import React, { createContext, useContext, useEffect, useState } from 'react'
import { login as apiLogin, logout as apiLogout } from './api'
import axios from 'axios'

interface AuthState {
  isAuthenticated: boolean
  patientId: string | null
  isLoading: boolean
  login: (patientId: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthState>({
  isAuthenticated: false,
  patientId: null,
  isLoading: true,
  login: async () => {},
  logout: async () => {},
})

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [patientId, setPatientId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // On mount, probe the API to see if a valid session exists
  useEffect(() => {
    axios
      .get('/api/history', { withCredentials: true })
      .then(() => {
        setIsAuthenticated(true)
        // patient_id is stored server-side; we can't read it from the client
        // so just mark as authenticated
        setPatientId('session')
      })
      .catch(() => {
        setIsAuthenticated(false)
        setPatientId(null)
      })
      .finally(() => setIsLoading(false))
  }, [])

  const login = async (id: string, password: string) => {
    await apiLogin(id, password)
    setIsAuthenticated(true)
    setPatientId(id)
  }

  const logout = async () => {
    await apiLogout()
    setIsAuthenticated(false)
    setPatientId(null)
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, patientId, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
