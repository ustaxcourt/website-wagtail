

window.addEventListener('scroll', () => {
    refreshScrollToTopButton();
});

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

    const img = button.querySelector('img');
    const screenWidth = window.screen.width;
    //only do this on desktop
    if(screenWidth < 1025) {
        button.style.bottom = '70px'
        return;
    }

    //when the footer top is closer to the top of the viewport than  the bottom of the viewport is to the top of the viewport, we need to scootch
    let scootchNeeded = (footerRect.top < window.innerHeight) ;
    if(scootchNeeded) {
        button.style.bottom = `${window.innerHeight - footerRect.top + 20}px`;
    } else {
        button.style.bottom = '20px'
    }
}
