<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center" style="background:#2c3e50">
    <div class="card p-4 shadow-lg" style="width:420px">
      <div class="text-center mb-4">
        <h4 class="fw-bold mt-2 mb-3">Welcome to Placement Portal</h4>
        <p class="text-muted">Sign in to your account</p>
      </div>
      <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
      <form @submit.prevent="login">
        <div class="mb-3">
          <label class="form-label fw-semibold">Email</label>
          <input v-model="email" type="email" class="form-control" placeholder="you@gmail.com" required />
        </div>
        <div class="mb-3">
          <label class="form-label fw-semibold">Password</label>
          <input v-model="password" type="password" class="form-control" placeholder="••••••••" required />
        </div>
        <button type="submit" class="btn btn-primary w-100 py-2 fw-bold" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          {{ loading ? 'Signing in...' : 'Login' }}
        </button>
      </form>
      <hr/>
      <p class="text-center text-muted mb-0">
        New here?
        <router-link to="/register" class="text-primary fw-semibold">Register</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import api from '../api'
export default {
  data() { return { email: '', password: '', error: '', loading: false } },
  methods: {
    async login() {
      this.loading = true; this.error = ''
      try {
        const res = await api.post('/auth/login', { email: this.email, password: this.password })
        const d = res.data
        localStorage.setItem('token', d.token)
        localStorage.setItem('role', d.role)
        localStorage.setItem('name', d.name)
        localStorage.setItem('email', d.email)
        if (d.company_id) localStorage.setItem('company_id', d.company_id)
        if (d.student_id) localStorage.setItem('student_id', d.student_id)
        const routes = { admin: '/admin', company: '/company', student: '/student' }
        this.$router.push(routes[d.role] || '/login')
      } catch (e) {
        this.error = e.response?.data?.message || 'Login failed'
      } finally { this.loading = false }
    }
  }
}
</script>
