(function () {
  "use strict";

  let initialized = false;

  function findSubtextWrappers(root) {
    return root.querySelectorAll(
      "[data-contentpath='subtext'], .w-field[data-contentpath='subtext']"
    );
  }

  function findSubtextInput(wrapper) {
    return wrapper.querySelector("textarea[name$='-subtext'], input[name$='-subtext']");
  }

  function deriveListTypeName(subtextName) {
    return subtextName.replace(/-items-\d+(?:-value)?-subtext$/, "-list_type");
  }

  function findListTypeSelect(subtextInput, root) {
    const expectedName = deriveListTypeName(subtextInput.name || "");

    if (expectedName) {
      const exactMatch = root.querySelector(`select[name='${expectedName}']`);
      if (exactMatch) {
        return exactMatch;
      }
    }

    const prefix = (subtextInput.name || "").split("-items-")[0];
    let current = subtextInput.parentElement;

    while (current) {
      const candidates = current.querySelectorAll("select[name$='-list_type']");
      if (candidates.length === 1) {
        return candidates[0];
      }

      const byPrefix = Array.from(candidates).find((candidate) =>
        prefix ? candidate.name.startsWith(prefix) : false
      );
      if (byPrefix) {
        return byPrefix;
      }

      current = current.parentElement;
    }

    return null;
  }

  function setVisibility(wrapper, input, visible) {
    wrapper.hidden = !visible;
    wrapper.style.display = visible ? "" : "none";
    if (input) {
      input.disabled = !visible;
      if (!visible) {
        input.value = "";
      }
    }
  }

  function updateSubtextVisibility(root) {
    const wrappers = findSubtextWrappers(root);

    wrappers.forEach((wrapper) => {
      const subtextInput = findSubtextInput(wrapper);
      if (!subtextInput || !subtextInput.name) {
        return;
      }

      const listTypeSelect = findListTypeSelect(subtextInput, root);

      if (!listTypeSelect) {
        return;
      }

      const isSubtextList = listTypeSelect.value === "checkbox_with_subtext";
      setVisibility(wrapper, subtextInput, isSubtextList);
    });
  }

  function boot() {
    if (initialized) {
      return;
    }
    initialized = true;

    const root = document;
    updateSubtextVisibility(root);

    root.addEventListener("change", (event) => {
      if (event.target && event.target.matches("select[name$='-list_type']")) {
        updateSubtextVisibility(root);
      }
    });

    const observer = new MutationObserver(() => updateSubtextVisibility(root));
    observer.observe(document.body, { childList: true, subtree: true });
  }

  document.addEventListener("wagtail:load", boot);
  document.addEventListener("DOMContentLoaded", boot);
})();
