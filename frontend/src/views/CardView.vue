<template>
  <div v-if="card" class="card-page">
    <RouterLink to="/" class="back">← Назад</RouterLink>

    <div class="card-page__header">
      <span class="category">{{ card.category }}</span>
      <span class="badge" :class="`badge--${card.difficulty}`">{{ card.difficulty }}</span>
    </div>

    <h1 class="card-page__question">{{ card.question }}</h1>

    <div class="card-page__answer">
      <p>{{ card.answer }}</p>
    </div>

    <div v-if="card.code_example" class="card-page__code">
      <pre><code ref="codeEl" class="language-python">{{ card.code_example }}</code></pre>
    </div>

    <div v-if="card.tags?.length" class="card-page__tags">
      <span v-for="tag in card.tags" :key="tag" class="tag">{{ tag }}</span>
    </div>
  </div>
  <div v-else class="state-msg">Загрузка...</div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import hljs from 'highlight.js/lib/core'
import python from 'highlight.js/lib/languages/python'
import api from '../api'

hljs.registerLanguage('python', python)

const route = useRoute()
const card = ref(null)
const codeEl = ref(null)

onMounted(async () => {
  const { data } = await api.get(`/cards/${route.params.id}`)
  card.value = data
  if (data.code_example) {
    await nextTick()
    hljs.highlightElement(codeEl.value)
  }
})
</script>

<style scoped>
.card-page { max-width: 800px; }
.back { color: var(--text-muted); font-size: 14px; display: block; margin-bottom: 24px; }
.card-page__header { display: flex; gap: 10px; align-items: center; margin-bottom: 12px; }
.category { font-size: 12px; color: var(--text-muted); text-transform: uppercase; }
.badge { font-size: 11px; padding: 2px 8px; border-radius: 20px; font-weight: 600; }
.badge--easy  { background: rgba(52,211,153,.15); color: var(--easy); }
.badge--normal{ background: rgba(251,191,36,.15);  color: var(--normal); }
.badge--hard  { background: rgba(248,113,113,.15); color: var(--hard); }
.card-page__question { font-size: 22px; font-weight: 700; margin-bottom: 20px; }
.card-page__answer { color: var(--text-muted); line-height: 1.8; white-space: pre-wrap; }
.card-page__code { margin-top: 20px; }
.card-page__code pre { margin: 0; }
.card-page__tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 16px; }
.tag { font-size: 12px; padding: 2px 10px; border-radius: 20px; background: rgba(91,110,245,.15); color: var(--accent); }
.state-msg { color: var(--text-muted); text-align: center; padding: 60px 0; }
</style>
