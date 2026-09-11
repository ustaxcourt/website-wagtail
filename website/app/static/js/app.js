const GAP_TO_BOTTOM_FOOTER = 70; //Needs to be updated based on size of bottom nav bar if displayed on page

document.getElementById('scroll-to-top').addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});


/***
 * Scroll to top button handler which is used to scroll to the top of the page when the button is clicked
 */
function refreshScrollToTopButton() {
    const button = document.getElementById('scroll-to-top');
    const mobileNavMenu = document.getElementById('mobile-nav-menu');
    const mobileNavMenuRect = mobileNavMenu.getBoundingClientRect();
    const mobileNavMenuStyle = window.getComputedStyle(mobileNavMenu);
    const footer = document.getElementById('app-footer');
    const footerRect = footer.getBoundingClientRect();

    if(window.scrollY <= 100) {
        button.classList.remove('visible');
        return;
    }
    button.classList.add('visible');

    const img = button.querySelector('img');
    const browserWidth = window.innerWidth;

    //only do this on desktop
    if(browserWidth < 1025) {
        if (mobileNavMenuStyle.display != 'none') {
            button.style.bottom = `${window.innerHeight - mobileNavMenuRect.top + GAP_TO_BOTTOM_FOOTER}px`;
            return;
        }
        button.style.bottom = `${GAP_TO_BOTTOM_FOOTER}px`;
        return;
    }

    //when the footer top is closer to the top of the viewport than  the bottom of the viewport is to the top of the viewport, we need to scootch
    let scootchNeeded = (footerRect.top < window.innerHeight) ;
    if(scootchNeeded) {
        button.style.bottom = `${window.innerHeight - footerRect.top + GAP_TO_BOTTOM_FOOTER}px`;
    } else {
        button.style.bottom = `${GAP_TO_BOTTOM_FOOTER}px`;
    }
}

window.addEventListener('scroll', refreshScrollToTopButton);
