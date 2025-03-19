document.addEventListener("DOMContentLoaded", () => {
  // Mobile navigation toggle
  const burger = document.querySelector(".burger")
  const nav = document.querySelector(".nav-links")

  if (burger) {
    burger.addEventListener("click", () => {
      nav.classList.toggle("nav-active")
      burger.classList.toggle("toggle")
    })
  }

  // Job board functionality
  const jobListings = document.getElementById("jobs-container") || document.querySelector(".jobs-container")
  const pagination = document.getElementById("pagination")
  const jobSearch = document.getElementById("job-search")
  const locationSearch = document.getElementById("location-search")
  const searchForm = document.getElementById("search-form")
  const searchBtn = document.getElementById("search-btn")
  const categoryTags = document.querySelectorAll(".category-tag")
  const jobModal = document.getElementById("job-modal")
  const jobDetails = document.getElementById("job-details")
  const closeModal = document.querySelector(".close")

  // Job data and pagination variables
  let allJobs = []
  let currentJobs = []
  let currentPage = 1
  const jobsPerPage = 6

  // Fetch jobs from API
  function fetchJobs() {
    console.log("Fetching jobs...")

    // Check if job listings container exists
    if (!jobListings) {
      console.error("Job listings container not found!")
      return
    }

    // Show loading spinner
    jobListings.innerHTML = `
      <div class="loading-spinner">
        <i class="fas fa-spinner fa-spin"></i>
        <p>Loading jobs...</p>
      </div>
    `

    fetch("/api/jobs")
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        return response.json()
      })
      .then((data) => {
        console.log("Jobs data received:", data.length, "jobs")

        if (!Array.isArray(data) || data.length === 0) {
          jobListings.innerHTML = `
            <div class="no-jobs">
              <i class="fas fa-exclamation-circle"></i>
              <p>No jobs found. Please try again later.</p>
            </div>
          `
          return
        }

        allJobs = data
        // Sort jobs by posted date (newest first)
        allJobs.sort((a, b) => new Date(b.posted_at) - new Date(a, b))
        currentJobs = [...allJobs] // Make a copy

        console.log("Rendering", currentJobs.length, "jobs")
        renderJobs()
        renderPagination()
      })
      .catch((error) => {
        console.error("Error fetching jobs:", error)
        jobListings.innerHTML = `
          <div class="error-message">
            <p>Failed to load jobs. Please try again later.</p>
            <button id="retry-btn" class="btn primary">Retry</button>
          </div>
        `
        const retryBtn = document.getElementById("retry-btn")
        if (retryBtn) {
          retryBtn.addEventListener("click", fetchJobs)
        }
      })
  }

  // Search functionality
  if (searchForm) {
    console.log("Search form found:", searchForm)

    searchForm.addEventListener("submit", (e) => {
      e.preventDefault()
      console.log("Search form submitted")

      const keyword = jobSearch ? jobSearch.value.trim().toLowerCase() : ""
      const location = locationSearch ? locationSearch.value.trim().toLowerCase() : ""

      console.log("Searching for keyword:", keyword, "location:", location)

      // Filter jobs based on search criteria
      searchJobs(keyword, location)
    })
  }

  function searchJobs(keyword, location) {
    console.log("Filtering jobs with keyword:", keyword, "and location:", location)

    if (!allJobs || allJobs.length === 0) {
      console.error("No jobs data available for filtering")
      return
    }

    // Reset current jobs to all jobs first
    currentJobs = [...allJobs]

    // Filter by keyword if provided
    if (keyword) {
      currentJobs = currentJobs.filter((job) => {
        return (
          job.title.toLowerCase().includes(keyword) ||
          job.company.toLowerCase().includes(keyword) ||
          (job.description && job.description.toLowerCase().includes(keyword)) ||
          (job.tags && job.tags.some((tag) => tag.toLowerCase().includes(keyword)))
        )
      })
    }

    // Filter by location if provided
    if (location) {
      currentJobs = currentJobs.filter((job) => {
        return job.location.toLowerCase().includes(location)
      })
    }

    console.log("Found", currentJobs.length, "matching jobs")

    // Reset to first page
    currentPage = 1

    // Render filtered jobs
    renderJobs()
    renderPagination()
  }

  // Category tag filtering
  if (categoryTags) {
    categoryTags.forEach((tag) => {
      tag.addEventListener("click", function () {
        // Update active class
        categoryTags.forEach((t) => t.classList.remove("active"))
        this.classList.add("active")

        const category = this.textContent.trim().toLowerCase()
        console.log("Category selected:", category)

        // Filter by category
        filterByCategory(category)
      })
    })
  }

  function filterByCategory(category) {
    if (!allJobs || allJobs.length === 0) {
      console.error("No jobs data available for filtering")
      return
    }

    // If "all" is selected, show all jobs
    if (category === "all") {
      currentJobs = [...allJobs]
    } else {
      // Filter jobs by the selected category
      currentJobs = allJobs.filter((job) => {
        return (
          (job.tags && job.tags.some((tag) => tag.toLowerCase().includes(category))) ||
          job.type.toLowerCase().includes(category) ||
          job.title.toLowerCase().includes(category) ||
          (job.level && job.level.toLowerCase().includes(category)) ||
          (job.remote && category === "remote")
        )
      })
    }

    console.log("Found", currentJobs.length, "jobs in category:", category)

    // Reset to first page
    currentPage = 1

    // Render filtered jobs
    renderJobs()
    renderPagination()
  }

  // Render jobs for current page
  function renderJobs() {
    if (!jobListings) {
      console.error("Job listings container not found when rendering!")
      return
    }

    console.log("Rendering jobs, container found:", jobListings)

    // Calculate pagination
    const startIndex = (currentPage - 1) * jobsPerPage
    const endIndex = startIndex + jobsPerPage
    const paginatedJobs = currentJobs.slice(startIndex, endIndex)

    console.log("Paginated jobs:", paginatedJobs.length)

    if (currentJobs.length === 0) {
      jobListings.innerHTML = `
        <div class="no-jobs">
          <i class="fas fa-exclamation-circle"></i>
          <p>No jobs found matching your criteria.</p>
          <button id="clear-filters-btn" class="btn secondary">Clear Filters</button>
        </div>
      `
      const clearFiltersBtn = document.getElementById("clear-filters-btn")
      if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener("click", clearFilters)
      }
      return
    }

    // Clear previous job listings
    jobListings.innerHTML = ""

    // Create job cards
    paginatedJobs.forEach((job) => {
      const jobCard = createJobCard(job)
      jobListings.appendChild(jobCard)
    })
  }

  // Create a job card element
  function createJobCard(job) {
    const jobCard = document.createElement("div")
    jobCard.className = "job-card"
    jobCard.setAttribute("data-id", job.id)

    // Format posted date
    const postedDate = new Date(job.posted_at)
    const timeAgo = getTimeAgo(postedDate)

    // Get company logo background color based on company name
    const colors = ["#4040ff", "#ff4040", "#40ff40", "#ff40ff", "#40ffff", "#ffff40"]
    const colorIndex = job.company.charCodeAt(0) % colors.length
    const logoColor = colors[colorIndex]

    // Determine the application URL - use source_url or apply_url if available
    const applyUrl = job.apply_url || job.source_url || "#"
    const hasApplyUrl = applyUrl !== "#"

    jobCard.innerHTML = `
    <div class="company-logo" style="background-color: ${logoColor}">
      ${job.company_logo || job.company.charAt(0)}
    </div>
    <div class="job-info">
      <h3>${job.title}</h3>
      <p class="company-name">${job.company}</p>
      <div class="job-meta">
        <span><i class="fas fa-map-marker-alt"></i> ${job.location}</span>
        <span><i class="fas fa-money-bill-wave"></i> ${job.salary}</span>
      </div>
      <div class="job-badges">
        <span class="job-badge badge-fulltime">${job.type}</span>
        ${job.remote ? '<span class="job-badge badge-remote">Remote</span>' : ""}
        <span class="job-badge badge-senior">${job.level || "Entry level"}</span>
      </div>
      <div class="job-tags">
        ${job.tags ? job.tags.map((tag) => `<span class="job-tag">${tag}</span>`).join("") : ""}
      </div>
    </div>
    <div class="job-actions">
      <button class="save-job"><i class="far fa-bookmark"></i></button>
      <div class="time-ago">${timeAgo}</div>
      <a href="${applyUrl}" class="apply-btn ${!hasApplyUrl ? "disabled" : ""}" ${hasApplyUrl ? 'target="_blank"' : ""}>Apply Now</a>
    </div>
  `

    // Add event listener to save job button
    const saveBtn = jobCard.querySelector(".save-job")
    if (saveBtn) {
      saveBtn.addEventListener("click", function () {
        this.innerHTML = this.innerHTML.includes("far")
          ? '<i class="fas fa-bookmark"></i>'
          : '<i class="far fa-bookmark"></i>'
        this.classList.toggle("saved")
      })
    }

    // If no apply URL is available, disable the button
    if (!hasApplyUrl) {
      const applyBtn = jobCard.querySelector(".apply-btn")
      if (applyBtn) {
        applyBtn.addEventListener("click", (e) => {
          e.preventDefault()
          alert("Application link not available for this job.")
        })
      }
    }

    return jobCard
  }

  // Format posted date to relative time (e.g., "2 days ago")
  function formatPostedDate(dateString) {
    const postedDate = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now - postedDate)
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
    const diffHours = Math.floor(diffTime / (1000 * 60 * 60))
    const diffMinutes = Math.floor(diffTime / (1000 * 60))

    if (diffDays > 30) {
      const diffMonths = Math.floor(diffDays / 30)
      return `${diffMonths} month${diffMonths > 1 ? "s" : ""} ago`
    } else if (diffDays > 0) {
      return `${diffDays} day${diffDays > 1 ? "s" : ""} ago`
    } else if (diffHours > 0) {
      return `${diffHours} hour${diffHours > 1 ? "s" : ""} ago`
    } else if (diffMinutes > 0) {
      return `${diffMinutes} minute${diffMinutes > 1 ? "s" : ""} ago`
    } else {
      return "Just now"
    }
  }

  // Render pagination controls
  function renderPagination() {
    if (!pagination) return

    const totalPages = Math.ceil(currentJobs.length / jobsPerPage)

    if (totalPages <= 1) {
      pagination.innerHTML = ""
      return
    }

    let paginationHTML = ""

    // Previous button
    paginationHTML += `
    <button class="pagination-btn prev ${currentPage === 1 ? "disabled" : ""}" 
      ${currentPage === 1 ? "disabled" : ""}>
      <i class="fas fa-chevron-left"></i>
    </button>
  `

    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
      if (i === 1 || i === totalPages || (i >= currentPage - 1 && i <= currentPage + 1)) {
        paginationHTML += `
        <button class="pagination-btn ${i === currentPage ? "active" : ""}" data-page="${i}">
          ${i}
        </button>
      `
      } else if (i === currentPage - 2 || i === currentPage + 2) {
        paginationHTML += `<span class="pagination-ellipsis">...</span>`
      }
    }

    // Next button
    paginationHTML += `
    <button class="pagination-btn next ${currentPage === totalPages ? "disabled" : ""}" 
      ${currentPage === totalPages ? "disabled" : ""}>
      <i class="fas fa-chevron-right"></i>
    </button>
  `

    pagination.innerHTML = paginationHTML

    // Add event listeners to pagination buttons
    const prevBtn = pagination.querySelector(".prev")
    const nextBtn = pagination.querySelector(".next")
    const pageButtons = pagination.querySelectorAll(".pagination-btn:not(.prev):not(.next)")

    if (prevBtn) {
      prevBtn.addEventListener("click", () => {
        if (currentPage > 1) {
          currentPage--
          renderJobs()
          renderPagination()
          scrollToTop()
        }
      })
    }

    if (nextBtn) {
      nextBtn.addEventListener("click", () => {
        if (currentPage < totalPages) {
          currentPage++
          renderJobs()
          renderPagination()
          scrollToTop()
        }
      })
    }

    pageButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const page = Number.parseInt(button.getAttribute("data-page"))
        if (page !== currentPage) {
          currentPage = page
          renderJobs()
          renderPagination()
          scrollToTop()
        }
      })
    })
  }

  // Scroll to top of job listings
  function scrollToTop() {
    const jobBoardSection = document.getElementById("job-board")
    if (jobBoardSection) {
      jobBoardSection.scrollIntoView({ behavior: "smooth" })
    }
  }

  // Show job details in modal
  function showJobDetails(job) {
    if (!jobModal || !jobDetails) return

    // Format posted date
    const postedDate = formatPostedDate(job.posted_at)

    // Create company logo or initial
    const companyLogo = job.company_logo || job.company.charAt(0)

    // Determine the application URL
    const applyUrl = job.apply_url || job.source_url || "#"
    const hasApplyUrl = applyUrl !== "#"

    jobDetails.innerHTML = `
    <div class="job-details-header">
      <div class="company-logo large">${companyLogo}</div>
      <div class="job-info">
        <h2 class="job-title">${job.title}</h2>
        <p class="company-name">${job.company}</p>
        <p class="posted-date">Posted ${postedDate}</p>
      </div>
    </div>
    <div class="job-details-body">
      <div class="job-meta">
        <div class="meta-item">
          <i class="fas fa-map-marker-alt"></i>
          <span>${job.location}</span>
        </div>
        <div class="meta-item">
          <i class="fas fa-money-bill-wave"></i>
          <span>${job.salary}</span>
        </div>
        <div class="meta-item">
          <i class="fas fa-briefcase"></i>
          <span>${job.type}</span>
        </div>
        <div class="meta-item">
          <i class="fas fa-user-tie"></i>
          <span>${job.level || "Not specified"}</span>
        </div>
      </div>
      <div class="job-tags">
        ${job.tags ? job.tags.map((tag) => `<span class="tag">${tag}</span>`).join("") : ""}
        ${job.remote ? '<span class="tag remote">Remote</span>' : ""}
      </div>
      <div class="job-description">
        <h3>Job Description</h3>
        <p>${job.description}</p>
      </div>
      ${
        job.requirements
          ? `
      <div class="job-requirements">
        <h3>Requirements</h3>
        <p>${job.requirements}</p>
      </div>
      `
          : ""
      }
      <div class="job-source">
        <p>Source: ${job.source || "NaijaFreelance"}</p>
      </div>
    </div>
    <div class="job-details-footer">
      <a href="${applyUrl}" class="btn primary apply-btn-large ${!hasApplyUrl ? "disabled" : ""}" ${hasApplyUrl ? 'target="_blank"' : ""}>
        Apply for this Job
      </a>
    </div>
  `

    // If no apply URL is available, disable the button
    if (!hasApplyUrl) {
      const applyBtn = jobDetails.querySelector(".apply-btn-large")
      if (applyBtn) {
        applyBtn.addEventListener("click", (e) => {
          e.preventDefault()
          alert("Application link not available for this job.")
        })
      }
    }

    // Show modal
    jobModal.style.display = "block"

    // Prevent body scrolling when modal is open
    document.body.style.overflow = "hidden"
  }

  // Close modal
  if (closeModal) {
    closeModal.addEventListener("click", closeJobModal)
  }

  // Close modal when clicking outside
  if (jobModal) {
    window.addEventListener("click", (e) => {
      if (e.target === jobModal) {
        closeJobModal()
      }
    })
  }

  function closeJobModal() {
    if (jobModal) {
      jobModal.style.display = "none"
      document.body.style.overflow = "auto"
    }
  }

  // Clear all filters
  function clearFilters() {
    if (jobSearch) jobSearch.value = ""
    if (locationSearch) locationSearch.value = ""

    // Reset to all jobs
    currentJobs = [...allJobs]
    currentPage = 1

    // Reset category tags
    if (categoryTags) {
      categoryTags.forEach((tag) => {
        tag.classList.remove("active")
        if (tag.textContent.trim().toLowerCase() === "all") {
          tag.classList.add("active")
        }
      })
    }

    renderJobs()
    renderPagination()
  }

  // Add event listeners for search input fields
  if (jobSearch) {
    jobSearch.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        e.preventDefault()
        searchForm.dispatchEvent(new Event("submit"))
      }
    })
  }

  if (locationSearch) {
    locationSearch.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        e.preventDefault()
        searchForm.dispatchEvent(new Event("submit"))
      }
    })
  }

  // Initialize job board
  console.log("Checking for job board...")
  // Try to find the job listings container in different ways
  const possibleContainers = [document.getElementById("jobs-container"), document.querySelector(".jobs-container")]

  for (const container of possibleContainers) {
    if (container) {
      console.log("Found job container:", container)
      fetchJobs()
      break
    }
  }

  // Update the mobile menu functionality
  const hamburger = document.querySelector(".hamburger")
  const navMenu = document.querySelector(".nav-menu")

  if (hamburger) {
    hamburger.addEventListener("click", () => {
      hamburger.classList.toggle("active")
      navMenu.classList.toggle("active")
    })
  }

  // Close menu when clicking a nav link
  document.querySelectorAll(".nav-link").forEach((link) => {
    link.addEventListener("click", () => {
      hamburger.classList.remove("active")
      navMenu.classList.remove("active")
    })
  })

  function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000)

    let interval = seconds / 31536000

    if (interval > 1) {
      return Math.floor(interval) + " years ago"
    }
    interval = seconds / 2592000
    if (interval > 1) {
      return Math.floor(interval) + " months ago"
    }
    interval = seconds / 86400
    if (interval > 1) {
      return Math.floor(interval) + " days ago"
    }
    interval = seconds / 3600
    if (interval > 1) {
      return Math.floor(interval) + " hours ago"
    }
    interval = seconds / 60
    if (interval > 1) {
      return Math.floor(interval) + " minutes ago"
    }
    return Math.floor(seconds) + " seconds ago"
  }
})

