<template>
  <div class="app">
    <header class="navbar">
      <RouterLink to="/" class="navbar__logo">🐍 Python Cards</RouterLink>
      <nav class="navbar__links">
        <RouterLink to="/">Карточки</RouterLink>
        <RouterLink to="/admin" class="navbar__admin">Admin</RouterLink>
      </nav>
    </header>
    <main class="main">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 32px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-card);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar__logo {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
}

.navbar__links {
  display: flex;
  gap: 24px;
}

.navbar__links a {
  color: var(--text-muted);
  transition: color 0.2s;
}

.navbar__links a:hover,
.navbar__links a.router-link-active {
  color: var(--text);
}

.navbar__admin {
  border: 1px solid var(--border);
  padding: 4px 12px;
  border-radius: 6px;
}

.main {
  flex: 1;
  padding: 32px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}
</style>
