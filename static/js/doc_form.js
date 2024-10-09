document.addEventListener('DOMContentLoaded', function() {
    const submitButton = document.querySelector('.bounce.custom-cursor');
    const cursorGif = document.querySelector('.cursor-gif');

    // Show cursor GIF on button hover
    submitButton.addEventListener('mouseenter', function(e) {
        cursorGif.style.display = 'block';
        moveCursor(e); // Ensure initial position is set
        document.addEventListener('mousemove', moveCursor);
    });

    submitButton.addEventListener('mouseleave', function() {
        cursorGif.style.display = 'none';
        document.removeEventListener('mousemove', moveCursor);
    });

    function moveCursor(e) {
        cursorGif.style.left = 1000*e.clientX + 'px';
        cursorGif.style.top = 1000*e.clientY + 'px';
    }

    // Handle form submission
    document.getElementById('doctorApplicationForm').addEventListener('submit', function(e) {
        e.preventDefault();
        setTimeout(function() {
            const submissionEffect = document.getElementById('submissionEffect');
            submissionEffect.style.display = 'flex';
            setTimeout(function() {
                submissionEffect.style.opacity = '1';
            }, 50);

            // Simulate actual form submission
            setTimeout(function() {
                alert('Application submitted successfully!');
                e.target.submit();
            }, 2000);
        }, 1000);
    });
});