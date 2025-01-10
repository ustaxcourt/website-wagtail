

function refreshScrollToTopButton() {
    const button = document.getElementById('scroll-to-top');
    if (window.scrollY > 100) {
        button.classList.add('visible');
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
