import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useAdminStore = defineStore('admin', () => {
  const token = ref(localStorage.getItem('admin_token') || '')
  const isLoggedIn = computed(() => !!token.value)

  async function login(password) {
    const { data } = await api.post('/admin/login', { password })
    token.value = data.access_token
    localStorage.setItem('admin_token', data.access_token)
  }

  function logout() {
    token.value = ''
    localStorage.removeItem('admin_token')
  }

  return { token, isLoggedIn, login, logout }
})
