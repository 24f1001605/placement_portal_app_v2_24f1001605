<template>
  <nav class="navbar navbar-expand-lg navbar-dark" style="background:#2c3e50">
    <div class="container-fluid px-4">
      <router-link to="/" class="navbar-brand fw-bold fs-5 text-decoration-none text-white">
        Placement Portal
      </router-link>
      <div class="d-flex align-items-center gap-3">
        <span class="text-white opacity-75 small">
          {{ name }}
          <span class="badge ms-2" :class="roleBadge">{{ role }}</span>
        </span>
        <button @click="logout" class="btn btn-light btn-sm fw-semibold">
          Logout
        </button>
      </div>
    </div>
  </nav>
</template>

<script>
import api from '../api'
export default {
  computed: {
    name() { return localStorage.getItem('name') || 'User' },
    role() { return localStorage.getItem('role') || '' },
    roleBadge() {
      const map = { admin: 'bg-danger', company: 'bg-success', student: 'bg-info' }
      return map[this.role] || 'bg-secondary'
    }
  },
  methods: {
    async logout() {
      try { await api.post('/auth/logout') } catch (e) { console.log(e) }
      localStorage.clear()
      this.$router.push('/login')
    }
  }
}
</script>
