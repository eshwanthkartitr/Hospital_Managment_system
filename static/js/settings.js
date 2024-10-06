document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('.nav-links a');
    const sections = document.querySelectorAll('.dashboard-section, .settings-section');
    const navLinksContainer = document.querySelector('.nav-links');
    
    // Create the moving background element
    const navBackground = document.createElement('div');
    navBackground.classList.add('nav-background');
    navLinksContainer.appendChild(navBackground);

    function setActiveLink(clickedLink) {
        navLinks.forEach(link => link.parentElement.classList.remove('active'));
        clickedLink.parentElement.classList.add('active');

        // Move the background to the active link
        const linkRect = clickedLink.getBoundingClientRect();
        const containerRect = navLinksContainer.getBoundingClientRect();
        const linkOffset = linkRect.top - containerRect.top;
        navBackground.style.transform = `translateY(${linkOffset}px)`;
    }

    function animateSection(section, show, index = 0) {
        section.style.display = show ? 'block' : 'none';
        section.style.opacity = show ? '0' : '1';
        section.style.transform = show ? 'translateY(20px)' : 'translateY(0)';

        if (show) {
            setTimeout(() => {
                section.style.opacity = '1';
                section.style.transform = 'translateY(0)';
                section.style.animation = `waveIn 0.5s ease-out ${index * 0.1}s`;
            }, 50);
        }
    }

    function toggleSections(showSectionId) {
        sections.forEach((section, index) => {
            const show = section.id === showSectionId || (showSectionId === 'overview' && section.id === 'appointments');
            animateSection(section, show, index);
        });
    }

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const sectionId = this.getAttribute('href').substring(1);
            setActiveLink(this);
            toggleSections(sectionId);
        });
    });

    // Set initial active link and background position
    const initialActiveLink = document.querySelector('.nav-links .active a');
    if (initialActiveLink) {
        setActiveLink(initialActiveLink);
    }

    // Rest of your code for form submissions...
});