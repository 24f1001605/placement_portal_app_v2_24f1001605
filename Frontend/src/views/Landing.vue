<template>
  <div class="landing-page d-flex flex-column min-vh-100 bg-light">
    <!-- Main Header / Hero Section -->
    <div class="text-white text-center py-5 shadow flex-grow-1 d-flex align-items-center" style="background:#2c3e50">
      <div class="container py-4">
        <h1 class="display-4 fw-bold mb-3"> Campus Placement Portal </h1>
        <p class="lead mb-4">The simplest way to kickstart your professional journey</p>
        <div class="d-flex justify-content-center gap-3">
          <router-link to="/register" class="btn btn-warning btn-lg fw-bold px-4">Register Now</router-link>
          <router-link to="/login" class="btn btn-outline-light btn-lg fw-bold px-4">Student/Company Login</router-link>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <footer class="bg-dark text-white-50 py-3 text-center">
      <div class="container">
        <small>&copy; 2026 Campus Placement Portal Application - MAD II Project</small>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.landing-page {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
</style>
