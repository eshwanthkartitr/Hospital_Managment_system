document.addEventListener('DOMContentLoaded', function() {
    const notificationContainer = document.getElementById('notification-container');
    const doctorId = sessionStorage.getItem('doctorId'); // Ensure this is set during login

    if (notificationContainer && doctorId) {
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
                })
                .catch(error => console.error('Error loading notifications:', error));
        }

        loadNotifications();
        setInterval(loadNotifications, 30000);
    } else {
        console.error('Notification container or Doctor ID is not set.');
    }

    const submitButton = document.querySelector('.bounce.custom-cursor');
    const cursorGif = document.querySelector('.cursor-gif');

    if (submitButton && cursorGif) {
        submitButton.addEventListener('mouseenter', function(e) {
            cursorGif.style.display = 'block';
            moveCursor(e);
            document.addEventListener('mousemove', moveCursor);
        });

        submitButton.addEventListener('mouseleave', function() {
            cursorGif.style.display = 'none';
            document.removeEventListener('mousemove', moveCursor);
        });
    }
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

function openChat(chatRoomId) {
    fetch(`/get_messages/${chatRoomId}`)
        .then(response => response.json())
        .then(data => {
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = '';
            data.messages.forEach(msg => {
                console.log("msg : ",msg);
                const messageElement = document.createElement('div');
                messageElement.textContent = msg[0];
                chatMessages.appendChild(messageElement);
            });
        });
}


document.getElementById('broadcastForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const message = document.getElementById('broadcastMessage').value;

    fetch('/broadcast_message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.status);
    })
    .catch(error => console.error('Error:', error));
});

document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.dashboard-section');

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);

            sections.forEach(section => {
                section.style.display = section.id === targetId ? 'block' : 'none';
            });
        });
    });

    // Initial load
    document.querySelector('.nav-link[href="#overview"]').click();
});

document.addEventListener('DOMContentLoaded', function() {
    // Update Profile Form Submission
    document.getElementById('updateProfileForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);

        fetch('/update_profile', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch(error => console.error('Error updating profile:', error));
    });

    // Change Password Form Submission
    document.getElementById('changePasswordForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);

        fetch('/change_password', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch(error => console.error('Error changing password:', error));
    });

    // Update Profile Picture Form Submission
    document.getElementById('updateProfilePicForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);

        fetch('/update_profile_picture', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch(error => console.error('Error updating profile picture:', error));
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const updateProfileForm = document.getElementById('updateProfileForm');
    if (updateProfileForm) {
        updateProfileForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);

            fetch('/update_profile', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
            })
            .catch(error => console.error('Error updating profile:', error));
        });
    }

    // Ensure other elements are also checked before adding event listeners
    const scheduleButton = document.getElementById('scheduleButton');
    if (scheduleButton) {
        scheduleButton.addEventListener('click', function() {
            // Your event handler code
        });
    }
});

document.getElementById('sendButton').addEventListener('click', function() {
    const message = document.getElementById('messageInput').value;
    const chatRoomId = 4; // Example chat room ID

    fetch('/send_message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_room_id: chatRoomId, message: message })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Message sent:', data);
        loadMessages(chatRoomId);
    })
    .catch(error => {
        console.error('Error sending message:', error);
    });
});

function loadMessages(chatRoomId) {
    if(chatRoomId == "Null"){
        return;
    }
    fetch(`/get_messages/${chatRoomId}`)
        .then(response => response.json())
        .then(data => {
            const messagesDiv = document.getElementById('messages');
            messagesDiv.innerHTML = '';
            console.log("data : ",data);
            data.forEach(msg => {
                const messageElement = document.createElement('div');
                console.log("msg : ",msg);
                messageElement.textContent = `${msg[0]}: ${msg[1]}`;
                messagesDiv.appendChild(messageElement);
            });
        });
}

setInterval(() => loadMessages(1), 5000); // Refresh messages every 5 seconds

function loadChatPartners() {
    fetch('/get_chat_partners')
        .then(response => response.json())
        .then(data => {
            const chatList = document.getElementById('chatList');
            chatList.innerHTML = '';

            data.forEach(partner => {
                const chatItem = document.createElement('div');
                chatItem.textContent = partner.name;
                chatItem.dataset.partnerId = partner.id;
                chatItem.classList.add('chat-item');
                chatItem.addEventListener('click', function () {
                    document.querySelectorAll('.chat-item').forEach(item => item.classList.remove('active'));
                    chatItem.classList.add('active');
                    document.getElementById('chatHeader').textContent = partner.name;

                    if (partner.chat_room_id) {
                        loadMessages(partner.chat_room_id);
                    } else {
                        createChatRoom(partner.id);
                    }
                });
                chatList.appendChild(chatItem);
            });
        })
        .catch(error => console.error('Error loading chat partners:', error));
}

function createChatRoom(partnerId) {
    fetch('/create_chat_room', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ partner_id: partnerId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.chat_room_id) {
            loadMessages(data.chat_room_id);
        } else {
            console.error('Error creating chat room');
        }
    })
    .catch(error => console.error('Error creating chat room:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    loadChatPartners();
});

document.getElementById('appointmentDate').addEventListener('change', function() {
    const date = this.value;
    const doctorId = /*    */;
    
    fetch('/get_available_slots', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ date: date, doctor_id: doctorId })
    })
    .then(response => response.json())
    .then(availableSlots => {
        const slotsContainer = document.getElementById('slotsContainer');
        slotsContainer.innerHTML = ''; // Clear previous slots

        const allSlots = Array.from({ length: 12 }, (_, i) => `${9 + i}:00`); // 9 AM to 8 PM
        allSlots.forEach(slot => {
            const slotElement = document.createElement('div');
            slotElement.textContent = slot;
            slotElement.classList.add('slot');

            if (availableSlots.includes(slot)) {
                slotElement.classList.add('available');
                slotElement.addEventListener('click', () => bookAppointment(slot, date, doctorId));
            } else {
                slotElement.classList.add('booked');
            }

            slotsContainer.appendChild(slotElement);
        });
    })
    .catch(error => console.error('Error fetching slots:', error));
});

function bookAppointment(slot, date, doctorId) {
    fetch('/book_appointment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ doctor_id: doctorId, date: date, time_slot: slot })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        // Optionally refresh the slots
    })
    .catch(error => console.error('Error booking appointment:', error));
}

let currentAppointmentId = null;
let currentAction = null;

function showModal(action, appointmentId) {
    currentAppointmentId = appointmentId;
    currentAction = action;
    const modal = document.getElementById("confirmationModal");
    const modalMessage = document.getElementById("modalMessage");
    modalMessage.textContent = `Are you sure you want to ${action} this appointment?`;
    modal.style.display = "block";
}

document.getElementById("confirmButton").addEventListener("click", function() {
    const memo = document.getElementById("memoInput").value;
    if (currentAction === "accept") {
        acceptAppointment(currentAppointmentId, memo);
    } else if (currentAction === "reject") {
        rejectAppointment(currentAppointmentId, memo);
    }
    closeModal();
});

document.getElementById("cancelButton").addEventListener("click", closeModal);
document.querySelector(".close").addEventListener("click", closeModal);

function closeModal() {
    const modal = document.getElementById("confirmationModal");
    modal.style.display = "none";
    document.getElementById("memoInput").value = "";
}

function acceptAppointment(appointmentId, memo) {
    fetch(`/appointments/accept/${appointmentId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ memo: memo })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        loadAppointments(); // Refresh the list of appointments
    })
    .catch(error => console.error('Error accepting appointment:', error));
}

function rejectAppointment(appointmentId, memo) {
    fetch(`/appointments/reject/${appointmentId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ memo: memo })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        loadAppointments(); // Refresh the list of appointments
    })
    .catch(error => console.error('Error rejecting appointment:', error));
}

function loadAppointments() {
    fetch("/get_appointments")
        .then(response => response.json())
        .then(data => {
            const appointmentsList = document.getElementById("appointmentsList");
            appointmentsList.innerHTML = ""; // Clear existing content

            data.forEach(appointment => {
                const appointmentItem = document.createElement("div");
                appointmentItem.classList.add("appointment-item");
                appointmentItem.innerHTML = `
                    <h4>Appointment with ${appointment.patient_name}</h4>
                    <p>Date: ${appointment.date} at ${appointment.time_slot}</p>
                    <button onclick="showModal('accept', ${appointment.id})" class="accept-btn">
                        <i class="fas fa-check"></i> Accept
                    </button>
                    <button onclick="showModal('reject', ${appointment.id})" class="reject-btn">
                        <i class="fas fa-times"></i> Reject
                    </button>
                `;
                appointmentsList.appendChild(appointmentItem);
            });
        })
        .catch(error => console.error("Error loading appointments:", error));
}

document.addEventListener('DOMContentLoaded', function() {
    loadAppointments();
});

document.addEventListener('DOMContentLoaded', function() {
    const scheduleButton = document.getElementById('scheduleButton');
    const scheduleModal = document.getElementById('scheduleModal');
    const closeModalButton = scheduleModal.querySelector('.close');
    const body = document.body;

    scheduleButton.addEventListener('click', function() {
        scheduleModal.style.display = 'block';
        body.classList.add('modal-open');
    });

    closeModalButton.addEventListener('click', function() {
        scheduleModal.style.display = 'none';
        body.classList.remove('modal-open');
    });

    window.addEventListener('click', function(event) {
        if (event.target === scheduleModal) {
            scheduleModal.style.display = 'none';
            body.classList.remove('modal-open');
        }
    });
});
