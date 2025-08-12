// Function to initialize the date update logic
function initializeNewsItemDateLogic() {
  // Try multiple selector strategies
  let publishDatePicker = document.querySelector(".publish-date-picker");
  let expirationDatePicker = document.querySelector(".expiration-date-picker");

  // Alternative: look for field panels with these names
  if (!publishDatePicker) {
    publishDatePicker = document.querySelector('[data-field="publish_date"]');
  }
  if (!expirationDatePicker) {
    expirationDatePicker = document.querySelector('[data-field="homepage_display_expiration_date"]');
  }

  if (!publishDatePicker || !expirationDatePicker) {
    // Try to find inputs directly by name patterns
    const publishDateInput = document.querySelector('input[name="publish_date"]');
    const expirationDateInput = document.querySelector('input[name="homepage_display_expiration_date"]');

    if (publishDateInput && expirationDateInput) {
      setupEventListeners(publishDateInput, expirationDateInput);
      return;
    }

    return;
  }

  // Find the actual input fields within the date picker containers.
  // These are single datetime text inputs, not separate date/time fields
  const publishDateInput = publishDatePicker.querySelector('input[name="publish_date"]');
  const expirationDateInput = expirationDatePicker.querySelector('input[name="homepage_display_expiration_date"]');

  if (!publishDateInput || !expirationDateInput) {
    return;
  }

  setupEventListeners(publishDateInput, expirationDateInput);
}

function setupEventListeners(publishDateInput, expirationDateInput) {
  // This function calculates and sets the expiration date.
  const updateExpirationDate = () => {
    const publishDateValue = publishDateInput.value;

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
  publishDateInput.addEventListener("change", updateExpirationDate);
  publishDateInput.addEventListener("input", updateExpirationDate);
}

// Only run on news item admin pages
function shouldInitialize() {
  return window.location.href.includes('admin/snippets/home/newsitem');
}

// The 'wagtail:load' event is the correct starting point for Wagtail admin JS.
document.addEventListener("wagtail:load", function() {
  if (shouldInitialize()) {
    initializeNewsItemDateLogic();
  }
});

// Fallback for DOMContentLoaded in case wagtail:load doesn't fire
document.addEventListener("DOMContentLoaded", function() {
  if (shouldInitialize()) {
    setTimeout(initializeNewsItemDateLogic, 1000);
  }
});
