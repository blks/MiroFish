import axios from 'axios'

// Create the Axios instance
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001',
  timeout: 300000, // 5-minute timeout (ontology generation can take a while)
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
service.interceptors.request.use(
  config => {
    const locale = localStorage.getItem('mirofish-locale') || 'en'
    config.headers['Accept-Language'] = locale
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor (fault-tolerant retry behavior)
service.interceptors.response.use(
  response => {
    const res = response.data
    
    // Throw when the response status is not success
    if (!res.success && res.success !== undefined) {
      console.error('API Error:', res.error || res.message || 'Unknown error')
      return Promise.reject(new Error(res.error || res.message || 'Error'))
    }
    
    return res
  },
  error => {
    console.error('Response error:', error)

    const data = error.response?.data
    const serverMsg =
      data && typeof data === 'object' && (data.error ?? data.message)
    if (serverMsg) {
      const wrapped = new Error(String(serverMsg))
      wrapped.response = error.response
      return Promise.reject(wrapped)
    }
    
    // Handle timeouts
    if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
      console.error('Request timeout')
    }
    
    // Handle network errors
    if (error.message === 'Network Error') {
      console.error('Network error - please check your connection')
    }
    
    return Promise.reject(error)
  }
)

// Request helper with retry support
export const requestWithRetry = async (requestFn, maxRetries = 3, delay = 1000) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn()
    } catch (error) {
      const status = error.response?.status
      if (typeof status === 'number' && status >= 400 && status < 500) {
        throw error
      }
      if (i === maxRetries - 1) throw error
      
      console.warn(`Request failed, retrying (${i + 1}/${maxRetries})...`)
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)))
    }
  }
}

export default service
