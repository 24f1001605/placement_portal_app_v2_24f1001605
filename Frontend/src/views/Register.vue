<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center py-4" style="background:#2c3e50">
    <div class="card p-4 shadow-lg" style="width:480px">
      <div class="text-center mb-3">
        <h3 class="fw-bold">Register</h3>
      </div>

      <!-- Role Switch -->
      <div class="btn-group w-100 mb-4">
        <button @click="role='student'" :class="['btn', role==='student' ? 'btn-primary' : 'btn-outline-primary']">
          Student
        </button>
        <button @click="role='company'" :class="['btn', role==='company' ? 'btn-primary' : 'btn-outline-primary']">
          Company
        </button>
      </div>

      <div v-if="msg" :class="['alert', success ? 'alert-success' : 'alert-danger', 'py-2']">{{ msg }}</div>

      <form @submit.prevent="register">
        <div class="row g-2">
          <div class="col-12">
            <input v-model="form.name" class="form-control" :placeholder="role==='company' ? 'Company Name *' : 'Full Name *'" required />
          </div>
          <div class="col-12">
            <input v-model="form.email" type="email" class="form-control" placeholder="Email *" required />
          </div>
          <div class="col-12">
            <input v-model="form.password" type="password" class="form-control" placeholder="Password *" required minlength="6" />
          </div>

          <!-- Student Fields -->
          <template v-if="role==='student'">
            <div class="col-6">
              <input v-model="form.branch" class="form-control" placeholder="Branch (e.g. CSE,ES,DS)" />
            </div>
            <div class="col-6">
              <input v-model="form.cgpa" type="number" step="0.01" min="0" max="10" class="form-control" placeholder="CGPA" />
            </div>
            <div class="col-6">
              <select v-model="form.year" class="form-select">
                <option value="">Year</option>
                <option v-for="y in [1,2,3,4]" :key="y" :value="y">Year {{ y }}</option>
              </select>
            </div>
            <div class="col-6">
              <input v-model="form.contact" class="form-control" placeholder="Contact No." />
            </div>
            <div class="col-12">
              <input v-model="form.skills" class="form-control" placeholder="Skills (comma separated)" />
            </div>
            <div class="col-12">
              <input v-model="form.address" class="form-control" placeholder="Address" />
            </div>
          </template>

          <!-- Company Fields -->
          <template v-else>
            <div class="col-6">
              <input v-model="form.industry" class="form-control" placeholder="Industry" />
            </div>
            <div class="col-6">
              <input v-model="form.location" class="form-control" placeholder="Location" />
            </div>
            <div class="col-6">
              <input v-model="form.website" class="form-control" placeholder="Website" />
            </div>
            <div class="col-6">
              <input v-model="form.hr_contact" class="form-control" placeholder="HR Contact" />
            </div>
            <div class="col-12">
              <textarea v-model="form.description" class="form-control" rows="2" placeholder="Company description"></textarea>
            </div>
          </template>

          <div class="col-12 mt-2">
            <button type="submit" class="btn btn-primary w-100 py-2 fw-bold" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              {{ loading ? 'Registering...' : 'Register' }}
            </button>
          </div>
        </div>
      </form>

      <p class="text-center text-muted mt-3 mb-0">
        Already have an account? <router-link to="/login" class="text-primary fw-semibold">Login</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import api from '../api'
export default {
  data() {
    return {
      role: 'student',
      form: { name:'', email:'', password:'', branch:'', cgpa:'', year:'', contact:'', skills:'', address:'', industry:'', location:'', website:'', hr_contact:'', description:'' },
      msg: '', success: false, loading: false
    }
  },
  methods: {
    async register() {
      this.loading = true; this.msg = ''
      try {
        const url = this.role === 'student' ? '/auth/register/student' : '/auth/register/company'
        await api.post(url, this.form)
        this.success = true
        this.msg = this.role === 'company'
          ? 'Company registered! Awaiting admin approval.'
          : 'Registered successfully! You can now login.'
        setTimeout(() => this.$router.push('/login'), 2000)
      } catch (e) {
        this.success = false
        this.msg = e.response?.data?.message || 'Registration failed'
      } finally { this.loading = false }
    }
  }
}
</script>
