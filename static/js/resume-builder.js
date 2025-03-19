document.addEventListener("DOMContentLoaded", () => {
    // Mobile Menu Toggle
    const hamburger = document.querySelector(".hamburger")
    const navMenu = document.querySelector(".nav-menu")
  
    if (hamburger) {
      hamburger.addEventListener("click", () => {
        navMenu.classList.toggle("active")
        hamburger.classList.toggle("active")
      })
    }
  
    // Add Experience Button
    const addExperienceBtn = document.getElementById("addExperience")
    const experienceSection = document.getElementById("experienceSection")
  
    if (addExperienceBtn && experienceSection) {
      addExperienceBtn.addEventListener("click", () => {
        const experienceItems = experienceSection.querySelectorAll(".experience-item")
        const newItem = experienceItems[0].cloneNode(true)
  
        // Clear input values
        newItem.querySelectorAll("input, textarea").forEach((input) => {
          input.value = ""
        })
  
        // Add remove button if it's not the first item
        if (experienceItems.length > 0) {
          const removeBtn = document.createElement("button")
          removeBtn.type = "button"
          removeBtn.className = "remove-btn"
          removeBtn.innerHTML = '<i class="fas fa-trash"></i>'
          removeBtn.addEventListener("click", () => {
            newItem.remove()
          })
  
          newItem.appendChild(removeBtn)
        }
  
        // Insert before the "Add Another Experience" button
        experienceSection.insertBefore(newItem, addExperienceBtn)
      })
    }
  
    // Add Education Button
    const addEducationBtn = document.getElementById("addEducation")
    const educationSection = document.getElementById("educationSection")
  
    if (addEducationBtn && educationSection) {
      addEducationBtn.addEventListener("click", () => {
        const educationItems = educationSection.querySelectorAll(".education-item")
        const newItem = educationItems[0].cloneNode(true)
  
        // Clear input values
        newItem.querySelectorAll("input, textarea").forEach((input) => {
          input.value = ""
        })
  
        // Add remove button if it's not the first item
        if (educationItems.length > 0) {
          const removeBtn = document.createElement("button")
          removeBtn.type = "button"
          removeBtn.className = "remove-btn"
          removeBtn.innerHTML = '<i class="fas fa-trash"></i>'
          removeBtn.addEventListener("click", () => {
            newItem.remove()
          })
  
          newItem.appendChild(removeBtn)
        }
  
        // Insert before the "Add Another Education" button
        educationSection.insertBefore(newItem, addEducationBtn)
      })
    }
  
    // Preview Resume Button
    const previewResumeBtn = document.getElementById("previewResume")
    const resumeForm = document.getElementById("resumeForm")
    const resumePreview = document.getElementById("resumePreview")
    const previewContent = document.getElementById("previewContent")
    const editResumeBtn = document.getElementById("editResume")
  
    if (previewResumeBtn && resumeForm && resumePreview && previewContent && editResumeBtn) {
      previewResumeBtn.addEventListener("click", () => {
        // Get form data
        const fullName = document.getElementById("fullName").value || "Your Name"
        const jobTitle = document.getElementById("jobTitle").value || "Professional Title"
        const email = document.getElementById("email").value || "email@example.com"
        const phone = document.getElementById("phone").value || "+234 123 456 7890"
        const location = document.getElementById("location").value || "Lagos, Nigeria"
        const website = document.getElementById("website").value || ""
        const summary = document.getElementById("summary").value || "Professional summary goes here..."
  
        // Get skills
        const skills = document
          .getElementById("skills")
          .value.split(",")
          .map((skill) => skill.trim())
          .filter((skill) => skill !== "")
  
        // Get experience items
        const experienceItems = Array.from(document.querySelectorAll(".experience-item")).map((item) => {
          return {
            title: item.querySelector('[name="expTitle[]"]').value || "Job Title",
            company: item.querySelector('[name="expCompany[]"]').value || "Company Name",
            startDate: formatDate(item.querySelector('[name="expStartDate[]"]').value) || "Start Date",
            endDate: item.querySelector('[name="expEndDate[]"]').value
              ? formatDate(item.querySelector('[name="expEndDate[]"]').value)
              : "Present",
            description: item.querySelector('[name="expDescription[]"]').value || "Job description...",
          }
        })
  
        // Get education items
        const educationItems = Array.from(document.querySelectorAll(".education-item")).map((item) => {
          return {
            degree: item.querySelector('[name="eduDegree[]"]').value || "Degree/Certificate",
            institution: item.querySelector('[name="eduInstitution[]"]').value || "Institution Name",
            startDate: formatDate(item.querySelector('[name="eduStartDate[]"]').value) || "Start Date",
            endDate: item.querySelector('[name="eduEndDate[]"]').value
              ? formatDate(item.querySelector('[name="eduEndDate[]"]').value)
              : "Present",
            description: item.querySelector('[name="eduDescription[]"]').value || "Education description...",
          }
        })
  
        // Generate resume HTML
        const resumeHTML = `
                  <div class="resume">
                      <div class="resume-header">
                          <h1>${fullName}</h1>
                          <p class="job-title">${jobTitle}</p>
                          <div class="contact-info">
                              <p><i class="fas fa-envelope"></i> ${email}</p>
                              <p><i class="fas fa-phone"></i> ${phone}</p>
                              <p><i class="fas fa-map-marker-alt"></i> ${location}</p>
                              ${website ? `<p><i class="fas fa-globe"></i> ${website}</p>` : ""}
                          </div>
                      </div>
                      
                      <div class="resume-section">
                          <h2>Professional Summary</h2>
                          <p>${summary}</p>
                      </div>
                      
                      <div class="resume-section">
                          <h2>Experience</h2>
                          ${experienceItems
                            .map(
                              (exp) => `
                              <div class="resume-item">
                                  <div class="resume-item-header">
                                      <h3>${exp.title}</h3>
                                      <p class="company">${exp.company}</p>
                                      <p class="date">${exp.startDate} - ${exp.endDate}</p>
                                  </div>
                                  <p>${exp.description}</p>
                              </div>
                          `,
                            )
                            .join("")}
                      </div>
                      
                      <div class="resume-section">
                          <h2>Education</h2>
                          ${educationItems
                            .map(
                              (edu) => `
                              <div class="resume-item">
                                  <div class="resume-item-header">
                                      <h3>${edu.degree}</h3>
                                      <p class="company">${edu.institution}</p>
                                      <p class="date">${edu.startDate} - ${edu.endDate}</p>
                                  </div>
                                  <p>${edu.description}</p>
                              </div>
                          `,
                            )
                            .join("")}
                      </div>
                      
                      <div class="resume-section">
                          <h2>Skills</h2>
                          <div class="skills-list">
                              ${
                                skills.length > 0
                                  ? skills.map((skill) => `<span class="skill">${skill}</span>`).join("")
                                  : "<p>No skills listed</p>"
                              }
                          </div>
                      </div>
                  </div>
              `
  
        // Display preview
        previewContent.innerHTML = resumeHTML
        resumeForm.style.display = "none"
        resumePreview.style.display = "block"
      })
  
      // Edit Resume Button
      editResumeBtn.addEventListener("click", () => {
        resumePreview.style.display = "none"
        resumeForm.style.display = "block"
      })
  
      // Download Resume Button
      const downloadResumeBtn = document.getElementById("downloadResume")
  
      if (downloadResumeBtn) {
        downloadResumeBtn.addEventListener("click", () => {
          // In a real application, you would use a library like html2pdf.js or jsPDF
          // For this demo, we'll just show an alert
          alert("In a production environment, this would download a PDF of your resume.")
  
          // Example of how you might implement this with html2pdf.js:
          // const element = document.getElementById('previewContent');
          // html2pdf().from(element).save('resume.pdf');
        })
      }
  
      // Form Submit
      resumeForm.addEventListener("submit", (e) => {
        e.preventDefault()
  
        // Collect form data
        const formData = {
          fullName: document.getElementById("fullName").value,
          jobTitle: document.getElementById("jobTitle").value,
          email: document.getElementById("email").value,
          phone: document.getElementById("phone").value,
          location: document.getElementById("location").value,
          website: document.getElementById("website").value,
          summary: document.getElementById("summary").value,
          skills: document
            .getElementById("skills")
            .value.split(",")
            .map((skill) => skill.trim()),
          experience: Array.from(document.querySelectorAll(".experience-item")).map((item) => ({
            title: item.querySelector('[name="expTitle[]"]').value,
            company: item.querySelector('[name="expCompany[]"]').value,
            startDate: item.querySelector('[name="expStartDate[]"]').value,
            endDate: item.querySelector('[name="expEndDate[]"]').value,
            description: item.querySelector('[name="expDescription[]"]').value,
          })),
          education: Array.from(document.querySelectorAll(".education-item")).map((item) => ({
            degree: item.querySelector('[name="eduDegree[]"]').value,
            institution: item.querySelector('[name="eduInstitution[]"]').value,
            startDate: item.querySelector('[name="eduStartDate[]"]').value,
            endDate: item.querySelector('[name="eduEndDate[]"]').value,
            description: item.querySelector('[name="eduDescription[]"]').value,
          })),
        }
  
        // Send data to server
        fetch("/api/resumes", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.success) {
              // Show preview
              previewResumeBtn.click()
  
              // Show success message
              alert("Resume saved successfully!")
            } else {
              alert("Error: " + data.error)
            }
          })
          .catch((error) => {
            console.error("Error saving resume:", error)
            alert("Failed to save resume. Please try again later.")
          })
      })
    }
  
    // Helper function to format date (YYYY-MM to Month Year)
    function formatDate(dateString) {
      if (!dateString) return ""
  
      const date = new Date(dateString)
      const months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
      ]
  
      return `${months[date.getMonth()]} ${date.getFullYear()}`
    }
  })
  
  