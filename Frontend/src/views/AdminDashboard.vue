<template>
  <div style="background: #f4f6f9; min-height: 100vh;">
    <Navbar />
    <div class="container-fluid p-4">

      <ul class="nav nav-tabs mb-4 fw-semibold">
        <li class="nav-item" v-for="tab in tabs" :key="tab.key">
          <button @click="switchTab(tab.key)" :class="['nav-link', activeTab===tab.key ? 'active' : '']">
            {{ tab.label }}
          </button>
        </li>
      </ul>

      <!-- OVERVIEW -->
      <div v-if="activeTab==='overview'">
        <div class="row g-3 mb-4">
          <div class="col-6 col-md-4 col-lg-2" v-for="stat in stats" :key="stat.label">
            <div class="card p-3 text-center h-100">
              <h3 class="fw-bold mb-0 text-primary">{{ stat.value }}</h3>
              <small class="text-muted">{{ stat.label }}</small>
            </div>
          </div>
        </div>

      </div>

      <!-- COMPANIES -->
      <div v-if="activeTab==='companies'">
        <div class="d-flex gap-2 mb-3 flex-wrap align-items-center">
          <input v-model="companySearch" @input="loadCompanies" class="form-control" style="max-width:280px" placeholder="Search companies by name..." />
          <span class="badge bg-secondary">{{ companies.length }} found</span>
        </div>
        <div v-if="actionMsg" class="alert alert-success py-2 small">{{ actionMsg }}</div>
        <div class="table-responsive">
          <table class="table table-hover align-middle bg-white rounded shadow-sm">
            <thead class="table-dark">
              <tr><th>Company</th><th>Industry</th><th>Email</th><th>Approval</th><th>Active</th><th>Actions</th></tr>
            </thead>
            <tbody>
              <tr v-for="c in companies" :key="c.id">
                <td>
                  <b>{{ c.name }}</b><br>
                  <small class="text-muted">{{ c.location }}</small>
                </td>
                <td>{{ c.industry || '-' }}</td>
                <td><small>{{ c.email }}</small></td>
                <td><span :class="statusBadge(c.approval_status)">{{ c.approval_status }}</span></td>
                <td>
                  <span :class="c.is_active ? 'badge bg-success' : 'badge bg-danger'">
                    {{ c.is_active ? 'Active' : 'Blacklisted' }}
                  </span>
                </td>
                <td>
                  <button v-if="c.approval_status==='Pending'" @click="approveCompany(c.id)" class="btn btn-success btn-sm me-1">Approve</button>
                  <button v-if="c.approval_status==='Pending'" @click="rejectCompany(c.id)" class="btn btn-danger btn-sm me-1">Reject</button>
                  <button @click="toggleCompany(c.id)" :class="['btn btn-sm', c.is_active ? 'btn-warning' : 'btn-secondary']">
                    {{ c.is_active ? 'Blacklist' : 'Activate' }}
                  </button>
                </td>
              </tr>
              <tr v-if="!companies.length">
                <td colspan="6" class="text-center text-muted py-4">No companies found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- STUDENTS -->
      <div v-if="activeTab==='students'">
        <div class="d-flex gap-2 mb-3 flex-wrap align-items-center">
          <input v-model="studentSearch" @input="loadStudents" class="form-control" style="max-width:280px" placeholder="Search students by name..." />
          <span class="badge bg-secondary">{{ students.length }} found</span>
        </div>
        <div v-if="actionMsg" class="alert alert-success py-2 small">{{ actionMsg }}</div>
        <div class="table-responsive">
          <table class="table table-hover align-middle bg-white rounded shadow-sm">
            <thead class="table-dark">
              <tr><th>Name</th><th>Branch</th><th>CGPA</th><th>Year</th><th>Email</th><th>Status</th><th>Action</th></tr>
            </thead>
            <tbody>
              <tr v-for="s in students" :key="s.id">
                <td><b>{{ s.name }}</b></td>
                <td>{{ s.branch || '-' }}</td>
                <td><span class="badge bg-primary">{{ s.cgpa }}</span></td>
                <td>Year {{ s.year }}</td>
                <td><small>{{ s.email }}</small></td>
                <td>
                  <span :class="s.is_active ? 'badge bg-success' : 'badge bg-danger'">
                    {{ s.is_active ? 'Active' : 'Deactivated' }}
                  </span>
                </td>
                <td>
                  <button @click="toggleStudent(s.id)" :class="['btn btn-sm', s.is_active ? 'btn-warning' : 'btn-secondary']">
                    {{ s.is_active ? 'Deactivate' : 'Activate'}}
                  </button>
                </td>
              </tr>
              <tr v-if="!students.length">
                <td colspan="7" class="text-center text-muted py-4">No students found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- DRIVES -->
      <div v-if="activeTab==='drives'">
        <div v-if="actionMsg" class="alert alert-success py-2 small mb-3">{{ actionMsg }}</div>
        <div class="table-responsive">
          <table class="table table-hover align-middle bg-white rounded shadow-sm">
            <thead class="table-dark">
              <tr><th>Job Title</th><th>Company</th><th>Salary</th><th>Deadline</th><th>Applicants</th><th>Status</th><th>Actions</th></tr>
            </thead>
            <tbody>
              <tr v-for="d in drives" :key="d.id">
                <td><b>{{ d.job_title }}</b></td>
                <td>{{ d.company }}</td>
                <td>{{ d.salary ? Number(d.salary).toLocaleString('en-IN') : 'N/A' }}</td>
                <td>{{ d.deadline ? new Date(d.deadline).toLocaleDateString('en-IN') : 'N/A' }}</td>
                <td><span class="badge bg-info text-dark">{{ d.applicants }}</span></td>
                <td><span :class="statusBadge(d.status)">{{ d.status }}</span></td>
                <td>
                  <button v-if="d.status==='Pending'" @click="approveDrive(d.id)" class="btn btn-success btn-sm me-1">Approve</button>
                  <button v-if="d.status==='Pending'" @click="rejectDrive(d.id)" class="btn btn-danger btn-sm">Reject</button>
                  <span v-if="d.status!=='Pending'" class="text-muted small">-</span>
                </td>
              </tr>
              <tr v-if="!drives.length">
                <td colspan="7" class="text-center text-muted py-4">No drives found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- APPLICATIONS -->
      <div v-if="activeTab==='applications'">
        <div class="table-responsive">
          <table class="table table-hover align-middle bg-white rounded shadow-sm">
            <thead class="table-dark">
              <tr><th>S.NO</th><th>Student</th><th>Drive</th><th>Company</th><th>Status</th><th>Applied On</th></tr>
            </thead>
            <tbody>
              <tr v-for="a in applications" :key="a.id">
                <td>{{ a.id }}</td>
                <td>{{ a.student }}</td>
                <td>{{ a.drive }}</td>
                <td>{{ a.company }}</td>
                <td><span :class="appBadge(a.status)">{{ a.status }}</span></td>
                <td>{{ new Date(a.applied_at).toLocaleDateString('en-IN') }}</td>
              </tr>
              <tr v-if="!applications.length">
                <td colspan="6" class="text-center text-muted py-4">No applications found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- PLACED STUDENTS -->
      <div v-if="activeTab==='placed'">
        <div class="table-responsive">
          <table class="table table-hover align-middle bg-white rounded shadow-sm">
            <thead class="table-dark">
              <tr><th>Student</th><th>Drive</th><th>Company</th><th>Salary</th><th>Placed On</th></tr>
            </thead>
            <tbody>
              <tr v-for="p in placedStudents" :key="p.id">
                <td><b>{{ p.student }}</b></td>
                <td>{{ p.drive }}</td>
                <td>{{ p.company }}</td>
                <td>{{ p.salary ? Number(p.salary).toLocaleString('en-IN') : 'N/A' }}</td>
                <td>{{ new Date(p.placed_on).toLocaleDateString('en-IN') }}</td>
              </tr>
              <tr v-if="!placedStudents.length">
                <td colspan="5" class="text-center text-muted py-4">No students placed yet</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import Navbar from '../components/Navbar.vue'
import api from '../api'


export default {
  components: { Navbar },
  data() {
    return {
      activeTab: 'overview',
      tabs: [
        { key: 'overview', label: 'Overview', icon: 'bi-speedometer2' },
        { key: 'companies', label: 'Companies', icon: 'bi-building' },
        { key: 'students', label: 'Students', icon: 'bi-people' },
        { key: 'drives', label: 'Drives', icon: 'bi-briefcase' },
        { key: 'applications', label: 'Applications', icon: 'bi-file-earmark-text' },
        { key: 'placed', label: 'Placement History', icon: 'bi-trophy' }
      ],
      stats: [],
      companies: [],
      students: [],
      drives: [],
      applications: [],
      placedStudents: [],
      companySearch: '',
      studentSearch: '',
      actionMsg: '',

    }
  },
  async mounted() {
    await this.loadDashboard()
  },
  methods: {
    async switchTab(val) {
      this.activeTab = val
      this.actionMsg = ''
      if (val === 'companies') await this.loadCompanies()
      else if (val === 'students') await this.loadStudents()
      else if (val === 'drives') await this.loadDrives()
      else if (val === 'applications') await this.loadApplications()
      else if (val === 'placed') await this.loadPlacedStudents()
    },
    async loadDashboard() {
      try {
        const res = await api.get('/admin/dashboard')
        const d = res.data
        this.stats = [
          { label: 'Students', value: d.total_students, icon: 'bi-people-fill', color: '#667eea' },
          { label: 'Companies', value: d.total_companies, icon: 'bi-building-fill', color: '#28a745' },
          { label: 'Drives', value: d.total_drives, icon: 'bi-briefcase-fill', color: '#fd7e14' },
          { label: 'Applications', value: d.total_applications, icon: 'bi-file-earmark-fill', color: '#dc3545' },
          { label: 'Placed Students', value: d.placed_students, icon: 'bi-trophy-fill', color: '#28a745' },
          { label: 'Pending Companies', value: d.pending_companies, icon: 'bi-hourglass-split', color: '#ffc107' },
          { label: 'Pending Drives', value: d.pending_drives, icon: 'bi-clock-history', color: '#6f42c1' }
        ]

      } catch (e) {
        console.error('Admin dashboard load error:', e)
      }
    },

    async loadCompanies() {
      const res = await api.get('/admin/companies', { params: { q: this.companySearch } })
      this.companies = res.data
    },
    async loadStudents() {
      const res = await api.get('/admin/students', { params: { q: this.studentSearch } })
      this.students = res.data
    },
    async loadDrives() {
      const res = await api.get('/admin/drives')
      this.drives = res.data
    },
    async loadApplications() {
      const res = await api.get('/admin/applications')
      this.applications = res.data
    },
    async loadPlacedStudents() {
      const res = await api.get('/admin/placed-students')
      this.placedStudents = res.data
    },
    async approveCompany(id) {
      await api.post(`/admin/companies/${id}/approve`)
      this.actionMsg = 'Company approved!'
      await this.loadCompanies()
      setTimeout(() => { this.actionMsg = '' }, 3000)
    },
    async rejectCompany(id) {
      await api.post(`/admin/companies/${id}/reject`)
      this.actionMsg = 'Company rejected.'
      await this.loadCompanies()
      setTimeout(() => { this.actionMsg = '' }, 3000)
    },
    async toggleCompany(id) {
      await api.post(`/admin/companies/${id}/toggle`)
      this.actionMsg = 'Company status updated.'
      await this.loadCompanies()
      setTimeout(() => { this.actionMsg = '' }, 3000)
    },
    async toggleStudent(id) {
      await api.post(`/admin/students/${id}/toggle`)
      this.actionMsg = 'Student status updated.'
      await this.loadStudents()
      setTimeout(() => { this.actionMsg = '' }, 3000)
    },
    async approveDrive(id) {
      await api.post(`/admin/drives/${id}/approve`)
      this.actionMsg = 'Drive approved!'
      await this.loadDrives()
      setTimeout(() => { this.actionMsg = '' }, 3000)
    },
    async rejectDrive(id) {
      await api.post(`/admin/drives/${id}/reject`)
      this.actionMsg = 'Drive rejected.'
      await this.loadDrives()
      setTimeout(() => { this.actionMsg = '' }, 3000)
    },
    statusBadge(s) {
      const map = { 'Approved': 'badge bg-success', 'Pending': 'badge bg-warning text-dark', 'Rejected': 'badge bg-danger', 'Closed': 'badge bg-secondary' }
      return map[s] || 'badge bg-secondary'
    },
    appBadge(s) {
      const map = { 'Applied': 'badge bg-primary', 'Shortlisted': 'badge bg-warning text-dark', 'Selected': 'badge bg-success', 'Rejected': 'badge bg-danger' }
      return map[s] || 'badge bg-secondary'
    }
  }
}
</script>
