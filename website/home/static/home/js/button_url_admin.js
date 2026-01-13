// Override Wagtail's default error message for max_num validation on ButtonBlock URL fields
(function() {
  // Use MutationObserver to catch error messages as they're added to the DOM
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      mutation.addedNodes.forEach(function(node) {
        if (node.nodeType === Node.ELEMENT_NODE) {
          // Look for error messages within ButtonBlock URL fields
          const errorMessages = node.querySelectorAll ? node.querySelectorAll('.help-block.help-critical, .error-message') : [];
          errorMessages.forEach(function(errorEl) {
            if (errorEl.textContent.includes('The maximum number of items is 1')) {
              // Check if this error is within a ButtonBlock URL field
              const urlContainer = errorEl.closest('[data-contentpath="url"]');
              if (urlContainer) {
                errorEl.textContent = 'Please select only one URL type for this button.';
              }
            }
          });

          // Also check if the node itself is an error message
          if (node.classList && (node.classList.contains('help-block') || node.classList.contains('error-message'))) {
            if (node.textContent.includes('The maximum number of items is 1')) {
              const urlContainer = node.closest('[data-contentpath="url"]');
              if (urlContainer) {
                node.textContent = 'Please select only one URL type for this button.';
              }
            }
          }
        }
      });
    });
  });

  // Start observing once DOM is ready
  document.addEventListener('DOMContentLoaded', function() {
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  });
})();

// Toggle add button and duplicate button visibility based on whether a URL link exists
(function() {
  function updateButtonVisibility() {
    document.querySelectorAll('[data-contentpath="url"]').forEach(function(container) {
      container.querySelectorAll('[data-streamfield-stream-container]').forEach(function(streamContainer) {
        // Get all streamfield child elements (the actual link items)
        const streamfieldChildren = streamContainer.querySelectorAll('[data-streamfield-child]');

        // Check for visible streamfield children (not hidden/deleted)
        const visibleChildren = Array.from(streamfieldChildren).filter(el => el.style.display !== 'none');

        // Get the add button container(s) - elements that are NOT streamfield children
        const addButtonContainers = Array.from(streamContainer.children).filter(el =>
          el.nodeType === Node.ELEMENT_NODE && !el.hasAttribute('data-streamfield-child')
        );

        // Get duplicate buttons within the url container
        const duplicateButtons = container.querySelectorAll('[data-streamfield-action="DUPLICATE"]');

        // If there are visible children, hide add buttons and duplicate buttons
        if (visibleChildren.length > 0) {
          addButtonContainers.forEach((element) => {
            element.style.display = 'none';
            element.setAttribute('aria-hidden', 'true');
          });
          duplicateButtons.forEach((element) => {
            element.style.display = 'none';
            element.setAttribute('aria-hidden', 'true');
          });
        } else {
          // No visible children - show only the first add button, hide the rest
          addButtonContainers.forEach((element, index) => {
            if (index === 0) {
              element.style.display = '';
              element.removeAttribute('aria-hidden');
            } else {
              element.style.display = 'none';
              element.setAttribute('aria-hidden', 'true');
            }
          });
          // Show duplicate buttons
          duplicateButtons.forEach((element) => {
            element.style.display = '';
            element.removeAttribute('aria-hidden');
          });
        }
      })
    })
  }

  // Use MutationObserver to detect when streamfield children are added, removed, or hidden
  const streamfieldObserver = new MutationObserver(updateButtonVisibility);

  document.addEventListener('DOMContentLoaded', function() {
    updateButtonVisibility();

    streamfieldObserver.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['style']
    });
  });
})();
