import axios from 'axios'

export interface AssessmentResult {
  [specialty: string]: {
    risk_score?: number
    risk_level?: string
    prediction?: string
    confidence?: number
    [key: string]: unknown
  }
}

export interface HistoryEntry {
  id: number
  timestamp: string
  profile: Record<string, number | string>
  results: AssessmentResult
}

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,          // send session cookie on every request
  headers: { 'Content-Type': 'application/json' },
})

// On 401 redirect to login — catches expired sessions across all calls
api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401 && !window.location.pathname.startsWith('/login')) {
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export async function login(patientId: string, password: string): Promise<void> {
  await api.post('/auth/login', { patient_id: patientId, password })
}

export async function logout(): Promise<void> {
  await api.post('/auth/logout')
}

export async function assess(
  trackId: string,
  profile: Record<string, number | string>
): Promise<{ results: AssessmentResult; profile_used: Record<string, number | string> }> {
  const { data } = await api.post('/assess', { trackId, profile })
  return data
}

export async function getHistory(): Promise<HistoryEntry[]> {
  const { data } = await api.get('/history')
  return data
}

export async function exportCsv(): Promise<void> {
  const response = await api.get('/export/csv', { responseType: 'blob' })
  const url = URL.createObjectURL(new Blob([response.data], { type: 'text/csv' }))
  const a = document.createElement('a')
  a.href = url
  a.download = 'patient_history.csv'
  a.click()
  URL.revokeObjectURL(url)
}
