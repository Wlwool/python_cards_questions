<template>
  <div class="card" :class="`card--${card.difficulty}`" @click="toggle">
    <div class="card__header">
      <span class="card__category">{{ card.category }}</span>
      <span class="card__badge" :class="`badge--${card.difficulty}`">{{ card.difficulty }}</span>
    </div>

    <h3 class="card__question">{{ card.question }}</h3>

    <div v-if="open" class="card__body" @click.stop>
      <p class="card__answer">{{ card.answer }}</p>

      <div v-if="card.code_example" class="card__code">
        <pre><code ref="codeEl" class="language-python">{{ card.code_example }}</code></pre>
      </div>

      <div v-if="card.tags?.length" class="card__tags">
        <span v-for="tag in card.tags" :key="tag" class="tag">{{ tag }}</span>
      </div>
    </div>

    <button class="card__toggle" :aria-label="open ? 'Скрыть' : 'Показать ответ'">
      {{ open ? '▲ Скрыть' : '▼ Показать ответ' }}
    </button>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import hljs from 'highlight.js/lib/core'
import python from 'highlight.js/lib/languages/python'

hljs.registerLanguage('python', python)

const props = defineProps({ card: Object })
const open = ref(false)
const codeEl = ref(null)

function toggle() {
  open.value = !open.value
}

// подсвечивает код после раскрытия карточки
watch(open, async (val) => {
  if (val && props.card.code_example) {
    await nextTick()
    if (codeEl.value && !codeEl.value.dataset.highlighted) {
      hljs.highlightElement(codeEl.value)
    }
  }
})
</script>

<style scoped>
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}

.card:hover {
  background: var(--bg-card-hover);
}

.card__header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.card__category {
  font-size: 12px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.card__badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 20px;
  font-weight: 600;
  margin-left: auto;
}

.badge--easy  { background: rgba(52,211,153,.15); color: var(--easy); }
.badge--normal{ background: rgba(251,191,36,.15);  color: var(--normal); }
.badge--hard  { background: rgba(248,113,113,.15); color: var(--hard); }

.card__question {
  font-size: 16px;
  font-weight: 600;
  line-height: 1.4;
}

.card__body {
  margin-top: 16px;
  border-top: 1px solid var(--border);
  padding-top: 16px;
}

.card__answer {
  color: var(--text-muted);
  white-space: pre-wrap;
  line-height: 1.7;
}

.card__code {
  margin-top: 12px;
}

.card__code pre {
  margin: 0;
}

.card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 12px;
}

.tag {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 20px;
  background: rgba(91,110,245,.15);
  color: var(--accent);
}

.card__toggle {
  margin-top: 14px;
  font-size: 12px;
  color: var(--text-muted);
  background: none;
  border: none;
  padding: 0;
}

.card__toggle:hover {
  color: var(--text);
}
</style>
