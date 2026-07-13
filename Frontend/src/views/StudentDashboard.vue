<template>
  <div style="background: #f4f6f9; min-height: 100vh;">
    <Navbar />
    <div class="container-fluid p-4">

      <ul class="nav nav-tabs mb-4 fw-semibold">
        <li class="nav-item" v-for="tab in tabs" :key="tab.key">
          <button @click="switchTab(tab.key)" :class="['nav-link', activeTab===tab.key ? 'active':'']">
            {{ tab.label }}
          </button>
        </li>
      </ul>

      <!-- OVERVIEW -->
      <div v-if="activeTab==='overview'">
        <div class="row g-3 mb-4">
          <div class="col-6 col-md-3" v-for="s in statsCards" :key="s.label">
            <div class="card p-3 text-center">
              
              <h3 class="fw-bold mb-0">{{ s.value }}</h3>
              <small class="text-muted">{{ s.label }}</small>
            </div>
          </div>
        </div>

        <!-- Profile Card -->
        <div class="card p-4 mb-4" v-if="student">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h6 class="fw-bold mb-0">My Profile</h6>
            <button @click="editMode=!editMode" class="btn btn-outline-primary btn-sm">
              {{ editMode ? 'Cancel' : 'Edit' }}
            </button>
          </div>
          <div v-if="!editMode" class="row g-2">
            <div class="col-md-4"><small class="text-muted">Name</small><p class="fw-semibold mb-1">{{ student.name }}</p></div>
            <div class="col-md-4"><small class="text-muted">Branch</small><p class="fw-semibold mb-1">{{ student.branch || '-' }}</p></div>
            <div class="col-md-4"><small class="text-muted">Year</small><p class="fw-semibold mb-1">Year {{ student.year }}</p></div>
            <div class="col-md-4"><small class="text-muted">CGPA</small><p class="fw-semibold mb-1">{{ student.cgpa }}</p></div>
            <div class="col-md-4"><small class="text-muted">Contact</small><p class="fw-semibold mb-1">{{ student.contact || '-' }}</p></div>
            <div class="col-md-8"><small class="text-muted">Email</small><p class="fw-semibold mb-1">{{ student.email }}</p></div>
            <div class="col-12"><small class="text-muted">Skills</small><p class="fw-semibold mb-0">{{ student.skills || '-' }}</p></div>
          </div>
          <div v-else class="row g-2">
            <div class="col-md-4"><input v-model="editForm.name" class="form-control" placeholder="Full Name" /></div>
            <div class="col-md-4"><input v-model="editForm.branch" class="form-control" placeholder="Branch" /></div>
            <div class="col-md-4"><input v-model="editForm.cgpa" type="number" step="0.01" min="0" max="10" class="form-control" placeholder="CGPA" /></div>
            <div class="col-md-4">
              <select v-model="editForm.year" class="form-select">
                <option v-for="y in [1,2,3,4]" :key="y" :value="y">Year {{ y }}</option>
              </select>
            </div>
            <div class="col-md-4"><input v-model="editForm.contact" class="form-control" placeholder="Contact" /></div>
            <div class="col-12"><input v-model="editForm.skills" class="form-control" placeholder="Skills (e.g. Python, Java, SQL)" /></div>
            <div class="col-12">
              <button @click="saveProfile" class="btn btn-primary btn-sm me-2">
                Save Changes
              </button>
              <span v-if="profileMsg" class="text-success small fw-semibold">{{ profileMsg }}</span>
            </div>
          </div>
        </div>

        <!-- Resume Upload Card -->
        <div class="card p-4">
          <h6 class="fw-bold mb-3">My Resume</h6>

          <!-- Current resume status -->
          <div v-if="student && student.resume_url" class="d-flex align-items-center gap-3 mb-3 p-3 bg-success bg-opacity-10 rounded">
            
            <div>
              <div class="fw-semibold text-success">Resume uploaded</div>
              <small class="text-muted">{{ student.resume_url }}</small>
            </div>
            <button @click="viewMyResume" class="btn btn-outline-success btn-sm ms-auto">
              View
            </button>
          </div>
          <div v-else class="d-flex align-items-center gap-3 mb-3 p-3 bg-warning bg-opacity-10 rounded">
            
            <div>
              <div class="fw-semibold text-warning">No resume uploaded</div>
              <small class="text-muted">Companies can view your resume when you apply</small>
            </div>
          </div>

          <!-- Upload form -->
          <div class="d-flex gap-2 align-items-center flex-wrap">
            <input
              type="file"
              ref="resumeInput"
              @change="onResumeSelected"
              accept=".pdf,.doc,.docx"
              class="form-control"
              style="max-width:320px"
            />
            <button
              @click="uploadResume"
              :disabled="!selectedResume || resumeUploading"
              class="btn btn-primary btn-sm"
            >
              <span v-if="resumeUploading" class="spinner-border spinner-border-sm me-1"></span>
              
              {{ resumeUploading ? 'Uploading...' : student && student.resume_url ? 'Replace Resume' : 'Upload Resume' }}
            </button>
          </div>
          <small class="text-muted mt-2 d-block">Accepted: PDF, DOC, DOCX (max 5MB)</small>
          <div v-if="resumeMsg" :class="['mt-2 small fw-semibold', resumeOk ? 'text-success' : 'text-danger']">
            {{ resumeMsg }}
          </div>
        </div>
      </div>

      <!-- DRIVES -->
      <div v-if="activeTab==='drives'">
        <div class="d-flex gap-2 mb-3 flex-wrap align-items-center">
          <input v-model="search" @input="loadDrives" class="form-control" style="max-width:300px" placeholder="Search by job title or branch..." />
          <span class="badge bg-secondary">{{ drives.length }} drives found</span>
        </div>
        <div v-if="applyMsg" :class="['alert py-2', applyOk ? 'alert-success':'alert-danger']">{{ applyMsg }}</div>

        <div class="row g-3">
          <div class="col-md-6 col-lg-4" v-for="d in drives" :key="d.id">
            <div class="card p-3 h-100" :class="{ 'border-success': d.eligible && !d.already_applied, 'border-warning': d.already_applied, 'border-danger': !d.eligible }">
              <div class="d-flex justify-content-between align-items-start mb-2">
                <div>
                  <h6 class="fw-bold mb-0">{{ d.job_title }}</h6>
                  <small class="text-muted">{{ d.company }}</small>
                </div>
                <span v-if="d.already_applied" class="badge bg-success">Applied</span>
                <span v-else-if="!d.eligible" class="badge bg-danger">Not Eligible</span>
                <span v-else class="badge bg-primary">Open</span>
              </div>
              <p class="small text-muted mb-2" style="max-height:48px;overflow:hidden">{{ d.job_description || 'No description.' }}</p>
              <div class="row g-1 small mb-2">
                <div class="col-6 text-muted">Salary: <b class="text-dark">{{ d.salary ? Number(d.salary).toLocaleString('en-IN') : 'N/A' }}</b></div>
                <div class="col-6 text-muted">Min CGPA: <b class="text-dark">{{ d.min_cgpa || 'None' }}</b></div>
                <div class="col-6 text-muted">Branches: <b class="text-dark">{{ d.eligible_branches || 'All' }}</b></div>
                <div class="col-6 text-muted">Location: <b class="text-dark">{{ d.location || 'N/A' }}</b></div>
                <div class="col-12 text-muted">Deadline: <b class="text-dark">{{ d.deadline ? new Date(d.deadline).toLocaleDateString('en-IN') : 'No Deadline' }}</b></div>
              </div>
              <button
                @click="applyDrive(d)"
                :disabled="d.already_applied || !d.eligible || applyingId===d.id"
                :class="['btn btn-sm w-100 fw-semibold', d.already_applied ? 'btn-success' : d.eligible ? 'btn-primary' : 'btn-secondary']"
              >
                <span v-if="applyingId===d.id" class="spinner-border spinner-border-sm me-1"></span>
                
                {{ d.already_applied ? 'Already Applied' : d.eligible ? 'Apply Now' : 'Not Eligible' }}
              </button>
            </div>
          </div>
          <div v-if="!drives.length" class="col-12 text-center text-muted py-5">
            No drives available right now
          </div>
        </div>
      </div>

      <!-- MY APPLICATIONS -->
      <div v-if="activeTab==='history'">
        <div class="d-flex justify-content-between mb-3 align-items-center">
          <h5 class="fw-bold mb-0">My Application History</h5>
          <button @click="exportCSV" class="btn btn-outline-success btn-sm">
            Export CSV
          </button>
        </div>
        <div v-if="exportMsg" class="alert alert-info py-2 small">{{ exportMsg }}</div>



        <div class="table-responsive">
          <table class="table table-hover align-middle bg-white rounded shadow-sm">
            <thead class="table-dark">
              <tr><th>Drive</th><th>Company</th><th>Salary</th><th>Applied On</th><th>Interview Date</th><th>Company Feedback</th><th>Status</th></tr>
            </thead>
            <tbody>
              <tr v-for="a in applications" :key="a.id">
                <td><b>{{ a.job_title }}</b></td>
                <td>{{ a.company }}</td>
                <td>{{ a.salary ? Number(a.salary).toLocaleString('en-IN') : 'N/A' }}</td>
                <td>{{ new Date(a.applied_at).toLocaleDateString('en-IN') }}</td>
                <td>
                  <span v-if="a.interview_date" class="badge bg-info text-dark">
                    {{ new Date(a.interview_date).toLocaleDateString('en-IN') }}
                  </span>
                  <span v-else class="text-muted">-</span>
                </td>
                <td>
                  <span v-if="a.feedback" class="text-dark small">
                    {{ a.feedback }}
                  </span>
                  <span v-else class="text-muted small">No feedback yet</span>
                </td>
                <td><span :class="appBadge(a.status)">{{ a.status }}</span></td>
              </tr>
              <tr v-if="!applications.length">
                <td colspan="7" class="text-center text-muted py-4">
                  No applications yet
                </td>
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
import axios from 'axios'


export default {
  components: { Navbar },
  data() {
    return {
      activeTab: 'overview',
      tabs: [
        { key: 'overview', label: 'Overview', icon: 'bi-speedometer2' },
        { key: 'drives', label: 'Browse Drives', icon: 'bi-briefcase' },
        { key: 'history', label: 'My Applications', icon: 'bi-clock-history' }
      ],
      student: null,
      statsCards: [],
      drives: [],
      applications: [],
      search: '',
      editMode: false,
      editForm: {},
      profileMsg: '',
      exportMsg: '',
      applyMsg: '',
      applyOk: false,
      applyingId: null,

      // Resume
      selectedResume: null,
      resumeUploading: false,
      resumeMsg: '',
      resumeOk: false
    }
  },
  computed: {
  },
  async mounted() {
    await this.loadDashboard()
  },
  methods: {
    async loadDashboard() {
      try {
        const res = await api.get('/student/dashboard')
        const d = res.data
        this.student = d.student
        this.editForm = { ...d.student }
        this.statsCards = [
          { label: 'Total Applied', value: d.total_applications, icon: 'bi-file-earmark-text', color: '#667eea' },
          { label: 'Shortlisted', value: d.shortlisted, icon: 'bi-star-fill', color: '#ffc107' },
          { label: 'Selected', value: d.selected, icon: 'bi-trophy-fill', color: '#28a745' },
          { label: 'My CGPA', value: d.student.cgpa, icon: 'bi-bar-chart-fill', color: '#dc3545' }
        ]
      } catch (e) {
        console.error('Dashboard load error:', e)
      }
    },
    async switchTab(key) {
      this.activeTab = key
      this.applyMsg = ''
      if (key === 'drives') await this.loadDrives()
      else if (key === 'history') await this.loadApplications()
    },
    async loadDrives() {
      try {
        const res = await api.get('/student/drives', { params: { q: this.search } })
        this.drives = res.data
      } catch (e) {
        console.error('Load drives error:', e)
      }
    },
    async applyDrive(drive) {
      if (!confirm(`Apply for "${drive.job_title}" at ${drive.company}?\n\nClick OK to confirm.`)) return
      this.applyingId = drive.id
      this.applyMsg = ''
      try {
        await api.post(`/student/apply/${drive.id}`)
        drive.already_applied = true
        this.applyOk = true
        this.applyMsg = `Successfully applied for ${drive.job_title} at ${drive.company}!`
      } catch (e) {
        this.applyOk = false
        this.applyMsg = '' + (e.response?.data?.message || 'Could not apply.')
      } finally {
        this.applyingId = null
        setTimeout(() => { this.applyMsg = '' }, 4000)
      }
    },
    async loadApplications() {
      try {
        const res = await api.get('/student/applications')
        this.applications = res.data
      } catch (e) {
        console.error('Load applications error:', e)
      }
    },

    async saveProfile() {
      try {
        await api.put('/student/profile', this.editForm)
        this.profileMsg = 'Profile saved!'
        this.editMode = false
        await this.loadDashboard()
        setTimeout(() => { this.profileMsg = '' }, 3000)
      } catch (e) {
        this.profileMsg = 'Failed to save.'
      }
    },
    onResumeSelected(event) {
      this.selectedResume = event.target.files[0] || null
      this.resumeMsg = ''
    },
    async uploadResume() {
      if (!this.selectedResume) return
      this.resumeUploading = true
      this.resumeMsg = ''
      try {
        const formData = new FormData()
        formData.append('resume', this.selectedResume)
        const token = localStorage.getItem('token')
        const res = await fetch('http://localhost:5001/api/student/resume/upload', {
          method: 'POST',
          headers: { 'Authentication-Token': token },
          body: formData
        })
        const data = await res.json()
        if (res.ok) {
          this.resumeOk = true
          this.resumeMsg = '' + data.message
          this.student.resume_url = data.resume_url
          this.selectedResume = null
          if (this.$refs.resumeInput) this.$refs.resumeInput.value = ''
        } else {
          this.resumeOk = false
          this.resumeMsg = '' + data.message
        }
      } catch (e) {
        this.resumeOk = false
        this.resumeMsg = 'Upload failed. Please try again.'
      } finally {
        this.resumeUploading = false
      }
    },
    async viewMyResume() {
      if (!this.student || !this.student.resume_url) return
      try {
        const res = await api.get(`/student/resume/download/${this.student.id}`, { responseType: 'blob' })
        let type = 'application/pdf'
        if (this.student.resume_url.endsWith('.doc')) type = 'application/msword'
        else if (this.student.resume_url.endsWith('.docx')) type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        
        const url = window.URL.createObjectURL(new Blob([res.data], { type }))
        window.open(url, '_blank')
      } catch (e) {
        alert('Failed to load resume. It may have been deleted.')
      }
    },
    async exportCSV() {
      try {
        const token = localStorage.getItem('token')
        const response = await axios.post('http://localhost:5001/api/student/export', {}, {
          headers: {
            'Authentication-Token': token
          },
          responseType: 'blob'
        })
        // Create download link for CSV
        const url = window.URL.createObjectURL(new Blob([response.data], { type: 'text/csv' }))
        const link = document.createElement('a')
        link.href = url
        link.download = 'my_applications.csv'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        this.exportMsg = 'CSV downloaded! You will also receive an email notification.'
        setTimeout(() => { this.exportMsg = '' }, 6000)
      } catch (e) {
        console.error('Export error:', e)
        this.exportMsg = 'Export failed. Please try again.'
        setTimeout(() => { this.exportMsg = '' }, 5000)
      }
    },
    appBadge(s) {
      const map = { 'Applied': 'badge bg-primary', 'Shortlisted': 'badge bg-warning text-dark', 'Selected': 'badge bg-success', 'Rejected': 'badge bg-danger' }
      return map[s] || 'badge bg-secondary'
    }
  }
}
</script>
