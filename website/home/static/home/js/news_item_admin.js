// Function to initialize the date update logic
function initializeNewsItemDateLogic() {
  console.log("Initializing news item date logic...");

  // Try multiple selector strategies
  let publishDatePicker = document.querySelector(".publish-date-picker");
  let expirationDatePicker = document.querySelector(".expiration-date-picker");

  console.log("Found publishDatePicker:", publishDatePicker);
  console.log("Found expirationDatePicker:", expirationDatePicker);

  // Alternative: look for field panels with these names
  if (!publishDatePicker) {
    publishDatePicker = document.querySelector('[data-field="publish_date"]');
  }
  if (!expirationDatePicker) {
    expirationDatePicker = document.querySelector('[data-field="homepage_display_expiration_date"]');
  }

  if (!publishDatePicker || !expirationDatePicker) {
    console.log("Date picker containers not found, trying direct input search");
    // Try to find inputs directly by name patterns
    const publishDateInput = document.querySelector('input[name="publish_date"]');
    const expirationDateInput = document.querySelector('input[name="homepage_display_expiration_date"]');

    console.log("Direct publishDateInput:", publishDateInput);
    console.log("Direct expirationDateInput:", expirationDateInput);

    if (publishDateInput && expirationDateInput) {
      console.log("Found inputs directly, setting up listeners");
      setupEventListeners(publishDateInput, expirationDateInput);
      return;
    }

    console.log("No inputs found, exiting");
    return;
  }

  // Find the actual input fields within the date picker containers.
  // These are single datetime text inputs, not separate date/time fields
  const publishDateInput = publishDatePicker.querySelector('input[name="publish_date"]');
  const expirationDateInput = expirationDatePicker.querySelector('input[name="homepage_display_expiration_date"]');

  console.log("Found publishDateInput in container:", publishDateInput);
  console.log("Found expirationDateInput in container:", expirationDateInput);

  if (!publishDateInput || !expirationDateInput) {
    console.log("Inputs not found in containers, exiting");
    return;
  }

  console.log("Setting up event listeners");
  setupEventListeners(publishDateInput, expirationDateInput);
}

function setupEventListeners(publishDateInput, expirationDateInput) {
  console.log("setupEventListeners called with:", publishDateInput, expirationDateInput);

  // This function calculates and sets the expiration date.
  const updateExpirationDate = () => {
    console.log("updateExpirationDate triggered");
    const publishDateValue = publishDateInput.value;
    console.log("Current publish date value:", publishDateValue);

    if (publishDateValue) {
      // Try to parse the date value - it might be in various formats
      let publishDate;

      // Try parsing as ISO datetime first
      publishDate = new Date(publishDateValue);

      // If that fails, try other common formats
      if (isNaN(publishDate.getTime())) {
        // Try parsing as "YYYY-MM-DD HH:MM:SS" format
        publishDate = new Date(publishDateValue.replace(' ', 'T'));
      }

      // If still fails, try parsing as just date and add default time
      if (isNaN(publishDate.getTime())) {
        publishDate = new Date(publishDateValue + 'T00:00:00');
      }

      if (!isNaN(publishDate.getTime())) {
        // Add 7 days
        publishDate.setDate(publishDate.getDate() + 7);

        // Format the expiration date to match the input format
        let formattedExpirationDate;

        if (publishDateValue.includes('T')) {
          // ISO format: 2023-12-01T10:30:00
          formattedExpirationDate = publishDate.toISOString().slice(0, 19);
        } else if (publishDateValue.includes(' ')) {
          // Space-separated format: 2023-12-01 10:30:00
          const year = publishDate.getFullYear();
          const month = String(publishDate.getMonth() + 1).padStart(2, "0");
          const day = String(publishDate.getDate()).padStart(2, "0");
          const hours = String(publishDate.getHours()).padStart(2, "0");
          const minutes = String(publishDate.getMinutes()).padStart(2, "0");
          const seconds = String(publishDate.getSeconds()).padStart(2, "0");
          formattedExpirationDate = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
        } else {
          // Date only format: 2023-12-01
          const year = publishDate.getFullYear();
          const month = String(publishDate.getMonth() + 1).padStart(2, "0");
          const day = String(publishDate.getDate()).padStart(2, "0");
          formattedExpirationDate = `${year}-${month}-${day}`;
        }

        // Set the value and dispatch event to notify Wagtail of the change
        expirationDateInput.value = formattedExpirationDate;
        expirationDateInput.dispatchEvent(new Event("change", { bubbles: true }));
        expirationDateInput.dispatchEvent(new Event("input", { bubbles: true }));
      }
    }
  };

  // Attach event listeners to the date input
  console.log("Adding event listeners to:", publishDateInput);
  publishDateInput.addEventListener("change", updateExpirationDate);
  publishDateInput.addEventListener("input", updateExpirationDate);
  console.log("Event listeners added successfully");
}

// Simple script load indicator
console.log("News item admin script loaded!");
console.log("Current URL:", window.location.href);
console.log("Page title:", document.title);

// The 'wagtail:load' event is the correct starting point for Wagtail admin JS.
document.addEventListener("wagtail:load", function() {
  console.log("wagtail:load event fired!");
  initializeNewsItemDateLogic();
});

// Fallback for DOMContentLoaded
document.addEventListener("DOMContentLoaded", function() {
  console.log("DOMContentLoaded event fired!");
  setTimeout(function() {
    console.log("DOMContentLoaded timeout - trying initialization");
    initializeNewsItemDateLogic();
  }, 1000);
});

// Immediate fallback
setTimeout(function() {
  console.log("Immediate timeout - trying initialization");
  initializeNewsItemDateLogic();
}, 2000);
