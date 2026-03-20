const GAP_TO_BOTTOM_FOOTER = 70;

document.getElementById('scroll-to-top').addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});


/***
 * Scroll to top button handler which is used to scroll to the top of the page when the button is clicked
 */
function refreshScrollToTopButton() {
    const button = document.getElementById('scroll-to-top');
    const footer = document.getElementById('app-footer');
    const footerRect = footer.getBoundingClientRect();

    if(window.scrollY <= 100) {
        button.classList.remove('visible');
        return;
    }
    button.classList.add('visible');

    // If the footer is taller than the viewport (tall stacked mobile layout), scootching would
    // push the button off the top of the screen — keep it fixed at the bottom instead.
    // On tablet/desktop the footer is shorter than the viewport, so scootch above its top edge.
    if(footer.offsetHeight >= window.innerHeight) {
        button.style.bottom = `${GAP_TO_BOTTOM_FOOTER}px`;
        return;
    }

    // Scootch the button above the footer when its top edge enters the viewport from the bottom.
    const scootchNeeded = footerRect.top > 0 && footerRect.top < window.innerHeight;
    if(scootchNeeded) {
        button.style.bottom = `${window.innerHeight - footerRect.top + GAP_TO_BOTTOM_FOOTER}px`;
    } else {
        button.style.bottom = `${GAP_TO_BOTTOM_FOOTER}px`;
    }
}

window.addEventListener('scroll', refreshScrollToTopButton);
