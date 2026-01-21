// Pamphlet admin customization: Add "insert at position" buttons between inline entries

console.log("hello from pamphlet admin");

function initializePamphletInsertButtons() {
  console.log("initializePamphletInsertButtons called");

  // Find the inline panel section - it has an ID like "panel-child-content-entries-section"
  const inlinePanel = document.querySelector('#panel-child-content-entries-section');

  if (!inlinePanel) {
    console.log("Could not find inline panel for entries");
    return;
  }

  console.log("Found inline panel:", inlinePanel);

  // Add insert buttons between entries
  addInsertButtons(inlinePanel);

  // Re-add buttons when new entries are added or the panel is sorted
  observeInlinePanelChanges(inlinePanel);
}

function addInsertButtons(inlinePanel) {
  // Find the container that holds all the inline items
  // Based on Wagtail's structure, this should be inside the panel content
  let childrenContainer = inlinePanel.querySelector('[data-inline-panel-child-container]');

  // If that doesn't exist, try finding the direct container of inline children
  if (!childrenContainer) {
    // Look for the parent of elements with IDs like "inline_child_entries-0"
    const firstChild = inlinePanel.querySelector('[id^="inline_child_entries-"]');
    if (firstChild) {
      childrenContainer = firstChild.parentElement;
      console.log("Found children container via first child:", childrenContainer);
    }
  }

  if (!childrenContainer) {
    console.log("Could not find children container");
    return;
  }

  // Remove any existing insert buttons first to avoid duplicates
  childrenContainer.querySelectorAll('.pamphlet-insert-button').forEach(btn => btn.remove());

  // Find all inline children - they have IDs like "inline_child_entries-0"
  const children = Array.from(childrenContainer.children).filter(
    child => child.id && child.id.startsWith('inline_child_entries-')
  );

  console.log("Found children:", children.length);

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
  // Find the "Add" button in the inline panel - look for button with text "Add" or similar
  const inlinePanel = document.querySelector('#panel-child-content-entries-section');

  // Try multiple selectors for the add button
  let addButton = inlinePanel.querySelector('button[data-inline-panel-add-child]');

  if (!addButton) {
    // Look for any button with "Add" text
    const buttons = Array.from(inlinePanel.querySelectorAll('button'));
    addButton = buttons.find(btn => btn.textContent.includes('Add'));
  }

  if (!addButton) {
    console.error('Could not find add button for inline panel');
    return;
  }

  console.log("Clicking add button:", addButton);

  // Store current scroll position to prevent jumping
  const scrollPosition = window.scrollY;

  // Click the add button to create a new entry
  addButton.click();

  // Wait for the new entry to be added to the DOM
  setTimeout(() => {
    // Restore scroll position immediately to prevent the jump to bottom
    window.scrollTo(0, scrollPosition);

    const firstChild = inlinePanel.querySelector('[id^="inline_child_entries-"]');
    if (!firstChild) {
      console.error("Could not find any entries after adding");
      return;
    }

    const childrenContainer = firstChild.parentElement;
    const children = Array.from(childrenContainer.children).filter(
      child => child.id && child.id.startsWith('inline_child_entries-')
    );

    console.log("Children after add:", children.length);

    // The new entry is added at the end, so move it to the desired position
    const newEntry = children[children.length - 1];

    if (position < children.length - 1) {
      // Move the new entry to the specified position
      const targetChild = children[position];
      childrenContainer.insertBefore(newEntry, targetChild);
      console.log("Moved new entry to position", position);
    }

    // Update sort_order values for all entries
    updateSortOrders(childrenContainer);

    // Update all entry labels to reflect their new positions
    updateEntryLabels(childrenContainer);

    // Refresh insert buttons
    addInsertButtons(inlinePanel);

    // Now scroll smoothly to the new entry
    setTimeout(() => {
      newEntry.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 50);
  }, 100);
}

function updateSortOrders(childrenContainer) {
  const children = Array.from(childrenContainer.children).filter(
    child => child.id && child.id.startsWith('inline_child_entries-')
  );

  children.forEach((child, index) => {
    // Find the sort_order input field - it might be named like "entries-0-sort_order" or "entries-0-ORDER"
    let sortOrderInput = child.querySelector('input[name*="sort_order"]');

    if (!sortOrderInput) {
      sortOrderInput = child.querySelector('input[name*="ORDER"]');
    }

    if (sortOrderInput) {
      sortOrderInput.value = index;
      console.log(`Set sort_order for ${child.id} to ${index}`);
    } else {
      console.warn(`Could not find sort_order input for ${child.id}`);
    }
  });
}

function updateEntryLabels(childrenContainer) {
  const children = Array.from(childrenContainer.children).filter(
    child => child.id && child.id.startsWith('inline_child_entries-')
  );

  children.forEach((child, index) => {
    // Find the label/heading that displays "Entries X"
    // It's typically in a heading or label element within the inline child
    const headingSelectors = [
      'h2',
      'h3',
      '.object-title',
      '.inline-child__header',
      '[class*="title"]',
      'summary',
      'legend'
    ];

    let heading = null;
    for (const selector of headingSelectors) {
      heading = child.querySelector(selector);
      if (heading && heading.textContent.includes('Entries')) {
        break;
      }
    }

    if (heading) {
      // Update the text to show the correct position
      // The text is usually "Entries X" where X is the old number
      const newLabel = `Entries ${index + 1}`;
      heading.textContent = heading.textContent.replace(/Entries \d+/, newLabel);
      console.log(`Updated label for ${child.id} to "${newLabel}"`);
    } else {
      console.warn(`Could not find heading for ${child.id}`);
    }
  });
}

function observeInlinePanelChanges(inlinePanel) {
  const firstChild = inlinePanel.querySelector('[id^="inline_child_entries-"]');
  if (!firstChild) {
    console.log("No children found yet for observer");
    return;
  }

  const childrenContainer = firstChild.parentElement;

  if (!childrenContainer) {
    return;
  }

  // Use MutationObserver to detect when entries are added, removed, or reordered
  const observer = new MutationObserver((mutations) => {
    let shouldRefresh = false;
    let shouldUpdateLabels = false;

    mutations.forEach((mutation) => {
      if (mutation.type === 'childList') {
        // Check if any added nodes are inline panel children
        mutation.addedNodes.forEach(node => {
          if (node.nodeType === 1 && node.id && node.id.startsWith('inline_child_entries-')) {
            shouldRefresh = true;
          }
        });

        // If nodes were moved (removed and re-added), update labels
        if (mutation.removedNodes.length > 0) {
          shouldUpdateLabels = true;
        }
      }
    });

    if (shouldRefresh) {
      // Debounce to avoid multiple rapid refreshes
      clearTimeout(observeInlinePanelChanges.refreshTimeout);
      observeInlinePanelChanges.refreshTimeout = setTimeout(() => {
        addInsertButtons(inlinePanel);
      }, 100);
    }

    if (shouldUpdateLabels) {
      // Update labels after drag-and-drop reordering
      clearTimeout(observeInlinePanelChanges.labelTimeout);
      observeInlinePanelChanges.labelTimeout = setTimeout(() => {
        updateEntryLabels(childrenContainer);
      }, 150);
    }
  });

  observer.observe(childrenContainer, {
    childList: true,
    subtree: false
  });
}

// Check if we're on a pamphlets page
function shouldInitialize() {
  const isAdminPages = window.location.href.includes('admin/pages/');
  const hasEntriesPanel = document.querySelector('#panel-child-content-entries-section') !== null;

  console.log("shouldInitialize check:", {
    url: window.location.href,
    isAdminPages,
    hasEntriesPanel
  });

  return isAdminPages && hasEntriesPanel;
}

// Initialize on Wagtail admin load
document.addEventListener('wagtail:load', function() {
  console.log("wagtail:load event fired");
  if (shouldInitialize()) {
    console.log("Initializing pamphlet insert buttons via wagtail:load");
    setTimeout(initializePamphletInsertButtons, 200);
  } else {
    console.log("shouldInitialize returned false on wagtail:load");
  }
});

// Fallback for DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
  console.log("DOMContentLoaded event fired");
  if (shouldInitialize()) {
    console.log("Initializing pamphlet insert buttons via DOMContentLoaded");
    setTimeout(initializePamphletInsertButtons, 500);
  } else {
    console.log("shouldInitialize returned false on DOMContentLoaded");
  }
});
