document.addEventListener('DOMContentLoaded', function() {
    const notificationContainer = document.getElementById('notification-container');
    const doctorId = /* Get doctor ID from session or data attribute */;

    function loadNotifications() {
        fetch(`/get_notifications?user_id=${doctorId}&user_type=doctor`)
            .then(response => response.json())
            .then(data => {
                notificationContainer.innerHTML = '';
                data.notifications.forEach(notification => {
                    const notificationElement = document.createElement('div');
                    notificationElement.classList.add('notification');
                    notificationElement.textContent = notification.message;
                    notificationContainer.appendChild(notificationElement);
                });
            });
    }

    // Load notifications on page load
    loadNotifications();

    // Reload notifications every 30 seconds
    setInterval(loadNotifications, 30000);
});

document.addEventListener('DOMContentLoaded', function() {
    const submitButton = document.querySelector('.bounce.custom-cursor');
    const cursorGif = document.querySelector('.cursor-gif');
    const submissionEffect = document.getElementById('submissionEffect');

    // Show cursor GIF on button hover
    submitButton.addEventListener('mouseenter', function(e) {
        cursorGif.style.display = 'block';
        moveCursor(e);
        document.addEventListener('mousemove', moveCursor);
    });

    submitButton.addEventListener('mouseleave', function() {
        cursorGif.style.display = 'none';
        document.removeEventListener('mousemove', moveCursor);
    });

    function moveCursor(e) {
        cursorGif.style.left = e.clientX + 'px';
        cursorGif.style.top = e.clientY + 'px';
    }

    // Handle form submission
    document.getElementById('doctorApplicationForm').addEventListener('submit', function(e) {
        e.preventDefault();
        setTimeout(function() {
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