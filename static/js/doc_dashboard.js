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