// Pamphlet admin customization: Add "insert at position" buttons between inline entries

function initializePamphletInsertButtons() {
  // Find the inline panel for pamphlet entries
  const inlinePanel = document.querySelector('[data-inline-panel-child="entries"]');

  if (!inlinePanel) {
    return;
  }

  // Add insert buttons between entries
  addInsertButtons(inlinePanel);

  // Re-add buttons when new entries are added or the panel is sorted
  observeInlinePanelChanges(inlinePanel);
}

function addInsertButtons(inlinePanel) {
  // Find the container that holds all the inline items
  const childrenContainer = inlinePanel.querySelector('[data-inline-panel-child-container]');

  if (!childrenContainer) {
    return;
  }

  // Remove any existing insert buttons first to avoid duplicates
  childrenContainer.querySelectorAll('.pamphlet-insert-button').forEach(btn => btn.remove());

  const children = Array.from(childrenContainer.children).filter(
    child => child.hasAttribute('data-inline-panel-child')
  );

  // Add an "Add new" button at the top
  const topButton = createInsertButton('Add new pamphlet at top', 0);
  childrenContainer.insertBefore(topButton, childrenContainer.firstChild);

  // Add insert buttons between and after each entry
  children.forEach((child, index) => {
    const insertButton = createInsertButton(`Add new pamphlet here`, index + 1);

    // Insert after the current child
    if (child.nextSibling) {
      childrenContainer.insertBefore(insertButton, child.nextSibling);
    } else {
      childrenContainer.appendChild(insertButton);
    }
  });
}

function createInsertButton(text, position) {
  const button = document.createElement('div');
  button.className = 'pamphlet-insert-button';
  button.style.cssText = `
    padding: 8px;
    margin: 4px 0;
    text-align: center;
    background: #f0f0f0;
    border: 2px dashed #ccc;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 13px;
    color: #666;
  `;

  button.innerHTML = `
    <span style="display: inline-flex; align-items: center; gap: 4px;">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M8 3V13M3 8H13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
      ${text}
    </span>
  `;

  // Hover effect
  button.addEventListener('mouseenter', () => {
    button.style.background = '#e8f4f8';
    button.style.borderColor = '#007cba';
    button.style.color = '#007cba';
  });

  button.addEventListener('mouseleave', () => {
    button.style.background = '#f0f0f0';
    button.style.borderColor = '#ccc';
    button.style.color = '#666';
  });

  // Click handler
  button.addEventListener('click', () => {
    insertNewEntryAtPosition(position);
  });

  return button;
}

function insertNewEntryAtPosition(position) {
  // Find the "Add" button in the inline panel
  const addButton = document.querySelector('[data-inline-panel-child="entries"] button[type="button"]');

  if (!addButton) {
    console.error('Could not find add button for inline panel');
    return;
  }

  // Click the add button to create a new entry
  addButton.click();

  // Wait for the new entry to be added to the DOM
  setTimeout(() => {
    const inlinePanel = document.querySelector('[data-inline-panel-child="entries"]');
    const childrenContainer = inlinePanel.querySelector('[data-inline-panel-child-container]');
    const children = Array.from(childrenContainer.children).filter(
      child => child.hasAttribute('data-inline-panel-child')
    );

    // The new entry is added at the end, so move it to the desired position
    const newEntry = children[children.length - 1];

    if (position < children.length - 1) {
      // Move the new entry to the specified position
      const targetChild = children[position];
      childrenContainer.insertBefore(newEntry, targetChild);
    }

    // Update sort_order values for all entries
    updateSortOrders(childrenContainer);

    // Refresh insert buttons
    addInsertButtons(inlinePanel);

    // Scroll the new entry into view
    newEntry.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }, 100);
}

function updateSortOrders(childrenContainer) {
  const children = Array.from(childrenContainer.children).filter(
    child => child.hasAttribute('data-inline-panel-child')
  );

  children.forEach((child, index) => {
    // Find the sort_order input field
    const sortOrderInput = child.querySelector('input[name*="ORDER"]');
    if (sortOrderInput) {
      sortOrderInput.value = index;
    }
  });
}

function observeInlinePanelChanges(inlinePanel) {
  const childrenContainer = inlinePanel.querySelector('[data-inline-panel-child-container]');

  if (!childrenContainer) {
    return;
  }

  // Use MutationObserver to detect when entries are added, removed, or reordered
  const observer = new MutationObserver((mutations) => {
    let shouldRefresh = false;

    mutations.forEach((mutation) => {
      if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
        // Check if any added nodes are inline panel children
        mutation.addedNodes.forEach(node => {
          if (node.nodeType === 1 && node.hasAttribute('data-inline-panel-child')) {
            shouldRefresh = true;
          }
        });
      }
    });

    if (shouldRefresh) {
      // Debounce to avoid multiple rapid refreshes
      clearTimeout(observeInlinePanelChanges.refreshTimeout);
      observeInlinePanelChanges.refreshTimeout = setTimeout(() => {
        addInsertButtons(inlinePanel);
      }, 100);
    }
  });

  observer.observe(childrenContainer, {
    childList: true,
    subtree: false
  });
}

// Check if we're on a pamphlets page
function shouldInitialize() {
  return window.location.href.includes('admin/pages/') &&
         document.querySelector('[data-inline-panel-child="entries"]') !== null;
}

// Initialize on Wagtail admin load
document.addEventListener('wagtail:load', function() {
  if (shouldInitialize()) {
    setTimeout(initializePamphletInsertButtons, 200);
  }
});

// Fallback for DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
  if (shouldInitialize()) {
    setTimeout(initializePamphletInsertButtons, 500);
  }
});
