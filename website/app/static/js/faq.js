/***
 * FAQ filter + accordion behavior for questionanswers blocks rendered by
 * includes/faq_accordion.html. Each [data-faq] container is independent.
 *
 * - FilterTag toggle buttons show only the questions with the selected tag ("All" = value "").
 * - Clicking a question's link toggles it. The link's click area covers the whole
 *   header (faq.css), so the handler stays on the link and the tag isn't announced
 *   as "clickable". Modified clicks (Cmd/Ctrl/Shift/Alt) are left to the browser.
 * - Visiting with a #anchortag that matches a question expands it and scrolls to it.
 */
(function () {
    // The template includes this script once per FAQ block; only wire up once.
    if (window.ustcFaqInitialized) return;
    window.ustcFaqInitialized = true;

    function setExpanded(item, expanded) {
        item.querySelector('[data-faq-answer]').hidden = !expanded;
        item.querySelector('[data-faq-link]').setAttribute('aria-expanded', String(expanded));
        item.classList.toggle('faq__item--expanded', expanded);
    }

    function isExpanded(item) {
        return item.querySelector('[data-faq-link]').getAttribute('aria-expanded') === 'true';
    }

    function applyFilter(faq, slug) {
        const items = faq.querySelectorAll('[data-faq-item]');
        let shown = 0;
        items.forEach(function (item) {
            item.hidden = Boolean(slug) && item.dataset.filtertag !== slug;
            if (!item.hidden) shown += 1;
        });
        const status = faq.querySelector('[data-faq-status]');
        if (status) {
            status.textContent = 'Showing ' + shown + ' of ' + items.length + ' questions';
        }
    }

    function selectFilter(faq, button) {
        faq.querySelectorAll('[data-faq-filter]').forEach(function (other) {
            other.setAttribute('aria-pressed', String(other === button));
        });
        applyFilter(faq, button.value);
    }

    function selectAll(faq) {
        const all = faq.querySelector('[data-faq-filter][value=""]');
        if (all && all.getAttribute('aria-pressed') !== 'true') selectFilter(faq, all);
    }

    function initFaq(faq) {
        faq.querySelectorAll('[data-faq-filter]').forEach(function (button) {
            button.addEventListener('click', function () {
                selectFilter(faq, button);
            });
        });

        faq.querySelectorAll('[data-faq-link]').forEach(function (link) {
            link.addEventListener('click', function (event) {
                // Let the browser open the permalink in a new tab/window as usual.
                if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
                // Handle the link ourselves so an expanded question can collapse;
                // a real navigation to the same hash wouldn't fire hashchange.
                event.preventDefault();
                const item = link.closest('[data-faq-item]');
                const expanding = !isExpanded(item);
                if (expanding) history.replaceState(null, '', '#' + item.id);
                setExpanded(item, expanding);
            });
        });
    }

    function openFromHash() {
        let id;
        try {
            id = decodeURIComponent(window.location.hash.slice(1));
        } catch (e) {
            return; // Malformed hash; open the page as if there were none.
        }
        const item = id && document.getElementById(id);
        if (!item || !item.matches('[data-faq-item]')) return;
        if (item.hidden) selectAll(item.closest('[data-faq]'));
        setExpanded(item, true);
        item.scrollIntoView();
    }

    function init() {
        document.querySelectorAll('[data-faq]').forEach(initFaq);
        openFromHash();
        window.addEventListener('hashchange', openFromHash);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
