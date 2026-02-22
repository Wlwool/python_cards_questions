import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import CardView from '../views/CardView.vue'
import AdminView from '../views/AdminView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomeView },
    { path: '/cards/:id', component: CardView },
    { path: '/admin', component: AdminView },
  ],
})

export default router
