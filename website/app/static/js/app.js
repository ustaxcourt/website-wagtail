
/***
 * Scroll to top button handler which is used to scroll to the top of the page when the button is clicked
 */
function refreshScrollToTopButton() {
    const button = document.getElementById('scroll-to-top');
    const footer = document.getElementById('app-footer');

    const buttonRect = button.getBoundingClientRect();
    const footerRect = footer.getBoundingClientRect();

    const viewportHeight = window.innerHeight;
    const distanceFromBottom = viewportHeight - footerRect.top;


    if (window.scrollY > 100) {
        button.classList.add('visible');

        if (buttonRect.bottom > footerRect.top) {
            //console.log(footerRect.top);

            button.style.bottom = `${20 + distanceFromBottom}px`;
        } else {
            button.style.bottom = '20px';
        }
    } else {
        button.classList.remove('visible');
    }
}

window.addEventListener('scroll', () => {
    refreshScrollToTopButton();
});

document.getElementById('scroll-to-top').addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});
