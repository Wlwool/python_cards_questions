import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

// добавляет JWT токен к каждому запросу если он есть
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export default api
