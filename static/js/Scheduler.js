// Appointments handling
const appointmentModal = document.getElementById('appointmentModal');
const scheduleButton = document.getElementById('scheduleButton');
const specializationSelect = document.getElementById('specialization');
const doctorSelect = document.getElementById('doctor');
const dateInput = document.getElementById('appointmentDate');
const timeSlotSelect = document.getElementById('timeSlot');

// Load appointments
function loadAppointments(tab = 'upcoming') {
    fetch(`/api/appointments/${tab}`)
        .then(response => response.json())
        .then(appointments => {
            const appointmentsList = document.getElementById('appointmentsList');
            appointmentsList.innerHTML = appointments.map(appointment => `
                <div class="appointment-card">
                    <div class="appointment-info">
                        <h3>Dr. ${appointment.doctor_name}</h3>
                        <div class="appointment-details">
                            <span><i class="fas fa-user-md"></i> ${appointment.specialization}</span>
                            <span><i class="fas fa-calendar"></i> ${appointment.date}</span>
                            <span><i class="fas fa-clock"></i> ${appointment.time_slot}</span>
                        </div>
                    </div>
                    <div class="appointment-actions">
                        ${appointment.status === 'accepted' ? `
                            <button onclick="openChat(${appointment.doctor_id})" class="btn-chat">
                                <i class="fas fa-comments"></i> Chat
                            </button>
                        ` : ''}
                        ${appointment.status === 'pending' ? `
                            <button onclick="cancelAppointment(${appointment.id})" class="btn-cancel">
                                <i class="fas fa-times"></i> Cancel
                            </button>
                        ` : ''}
                    </div>
                </div>
            `).join('');
        });
}

// Load specializations
function loadSpecializations() {
    fetch('/api/specializations')
        .then(response => response.json())
        .then(specializations => {
            specializationSelect.innerHTML = `
                <option value="">Select Specialization</option>
                ${specializations.map(spec => `
                    <option value="${spec}">${spec}</option>
                `).join('')}
            `;
        });
}

// Load doctors by specialization
specializationSelect.addEventListener('change', () => {
    const specialization = specializationSelect.value;
    if (specialization) {
        fetch(`/api/doctors/${specialization}`)
            .then(response => response.json())
            .then(doctors => {
                doctorSelect.innerHTML = `
                    <option value="">Select Doctor</option>
                    ${doctors.map(doctor => `
                        <option value="${doctor.id}">Dr. ${doctor.name}</option>
                    `).join('')}
                `;
                doctorSelect.disabled = false;
            });
    } else {
        doctorSelect.disabled = true;
        doctorSelect.innerHTML = '<option value="">Select Doctor</option>';
    }
});

// Load available time slots
dateInput.addEventListener('change', () => {
    const doctorId = doctorSelect.value;
    const date = dateInput.value;
    if (doctorId && date) {
        fetch(`/api/time-slots/${doctorId}/${date}`)
            .then(response => response.json())
            .then(slots => {
                timeSlotSelect.innerHTML = `
                    <option value="">Select Time Slot</option>
                    ${slots.map(slot => `
                        <option value="${slot}">${slot}</option>
                    `).join('')}
                `;
                timeSlotSelect.disabled = false;
            });
    }
});

// Chat functionality
const chatModal = document.getElementById('chatModal');
const messageInput = document.getElementById('messageInput');
const chatMessages = document.getElementById('chatMessages');
let currentDoctorId = null;

function openChat(doctorId) {
    currentDoctorId = doctorId;
    chatModal.style.display = 'block';
    loadMessages(doctorId);
}

function loadMessages(doctorId) {
    fetch(`/api/messages/${doctorId}`)
        .then(response => response.json())
        .then(messages => {
            chatMessages.innerHTML = messages.map(message => `
                <div class="message ${message.sender_type === 'patient' ? 'sent' : 'received'}">
                    ${message.content}
                </div>
            `).join('');
            chatMessages.scrollTop = chatMessages.scrollHeight;
        });
}

document.getElementById('sendMessage').addEventListener('click', () => {
    const message = messageInput.value.trim();
    if (message && currentDoctorId) {
        fetch('/api/messages/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                doctor_id: currentDoctorId,
                message: message
            })
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                messageInput.value = '';
                loadMessages(currentDoctorId);
            }
        });
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadAppointments();
    loadSpecializations();
});

// Event listeners for modal controls
document.querySelectorAll('.close').forEach(closeBtn => {
    closeBtn.addEventListener('click', () => {
        closeBtn.closest('.modal').style.display = 'none';
    });
});

window.addEventListener('click', (event) => {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
});