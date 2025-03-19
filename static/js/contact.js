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
  
    // Contact Form Submission
    const contactForm = document.getElementById("contactForm")
  
    if (contactForm) {
      contactForm.addEventListener("submit", (e) => {
        e.preventDefault()
  
        // Get form data
        const name = document.getElementById("name").value
        const email = document.getElementById("email").value
        const subject = document.getElementById("subject").value
        const message = document.getElementById("message").value
  
        // Validate form data
        if (!name || !email || !subject || !message) {
          alert("Please fill in all fields")
          return
        }
  
        // Prepare data for submission
        const formData = {
          name,
          email,
          subject,
          message,
        }
  
        // Show loading state
        const submitBtn = contactForm.querySelector('button[type="submit"]')
        const originalBtnText = submitBtn.textContent
        submitBtn.disabled = true
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...'
  
        // Send data to server
        fetch("/api/contact", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
        })
          .then((response) => response.json())
          .then((data) => {
            // Reset button state
            submitBtn.disabled = false
            submitBtn.textContent = originalBtnText
  
            if (data.success) {
              // Show success message
              alert("Message sent successfully! We will get back to you soon.")
  
              // Reset form
              contactForm.reset()
            } else {
              // Show error message
              alert("Error: " + (data.error || "Failed to send message"))
            }
          })
          .catch((error) => {
            // Reset button state
            submitBtn.disabled = false
            submitBtn.textContent = originalBtnText
  
            console.error("Error sending message:", error)
            alert("Failed to send message. Please try again later.")
          })
      })
    }
  })
  
  