<template>
  <div class="filters">
    <input
      v-model="filters.search"
      class="filters__search"
      type="text"
      placeholder="Поиск по вопросам и ответам..."
      @input="onSearch"
    />

    <div class="filters__row">
      <select v-model="filters.category" class="filters__select" @change="emit('change')">
        <option value="">Все категории</option>
        <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
      </select>

      <select v-model="filters.difficulty" class="filters__select" @change="emit('change')">
        <option value="">Любая сложность</option>
        <option value="easy">Easy</option>
        <option value="normal">Normal</option>
        <option value="hard">Hard</option>
      </select>

      <button class="filters__reset" @click="onReset">Сбросить</button>
    </div>
  </div>
</template>

<script setup>
import { useDebounceFn } from '../composables/useDebounceFn'
import { useCardsStore } from '../stores/cards'
import { storeToRefs } from 'pinia'

const emit = defineEmits(['change'])
const store = useCardsStore()
const { filters, categories } = storeToRefs(store)

const onSearch = useDebounceFn(() => {
  filters.value.page = 1
  emit('change')
}, 400)

function onReset() {
  store.resetFilters()
  emit('change')
}
</script>

<style scoped>
.filters {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 28px;
}

.filters__search {
  width: 100%;
  padding: 10px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text);
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}

.filters__search:focus {
  border-color: var(--accent);
}

.filters__row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.filters__select {
  padding: 8px 12px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text);
  font-size: 14px;
  outline: none;
  cursor: pointer;
  min-width: 160px;
}

.filters__reset {
  padding: 8px 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: none;
  color: var(--text-muted);
  font-size: 14px;
  transition: color 0.2s;
}

.filters__reset:hover {
  color: var(--text);
}
</style>
