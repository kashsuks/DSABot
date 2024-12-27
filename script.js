const body = document.body;

// Active section highlighting
const sections = document.querySelectorAll('section');
const navLinks = document.querySelectorAll('.nav-link');

const isInViewport = (element) => {
    const rect = element.getBoundingClientRect();
    return (
        rect.top <= 150 &&
        rect.bottom >= 150
    );
}

window.addEventListener('scroll', () => {
    sections.forEach(section => {
        if (isInViewport(section)) {
            const id = section.getAttribute('id');
            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${id}`) {
                    link.classList.add('active');
                }
            });
        }
    });
});