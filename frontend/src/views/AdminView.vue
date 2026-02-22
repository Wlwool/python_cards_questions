<template>
  <div class="admin">
    <!-- форма входа -->
    <div v-if="!admin.isLoggedIn" class="login-box">
      <h2>Вход в панель</h2>
      <input
        v-model="password"
        type="password"
        placeholder="Пароль"
        class="input"
        @keyup.enter="doLogin"
      />
      <div v-if="loginError" class="error">{{ loginError }}</div>
      <button class="btn btn--primary" @click="doLogin">Войти</button>
    </div>

    <!-- панель управления -->
    <div v-else>
      <div class="admin-header">
        <h2>Управление карточками</h2>
        <button class="btn" @click="admin.logout()">Выйти</button>
      </div>

      <!-- форма создания/редактирования -->
      <div class="form-box">
        <h3>{{ editId ? 'Редактировать' : 'Новая карточка' }}</h3>

        <label class="label">Вопрос</label>
        <textarea v-model="form.question" class="input" rows="2" />

        <label class="label">Ответ</label>
        <textarea v-model="form.answer" class="input" rows="4" />

        <label class="label">Пример кода (необязательно)</label>
        <textarea v-model="form.code_example" class="input code-input" rows="6" placeholder="def foo(): ..." />

        <div class="form-row">
          <div>
            <label class="label">Категория</label>
            <input v-model="form.category" class="input" />
          </div>
          <div>
            <label class="label">Сложность</label>
            <select v-model="form.difficulty" class="input">
              <option value="easy">Easy</option>
              <option value="normal">Normal</option>
              <option value="hard">Hard</option>
            </select>
          </div>
        </div>

        <label class="label">Теги (через запятую)</label>
        <input v-model="tagsRaw" class="input" placeholder="list, dict, comprehension" />

        <div class="form-actions">
          <button class="btn btn--primary" @click="saveCard">
            {{ editId ? 'Сохранить' : 'Создать' }}
          </button>
          <button v-if="editId" class="btn" @click="cancelEdit">Отмена</button>
        </div>
      </div>

      <!-- список карточек -->
      <div class="cards-list">
        <div v-for="card in cards" :key="card.id" class="card-row">
          <div class="card-row__info">
            <span class="card-row__cat">{{ card.category }}</span>
            <span class="card-row__q">{{ card.question }}</span>
          </div>
          <div class="card-row__actions">
            <button class="btn btn--sm" @click="startEdit(card)">✏️ Ред.</button>
            <button class="btn btn--sm btn--danger" @click="removeCard(card.id)">🗑️</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAdminStore } from '../stores/admin'
import api from '../api'

const admin = useAdminStore()
const password = ref('')
const loginError = ref('')
const cards = ref([])
const editId = ref(null)
const tagsRaw = ref('')

const form = reactive({
  question: '', answer: '', code_example: '',
  category: '', difficulty: 'normal',
})

async function doLogin() {
  loginError.value = ''
  try {
    await admin.login(password.value)
    loadCards()
  } catch {
    loginError.value = 'Неверный пароль'
  }
}

async function loadCards() {
  const { data } = await api.get('/cards', { params: { per_page: 100 } })
  cards.value = data.items
}

async function saveCard() {
  const payload = {
    ...form,
    code_example: form.code_example || null,
    tags: tagsRaw.value.split(',').map(t => t.trim()).filter(Boolean),
  }
  if (editId.value) {
    await api.put(`/admin/cards/${editId.value}`, payload)
  } else {
    await api.post('/admin/cards', payload)
  }
  cancelEdit()
  loadCards()
}

function startEdit(card) {
  editId.value = card.id
  Object.assign(form, {
    question: card.question,
    answer: card.answer,
    code_example: card.code_example || '',
    category: card.category,
    difficulty: card.difficulty,
  })
  tagsRaw.value = (card.tags || []).join(', ')
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function cancelEdit() {
  editId.value = null
  Object.assign(form, { question: '', answer: '', code_example: '', category: '', difficulty: 'normal' })
  tagsRaw.value = ''
}

async function removeCard(id) {
  if (!confirm('Удалить карточку?')) return
  await api.delete(`/admin/cards/${id}`)
  loadCards()
}

onMounted(() => {
  if (admin.isLoggedIn) loadCards()
})
</script>

<style scoped>
.admin { max-width: 860px; }

.login-box {
  max-width: 360px;
  margin: 60px auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.form-box {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 32px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.form-row > div {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.label { font-size: 13px; color: var(--text-muted); }

.input {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text);
  padding: 8px 12px;
  font-size: 14px;
  font-family: var(--font);
  outline: none;
  width: 100%;
  resize: vertical;
}

.input:focus { border-color: var(--accent); }

.code-input { font-family: monospace; }

.form-actions { display: flex; gap: 10px; margin-top: 6px; }

.btn {
  padding: 8px 18px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text);
  font-size: 14px;
  transition: all 0.15s;
}

.btn:hover { border-color: var(--accent); }
.btn--primary { background: var(--accent); border-color: var(--accent); color: white; }
.btn--primary:hover { background: var(--accent-hover); }
.btn--danger { color: var(--hard); }
.btn--danger:hover { border-color: var(--hard); }
.btn--sm { padding: 4px 10px; font-size: 12px; }

.error { color: var(--hard); font-size: 13px; }

.cards-list { display: flex; flex-direction: column; gap: 8px; }

.card-row {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.card-row__info { display: flex; gap: 10px; align-items: baseline; overflow: hidden; }
.card-row__cat { font-size: 11px; color: var(--text-muted); white-space: nowrap; }
.card-row__q { font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.card-row__actions { display: flex; gap: 6px; flex-shrink: 0; }
</style>
