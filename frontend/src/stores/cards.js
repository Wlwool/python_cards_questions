import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import api from '../api'

export const useCardsStore = defineStore('cards', () => {
  const items = ref([])
  const total = ref(0)
  const loading = ref(false)
  const categories = ref([])

  const filters = reactive({
    search: '',
    category: '',
    difficulty: '',
    tags: '',
    page: 1,
    per_page: 20,
  })

  async function fetchCards() {
    loading.value = true
    try {
      const params = Object.fromEntries(
        Object.entries(filters).filter(([, v]) => v !== '' && v !== null)
      )
      const { data } = await api.get('/cards', { params })
      items.value = data.items
      total.value = data.total
    } finally {
      loading.value = false
    }
  }

  async function fetchCategories() {
    const { data } = await api.get('/cards/categories')
    categories.value = data.categories
  }

  function resetFilters() {
    Object.assign(filters, { search: '', category: '', difficulty: '', tags: '', page: 1 })
  }

  return { items, total, loading, categories, filters, fetchCards, fetchCategories, resetFilters }
})
