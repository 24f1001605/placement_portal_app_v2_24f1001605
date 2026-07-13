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
          <div class="col-6 col-md-3" v-for="s in summaryStats" :key="s.label">
            <div class="card p-3 text-center">
              
              <h3 class="fw-bold mb-0">{{ s.value }}</h3>
              <small class="text-muted">{{ s.label }}</small>
            </div>
          </div>
        </div>
        <div class="card p-4" v-if="company">
          <h6 class="fw-bold mb-3">Company Profile</h6>
          <div class="row g-2">
            <div class="col-md-6"><small class="text-muted">Company Name</small><p class="mb-1 fw-semibold">{{ company.name }}</p></div>
            <div class="col-md-6"><small class="text-muted">Industry</small><p class="mb-1 fw-semibold">{{ company.industry || '-' }}</p></div>
            <div class="col-md-6"><small class="text-muted">Location</small><p class="mb-1 fw-semibold">{{ company.location || '-' }}</p></div>
            <div class="col-md-6"><small class="text-muted">HR Contact</small><p class="mb-1 fw-semibold">{{ company.hr_contact || '-' }}</p></div>
            <div class="col-md-6"><small class="text-muted">Website</small><p class="mb-1 fw-semibold">{{ company.website || '-' }}</p></div>
            <div class="col-12"><small class="text-muted">About</small><p class="mb-0">{{ company.description || '-' }}</p></div>
          </div>
        </div>
      </div>

      <!-- DRIVES -->
      <div v-if="activeTab==='drives'">
        <div class="d-flex justify-content-between mb-3 align-items-center">
          <h5 class="fw-bold mb-0">My Placement Drives</h5>
          <button @click="showCreateDrive=!showCreateDrive" class="btn btn-primary btn-sm">
            {{ showCreateDrive ? 'Cancel' : 'Create Drive' }}
          </button>
        </div>

        <!-- Create Drive Form -->
        <div v-if="showCreateDrive" class="card p-4 mb-4 border-primary">
          <h6 class="fw-bold mb-3 text-primary">Create New Placement Drive</h6>
          <div v-if="driveMsg" :class="['alert py-2', driveMsgOk ? 'alert-success':'alert-danger']">{{ driveMsg }}</div>
          <form @submit.prevent="createDrive">
            <div class="row g-2">
              <div class="col-md-6">
                <label class="form-label small fw-semibold">Job Title *</label>
                <input v-model="newDrive.job_title" class="form-control" placeholder="e.g. Software Engineer" required />
              </div>
              <div class="col-md-6">
                <label class="form-label small fw-semibold">Location</label>
                <input v-model="newDrive.location" class="form-control" placeholder="e.g. Bangalore" />
              </div>
              <div class="col-12">
                <label class="form-label small fw-semibold">Job Description</label>
                <textarea v-model="newDrive.job_description" class="form-control" rows="3" placeholder="Describe the role..."></textarea>
              </div>
              <div class="col-md-4">
                <label class="form-label small fw-semibold">Eligible Branches</label>
                <input v-model="newDrive.eligible_branches" class="form-control" placeholder="CSE,ECE..." />
              </div>
              <div class="col-md-4">
                <label class="form-label small fw-semibold">Minimum CGPA</label>
                <input v-model="newDrive.min_cgpa" type="number" step="0.1" min="0" max="10" class="form-control" placeholder="e.g. 7.0" />
              </div>
              <div class="col-md-4">
                <label class="form-label small fw-semibold">Eligible Year</label>
                <select v-model="newDrive.eligible_year" class="form-select">
                  <option value="">All Years</option>
                  <option v-for="y in [1,2,3,4]" :key="y" :value="y">Year {{ y }}</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label small fw-semibold">Salary</label>
                <input v-model="newDrive.salary" type="number" min="0" class="form-control" placeholder="e.g. 600000" />
              </div>
              <div class="col-md-6">
                <label class="form-label small fw-semibold">Application Deadline</label>
                <input v-model="newDrive.application_deadline" type="date" class="form-control" />
              </div>
              <div class="col-12 mt-1">
                <button type="submit" class="btn btn-primary btn-sm me-2" :disabled="driveLoading">
                  <span v-if="driveLoading" class="spinner-border spinner-border-sm me-1"></span>
                  Submit for Admin Approval
                </button>
                <button type="button" @click="showCreateDrive=false;driveMsg=''" class="btn btn-secondary btn-sm">Cancel</button>
              </div>
            </div>
          </form>
        </div>

        <!-- Drives List -->
        <div class="row g-3">
          <div class="col-md-6" v-for="d in drives" :key="d.id">
            <div class="card p-3 h-100">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <h6 class="fw-bold mb-1">{{ d.job_title }}</h6>
                  <small class="text-muted">{{ d.location || 'N/A' }}</small>
                </div>
                <span :class="driveBadge(d.status)">{{ d.status }}</span>
              </div>
              <hr class="my-2"/>
              <div class="row g-1 small">
                <div class="col-6 text-muted">Branches: <b class="text-dark">{{ d.eligible_branches || 'All' }}</b></div>
                <div class="col-6 text-muted">Min CGPA: <b class="text-dark">{{ d.min_cgpa || 'None' }}</b></div>
                <div class="col-6 text-muted">Salary: <b class="text-dark">{{ d.salary ?  +Number(d.salary).toLocaleString('en-IN') : 'N/A' }}</b></div>
                <div class="col-6 text-muted">Applicants: <b class="text-dark">{{ d.applicants }}</b></div>
                <div class="col-12 text-muted">Deadline: <b class="text-dark">{{ d.deadline ? new Date(d.deadline).toLocaleDateString('en-IN') : 'No Deadline' }}</b></div>
              </div>
              <div class="mt-2 d-flex gap-2">
                <button @click="viewApplications(d)" class="btn btn-outline-primary btn-sm flex-fill">
                  View Applicants ({{ d.applicants }})
                </button>
                <button v-if="d.status==='Approved'" @click="closeDrive(d.id)" class="btn btn-outline-secondary btn-sm">
                  Close
                </button>
              </div>
            </div>
          </div>
          <div v-if="!drives.length" class="col-12 text-center text-muted py-5">
            No drives yet. Click "Create Drive".
          </div>
        </div>
      </div>

      <!-- APPLICANTS -->
      <div v-if="activeTab==='applications'">
        <div v-if="selectedDrive">
          <div class="d-flex align-items-center mb-3 gap-2">
            <button @click="selectedDrive=null;driveApps=[]" class="btn btn-outline-secondary btn-sm">
              Back
            </button>
            <h6 class="fw-bold mb-0">Applicants: {{ selectedDrive.job_title }}</h6>
            <span class="badge bg-info text-dark">{{ driveApps.length }} total</span>
          </div>
          <div v-if="updateMsg" class="alert alert-success py-2 small">{{ updateMsg }}</div>

          <div class="row g-3">
            <div class="col-12" v-for="a in driveApps" :key="a.id">
              <div class="card p-3">
                <div class="row align-items-start g-2">

                  <!-- Student Info -->
                  <div class="col-md-4">
                    <div class="fw-bold">{{ a.student_name }}</div>
                    <small class="text-muted d-block">{{ a.email }}</small>
                    <div class="mt-1 small">
                      <span class="me-2">{{ a.branch }}</span>
                      <span class="me-2">CGPA {{ a.cgpa }}</span>
                      <span>Year {{ a.year }}</span>
                    </div>
                    <div class="mt-1 small text-muted">{{ a.skills || 'No skills listed' }}</div>
                    <!-- Resume Button -->
                    <div class="mt-2">
                      <button
                        v-if="a.resume_url"
                        @click="viewStudentResume(a)"
                        class="btn btn-outline-info btn-sm"
                      >
                        View Resume
                      </button>
                      <span v-else class="badge bg-secondary">No Resume</span>
                    </div>
                  </div>

                  <!-- Status Update -->
                  <div class="col-md-3">
                    <label class="form-label small fw-semibold mb-1">Application Status</label>
                    <select @change="updateStatus(a.id, $event.target.value, a)" class="form-select form-select-sm">
                      <option v-for="s in appStatuses" :key="s" :value="s" :selected="a.status===s">{{ s }}</option>
                    </select>
                    <div class="mt-2">
                      <span :class="appBadge(a.status)">{{ a.status }}</span>
                    </div>
                    <small class="text-muted d-block mt-1">Applied: {{ new Date(a.applied_at).toLocaleDateString('en-IN') }}</small>
                  </div>

                  <!-- Interview Date -->
                  <div class="col-md-2">
                    <label class="form-label small fw-semibold mb-1">Interview Date</label>
                    <input
                      type="date"
                      class="form-control form-control-sm"
                      :value="a.interview_date ? a.interview_date.slice(0,16) : ''"
                      @change="updateInterviewDate(a.id, $event.target.value, a)"
                    />
                    <small v-if="a.interview_date" class="text-info d-block mt-1">
                      {{ new Date(a.interview_date).toLocaleDateString('en-IN') }}
                    </small>
                  </div>

                  <!-- Feedback -->
                  <div class="col-md-3">
                    <label class="form-label small fw-semibold mb-1">Feedback to Student</label>
                    <textarea
                      class="form-control form-control-sm"
                      rows="3"
                      placeholder="Write feedback for this student..."
                      :value="a.feedback || ''"
                      @blur="updateFeedback(a.id, $event.target.value, a)"
                    ></textarea>
                    <small class="text-muted">Student will see this in their applications</small>
                  </div>

                </div>
              </div>
            </div>

            <div v-if="!driveApps.length" class="col-12 text-center text-muted py-5">
              No applicants yet
            </div>
          </div>
        </div>

        <div v-else class="text-center text-muted py-5">
          
          Go to <strong>Drives</strong> tab -> click <strong>View Applicants</strong>
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
        { key: 'drives', label: 'Drives', icon: 'bi-briefcase' },
        { key: 'applications', label: 'Applicants', icon: 'bi-people' }
      ],
      company: null,
      summaryStats: [],
      drives: [],
      driveApps: [],
      selectedDrive: null,
      showCreateDrive: false,
      newDrive: { job_title: '', job_description: '', eligible_branches: '', min_cgpa: '', eligible_year: '', salary: '', location: '', application_deadline: '' },
      driveMsg: '',
      driveMsgOk: false,
      driveLoading: false,
      updateMsg: '',
      appStatuses: ['Applied', 'Shortlisted', 'Selected', 'Rejected']
    }
  },
  async mounted() {
    await this.loadDashboard()
  },
  methods: {
    async loadDashboard() {
      try {
        const res = await api.get('/company/dashboard')
        const d = res.data
        this.company = d.company
        this.summaryStats = [
          { label: 'Total Drives', value: d.total_drives, icon: 'bi-briefcase-fill', color: '#667eea' },
          { label: 'Total Applicants', value: d.total_applicants, icon: 'bi-people-fill', color: '#28a745' },
          { label: 'Shortlisted', value: d.shortlisted, icon: 'bi-star-fill', color: '#ffc107' },
          { label: 'Selected', value: d.selected, icon: 'bi-trophy-fill', color: '#dc3545' }
        ]
      } catch (e) {
        console.error('Company dashboard error:', e)
      }
    },
    async switchTab(key) {
      this.activeTab = key
      if (key === 'drives') await this.loadDrives()
    },
    async loadDrives() {
      try {
        const res = await api.get('/company/drives')
        this.drives = res.data
      } catch (e) {
        console.error('Load drives error:', e)
      }
    },
    async createDrive() {
      this.driveLoading = true
      this.driveMsg = ''
      try {
        await api.post('/company/drives', this.newDrive)
        this.driveMsgOk = true
        this.driveMsg = 'Drive submitted for admin approval!'
        this.newDrive = { job_title: '', job_description: '', eligible_branches: '', min_cgpa: '', eligible_year: '', salary: '', location: '', application_deadline: '' }
        await this.loadDrives()
        setTimeout(() => { this.showCreateDrive = false; this.driveMsg = '' }, 2500)
      } catch (e) {
        this.driveMsgOk = false
        this.driveMsg = '' + (e.response?.data?.message || 'Failed to create drive')
      } finally {
        this.driveLoading = false
      }
    },
    async closeDrive(id) {
      if (!confirm('Close this drive? Students will no longer be able to apply.')) return
      await api.post(`/company/drives/${id}/close`)
      await this.loadDrives()
    },
    async viewApplications(drive) {
      this.selectedDrive = drive
      this.activeTab = 'applications'
      try {
        const res = await api.get(`/company/drives/${drive.id}/applications`)
        this.driveApps = res.data
      } catch (e) {
        console.error('Load applicants error:', e)
      }
    },
    async updateStatus(id, status, app) {
      try {
        await api.post(`/company/applications/${id}/update`, { status })
        app.status = status
        this.showUpdateMsg('Status updated to "' + status + '"')
      } catch (e) {
        alert('Failed to update status.')
      }
    },
    async updateInterviewDate(id, dateVal, app) {
      if (!dateVal) return
      try {
        await api.post(`/company/applications/${id}/update`, { interview_date: dateVal })
        app.interview_date = dateVal
        this.showUpdateMsg('Interview date saved!')
      } catch (e) {
        alert('Failed to save interview date.')
      }
    },
    async updateFeedback(id, feedback, app) {
      try {
        await api.post(`/company/applications/${id}/update`, { feedback })
        app.feedback = feedback
        this.showUpdateMsg('Feedback saved! Student will see this.')
      } catch (e) {
        alert('Failed to save feedback.')
      }
    },
    showUpdateMsg(msg) {
      this.updateMsg = msg
      setTimeout(() => { this.updateMsg = '' }, 3000)
    },
    async viewStudentResume(app) {
      try {
        const res = await api.get(`/company/resume/${app.student_id}`, { responseType: 'blob' })
        let type = 'application/pdf'
        if (app.resume_url.endsWith('.doc')) type = 'application/msword'
        else if (app.resume_url.endsWith('.docx')) type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        
        const url = window.URL.createObjectURL(new Blob([res.data], { type }))
        window.open(url, '_blank')
      } catch (e) {
        alert('Failed to load resume. It may have been deleted.')
      }
    },
    driveBadge(s) {
      const map = { 'Approved': 'badge bg-success', 'Pending': 'badge bg-warning text-dark', 'Closed': 'badge bg-secondary', 'Rejected': 'badge bg-danger' }
      return map[s] || 'badge bg-secondary'
    },
    appBadge(s) {
      const map = { 'Applied': 'badge bg-primary', 'Shortlisted': 'badge bg-warning text-dark', 'Selected': 'badge bg-success', 'Rejected': 'badge bg-danger' }
      return map[s] || 'badge bg-secondary'
    }
  }
}
</script>
