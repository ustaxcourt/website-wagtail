(function() {
    const historyEntryIdKey = "detailedTimelineEntryId";
    let printHost = null;

    function getHistoryEntryId() {
        const state = window.history.state;
        return state && typeof state === "object" ? state[historyEntryIdKey] || null : null;
    }

    function ensureHistoryEntryId() {
        let entryId = getHistoryEntryId();
        if (entryId) return entryId;

        entryId = Date.now().toString(36) + Math.random().toString(36).slice(2);
        const currentState = window.history.state;
        const state = currentState && typeof currentState === "object" ? currentState : {};
        try {
            window.history.replaceState(
                Object.assign({}, state, { [historyEntryIdKey]: entryId }),
                ""
            );
            return entryId;
        } catch (error) {
            return null;
        }
    }

    function getStorageKey(entryId, timeline) {
        return "detailed-timeline:" + entryId + ":" + timeline.id;
    }

    function setAccordionExpanded(accordion, isExpanded) {
        const content = accordion.querySelector(".detailed-timeline-accordion-content");
        const header = accordion.querySelector(".detailed-timeline-accordion-header");
        const title = accordion.querySelector(".detailed-timeline-accordion-title");
        const button = accordion.querySelector(".detailed-timeline-accordion-header-button");
        const icon = accordion.querySelector(".detailed-timeline-accordion-icon");

        if (content) content.classList.toggle("hidden", !isExpanded);
        [header, title, button, icon].forEach(function(element) {
            if (element) element.classList.toggle("active", isExpanded);
        });
        if (button) button.setAttribute("aria-expanded", isExpanded);
        if (icon) icon.classList.toggle("rotated", isExpanded);
    }

    function saveAccordionState(timeline) {
        const entryId = ensureHistoryEntryId();
        if (!entryId) return;

        const states = Array.from(
            timeline.querySelectorAll(".detailed-timeline-accordion-content")
        ).map(function(content) {
            return !content.classList.contains("hidden");
        });
        try {
            window.sessionStorage.setItem(
                getStorageKey(entryId, timeline),
                JSON.stringify(states)
            );
        } catch (error) {
            // Storage unavailable; state just will not persist.
        }
    }

    function restoreAccordionState(timeline) {
        const entryId = getHistoryEntryId();
        if (!entryId) return;

        let savedStates = null;
        try {
            const storedStates = window.sessionStorage.getItem(
                getStorageKey(entryId, timeline)
            );
            savedStates = storedStates ? JSON.parse(storedStates) : null;
        } catch (error) {
            savedStates = null;
        }

        const accordions = Array.from(
            timeline.querySelectorAll(".detailed-timeline-accordion-block")
        );
        if (!Array.isArray(savedStates) || savedStates.length !== accordions.length) return;

        accordions.forEach(function(accordion, index) {
            setAccordionExpanded(accordion, Boolean(savedStates[index]));
        });
    }

    function updateExpandButtonState(timeline, expandButton) {
        const contents = Array.from(
            timeline.querySelectorAll(".detailed-timeline-accordion-content")
        );
        const allExpanded = contents.length > 0 && contents.every(function(content) {
            return !content.classList.contains("hidden");
        });

        expandButton.setAttribute("aria-expanded", allExpanded);
        expandButton.querySelector(".detailed-timeline-expand-button-label").textContent =
            allExpanded ? "Collapse All" : "Expand All";
    }

    function setAllAccordionsExpanded(timeline, expandButton, isExpanded) {
        timeline.querySelectorAll(".detailed-timeline-accordion-block").forEach(
            function(accordion) {
                setAccordionExpanded(accordion, isExpanded);
            }
        );
        updateExpandButtonState(timeline, expandButton);
        saveAccordionState(timeline);
    }

    function createPrintClone(timeline) {
        const clone = timeline.cloneNode(true);
        const originalCheckboxes = timeline.querySelectorAll('input[type="checkbox"]');

        clone.querySelectorAll('input[type="checkbox"]').forEach(function(checkbox, index) {
            const isChecked = Boolean(originalCheckboxes[index] && originalCheckboxes[index].checked);
            checkbox.checked = isChecked;
            checkbox.toggleAttribute("checked", isChecked);
        });
        clone.querySelectorAll(".detailed-timeline-accordion-content").forEach(
            function(content) {
                content.classList.remove("hidden");
            }
        );
        clone.querySelectorAll(
            ".detailed-timeline-accordion-header, .detailed-timeline-accordion-title, .detailed-timeline-accordion-header-button"
        ).forEach(function(element) {
            element.classList.add("active");
        });
        clone.querySelectorAll(".detailed-timeline-accordion-header-button").forEach(
            function(button) {
                button.setAttribute("aria-expanded", "true");
            }
        );
        clone.querySelectorAll("[id]").forEach(function(element) {
            element.removeAttribute("id");
        });
        clone.removeAttribute("id");
        return clone;
    }

    function cleanupPrintHost() {
        document.body.classList.remove("printing-detailed-timeline");
        if (printHost) {
            printHost.remove();
            printHost = null;
        }
    }

    function initializeTimeline(timeline) {
        if (timeline.dataset.initialized === "true") return;

        const expandButton = timeline.querySelector(".detailed-timeline-expand-button");
        const printButton = timeline.querySelector(".detailed-timeline-print-button");
        if (!expandButton || !printButton) return;

        restoreAccordionState(timeline);
        updateExpandButtonState(timeline, expandButton);

        timeline.addEventListener("click", function(event) {
            const target = event.target;
            if (!(target instanceof Element)) return;

            const accordionHeader = target.closest(".detailed-timeline-accordion-header");
            if (accordionHeader && timeline.contains(accordionHeader)) {
                const accordion = accordionHeader.closest(".detailed-timeline-accordion-block");
                const accordionButton = accordion.querySelector(
                    ".detailed-timeline-accordion-header-button"
                );
                const isExpanded = accordionButton.getAttribute("aria-expanded") === "true";
                setAccordionExpanded(accordion, !isExpanded);
                updateExpandButtonState(timeline, expandButton);
                saveAccordionState(timeline);
                return;
            }

            const clickedExpandButton = target.closest(".detailed-timeline-expand-button");
            if (clickedExpandButton && timeline.contains(clickedExpandButton)) {
                setAllAccordionsExpanded(
                    timeline,
                    expandButton,
                    expandButton.getAttribute("aria-expanded") !== "true"
                );
                return;
            }

            const clickedPrintButton = target.closest(".detailed-timeline-print-button");
            if (clickedPrintButton && timeline.contains(clickedPrintButton)) {
                cleanupPrintHost();
                printHost = document.createElement("div");
                printHost.className = "detailed-timeline-print-host";
                printHost.appendChild(createPrintClone(timeline));
                document.body.appendChild(printHost);
                document.body.classList.add("printing-detailed-timeline");
                window.print();
            }
        });

        timeline.dataset.initialized = "true";
    }

    function initializeTimelines() {
        document.querySelectorAll(".detailed-timeline-rectangle").forEach(
            initializeTimeline
        );
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initializeTimelines);
    } else {
        initializeTimelines();
    }

    document.addEventListener("initAccordion", initializeTimelines);
    window.addEventListener("afterprint", cleanupPrintHost);
})();
