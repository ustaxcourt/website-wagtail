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

// Fallback for DOMContentLoaded in case wagtail:load doesn't fire
document.addEventListener("DOMContentLoaded", function() {
  function hideAddButtonIfNeeded() {
    //TODO: Need to verify that this code works properly if multiple buttons have been added to the page
    document.querySelectorAll('[data-contentpath="url"]').forEach(function(container) {
      container.querySelectorAll('[data-streamfield-stream-container]').forEach(function(streamContainer) {
        console.log(streamContainer); //TODO: Remove before submitting pull request

        //Check for element in streamContainer with attribute = [data-streamfield-child] and style is null (or style is not "display: none;")
        const elementsWithoutStyle = Array.from(streamContainer.childNodes).filter(el => el.hasAttribute('data-streamfield-child') && (!el.hasAttribute('style') || el.style.display !== 'none'));
        console.log(elementsWithoutStyle); //TODO: Remove before submitting pull request

        const elementsNotDataStreamfieldChild = Array.from(streamContainer.childNodes).filter(el => !el.hasAttribute('data-streamfield-child'));
        //If element found, then set all divs without [data-streamfield-child] attribute in streamContainer to have style="display: none;" and aria-hidden="true"
        if (elementsWithoutStyle.length > 0)
        {
          elementsNotDataStreamfieldChild.forEach((element) => {
            element.style.display = 'none';
            element.setAttribute('aria-hidden', 'true');
          });
        }
        else //Else set last div without [data-streamfield-child] attribute to have style="" and remove aria-hidden attribute
        {
          const lastElement = elementsNotDataStreamfieldChild[elementsNotDataStreamfieldChild.length - 1];
          lastElement.style.display = '';
          lastElement.removeAttribute('aria-hidden');
        }
      })
      console.log(container); //TODO: Remove before submitting pull request
    })
  }

  // Run on load
  hideAddButtonIfNeeded();

  //TODO: Identify the correct event(s) to associate the action to hide the add buttons for URLs of button components.
  //TODO: Figure out what event is fired when the trash can icon is clicked on a URL object.
  document.body.addEventListener('click', function(e) {
    setTimeout(hideAddButtonIfNeeded, 100); // Delay to allow DOM update
  });
});
