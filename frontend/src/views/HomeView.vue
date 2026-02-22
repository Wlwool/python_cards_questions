<template>
  <div>
    <div class="page-header">
      <h1>Карточки для подготовки</h1>
      <span class="page-header__count">{{ store.total }} вопросов</span>
    </div>

    <FilterBar @change="load" />

    <div v-if="store.loading" class="state-msg">Загрузка...</div>

    <div v-else-if="!store.items.length" class="state-msg">
      Ничего не найдено. Попробуй изменить фильтры.
    </div>

    <div v-else class="cards-grid">
      <CardComponent v-for="card in store.items" :key="card.id" :card="card" />
    </div>

    <!-- пагинация -->
    <div v-if="totalPages > 1" class="pagination">
      <button
        v-for="p in totalPages"
        :key="p"
        class="pagination__btn"
        :class="{ 'pagination__btn--active': p === store.filters.page }"
        @click="goToPage(p)"
      >
        {{ p }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useCardsStore } from '../stores/cards'
import CardComponent from '../components/CardComponent.vue'
import FilterBar from '../components/FilterBar.vue'

const store = useCardsStore()
const totalPages = computed(() => Math.ceil(store.total / store.filters.per_page))

function load() {
  store.fetchCards()
}

function goToPage(p) {
  store.filters.page = p
  load()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  store.fetchCategories()
  store.fetchCards()
})
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 700;
}

.page-header__count {
  color: var(--text-muted);
  font-size: 14px;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 16px;
}

.state-msg {
  color: var(--text-muted);
  text-align: center;
  padding: 60px 0;
}

.pagination {
  display: flex;
  justify-content: center;
  gap: 6px;
  margin-top: 32px;
}

.pagination__btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text-muted);
  font-size: 14px;
  transition: all 0.15s;
}

.pagination__btn:hover {
  border-color: var(--accent);
  color: var(--text);
}

.pagination__btn--active {
  background: var(--accent);
  border-color: var(--accent);
  color: white;
}
</style>
