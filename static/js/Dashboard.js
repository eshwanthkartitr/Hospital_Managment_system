document.addEventListener('DOMContentLoaded', function () {


    const themeSwitch = document.getElementById('theme-switch');
    const htmlElement = document.documentElement;

    function setTheme(theme) {
        htmlElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        if (themeSwitch) themeSwitch.checked = theme === 'dark';
    }

    if (themeSwitch) {
        themeSwitch.addEventListener('change', function () {
            setTheme(this.checked ? 'dark' : 'light');
        });
    }

    const savedTheme = localStorage.getItem('theme');
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');

    if (savedTheme) {
        setTheme(savedTheme);
    } else if (prefersDarkScheme.matches) {
        setTheme('dark');
    }

    const scheduleButton = document.getElementById('scheduleButton');
    const cursorGif = document.querySelector('.cursor-gif');

    if (scheduleButton) {
        scheduleButton.addEventListener('mouseenter', function (e) {
            cursorGif.style.display = 'block';
            document.body.classList.add('hide-cursor');
            moveCursor(e);
            document.addEventListener('mousemove', moveCursor);
        });

        scheduleButton.addEventListener('mouseleave', function () {
            cursorGif.style.display = 'none';
            document.body.classList.remove('hide-cursor');
            document.removeEventListener('mousemove', moveCursor);
        });
    }

    function moveCursor(e) {
        cursorGif.style.left = e.clientX + 'px';
        cursorGif.style.top = e.clientY + 'px';
    }

    const bookAppointmentBtn = document.getElementById('bookAppointmentBtn');
    const appointmentModal = document.getElementById('appointmentModal');

    if (bookAppointmentBtn && appointmentModal) {
        bookAppointmentBtn.addEventListener('click', () => {
            appointmentModal.style.display = 'block';
            document.getElementById("myAppointments").style.display = "none";
            loadDoctors();
        });

        appointmentModal.querySelector('.close').addEventListener('click', () => {
            appointmentModal.style.display = 'none';
            document.getElementById("myAppointments").style.display = "block";
        });
    }

    function loadDoctors() {
        fetch('/get_available_doctors')
            .then(response => response.json())
            .then(doctors => {
                const doctorSelect = document.getElementById('doctorSelect');
                if (doctorSelect) {
                    doctorSelect.innerHTML = '<option value="">Select a doctor</option>';
                    doctors.forEach(doctor => {
                        const option = document.createElement('option');
                        option.value = doctor[0];
                        option.textContent = `${doctor[1]} - ${doctor[2]}`;
                        doctorSelect.appendChild(option);
                    });
                }
            })
            .catch(error => console.error('Error:', error));
    }

    const appointmentForm = document.getElementById('appointmentForm');
    if (appointmentForm) {
        appointmentForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const doctorId = doctorSelect.value;
            const date = appointmentDate.value;
            const time = appointmentTime.value;

            fetch('/book_appointment', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        doctor_id: doctorId,
                        date: date,
                        time_slot: time
                    }),
                })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    appointmentModal.style.display = 'none';
                    loadAppointments();
                })
                .catch(error => console.error('Error:', error));
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        const appointmentsSection = document.getElementById('myAppointments');
        if (appointmentsSection) {
            console.log('Appointments section found');
            loadAppointments();
        } else {
            console.error('Element with ID "myAppointments" not found');
        }
    });



    const appointmentDate = document.getElementById('appointmentDate');
    const appointmentTime = document.getElementById('appointmentTime');

    if (appointmentDate && appointmentTime) {
        appointmentDate.addEventListener('change', () => {
            const selectedDoctor = document.querySelector('.doctor-item.selected');
            if (!selectedDoctor) {
                alert('Please select a doctor.');
                return;
            }

            const doctorId = selectedDoctor.dataset.id;
            const date = appointmentDate.value;
            const time = appointmentTime.value;

            fetch('/book_appointment', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        doctor_id: doctorId,
                        date: date,
                        time_slot: time
                    })
                })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    loadAppointments();
                })
                .catch(error => console.error('Error booking appointment:', error));
        });
    }

    const doctorSelect = document.getElementById('doctorSelect');
    const doctorSelection = document.getElementById('doctorList');

    if (doctorSelect && doctorSelection) {
        doctorSelect.addEventListener('change', () => {
            const selectedDoctor = document.querySelector('.doctor-item.selected');
            if (!selectedDoctor) {
                alert('Please select a doctor.');
                return;
            }

            const doctorId = selectedDoctor.dataset.id;
            const date = appointmentDate.value;
            const time = appointmentTime.value;

            fetch('/book_appointment', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        doctor_id: doctorId,
                        date: date,
                        time_slot: time
                    })
                })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    document.getElementById('doctorSelection').style.display = 'none';
                })
                .catch(error => console.error('Error booking appointment:', error));
        });
    }

    const doctorList = document.getElementById('doctorList');

    if (doctorList) {
        doctorList.addEventListener('click', function (e) {
            if (e.target.classList.contains('doctor-item')) {
                document.querySelectorAll('.doctor-item').forEach(item => item.classList.remove('selected'));
                e.target.classList.add('selected');
            }
        });
    }

    const scheduleModal = document.getElementById('scheduleModal');

    if (scheduleModal) {
        document.querySelector('.close').addEventListener('click', function () {
            scheduleModal.style.display = 'none';
            document.getElementById("myAppointments").style.display = "block";
        });

        window.onclick = function (event) {
            if (event.target === scheduleModal) {
                scheduleModal.style.display = 'none';
                document.getElementById("myAppointments").style.display = "block";
            }
        };
    }

    function loadAvailableDoctors() {
        fetch('/get_available_doctors')
            .then(response => response.json())
            .then(data => {
                const availableDoctors = document.getElementById('availableDoctors');
                data.forEach(doctor => {
                    const doctorElement = document.createElement('div');
                    doctorElement.textContent = `${doctor.name} - ${doctor.specialty}`;
                    doctorElement.dataset.id = doctor.id;
                    console.log("Loggin bro")
                    doctorElement.classList.add('doctor-item');
                    doctorElement.addEventListener('click', () => selectDoctor(doctor.id));
                    availableDoctors.appendChild(doctorElement);
                });
            })
            .catch(error => console.error('Error fetching doctors:', error));
    }

    document.addEventListener('DOMContentLoaded', loadAppointments);

    function loadAppointments() {
        const appointmentsList = document.getElementById('appointmentsList');
        if (!appointmentsList) {
            console.error('Element with ID "appointmentsList" not found');
            return;
        }

        fetch("/get_user_appointments")
            .then(response => response.json())
            .then(appointments => {
                appointmentsList.innerHTML = ''; // Clear previous appointments

                if (appointments.length === 0) {
                    appointmentsList.innerHTML = "<p>No appointments scheduled.</p>";
                    return;
                }

                appointments.forEach(appointment => {
                    const appointmentElement = document.createElement('div');
                    appointmentElement.classList.add('appointment-item');
                    appointmentElement.innerHTML = `
                        <h4>${appointment.doctor_name} (${appointment.specialty})</h4>
                        <p>Date: ${new Date(appointment.appointment_date).toLocaleDateString()}</p>
                        <p>Time: ${appointment.time_slot}</p>
                        <p class = "status-${appointment.status}">Status: ${appointment.status}</p>
                        <p>Memo: ${appointment.doctor_memo || "N/A"}</p>
                    `;
                    appointmentsList.appendChild(appointmentElement);
                });
            })
            .catch(error => {
                console.error("Error loading appointments:", error);
                appointmentsList.innerHTML = "<p>Error loading appointments. Please try again later.</p>";
            });
    }

    document.addEventListener('DOMContentLoaded', loadAvailableDoctors);
    let selectedDoctorId = null;

    function selectDoctor(doctorId) {
        selectedDoctorId = doctorId;
        const dateInput = document.getElementById('appointmentDate');
        dateInput.style.display = 'block'; // Show date input
        dateInput.addEventListener('change', () => fetchAvailableSlots(dateInput.value));
    }

    const slotsContainer = document.getElementById('slotsContainer');
    let selectedSlot = null;

    appointmentDate.addEventListener('change', function () {
        const date = this.value;
        const doctorId = selectedDoctorId; // Assume this is set when a doctor is selected

        fetchAvailableSlots(date, doctorId);
    });

    function fetchAvailableSlots(date, doctorId) {
        fetch('/get_available_slots', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    date: date,
                    doctor_id: doctorId
                })
            })
            .then(response => response.json())
            .then(availableSlots => {
                slotsContainer.innerHTML = ''; // Clear previous slots

                const allSlots = [
                    "08:00", "09:00", "10:00", "11:00", "12:00",
                    "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"
                ];

                allSlots.forEach(slot => {
                    const slotElement = document.createElement('div');
                    slotElement.textContent = slot;
                    slotElement.classList.add('slot');

                    if (availableSlots.includes(slot)) {
                        slotElement.classList.add('available');
                        slotElement.addEventListener('click', () => selectSlot(slot));
                    } else {
                        slotElement.classList.add('booked');
                    }

                    slotsContainer.appendChild(slotElement);
                });
            })
            .catch(error => console.error('Error fetching slots:', error));
    }

    function selectSlot(slot) {
        console.log(slot);
        if (selectedSlot) {
            selectedSlot.classList.remove('selected');
        }

        const slots = document.querySelectorAll('.slot');
        selectedSlot = Array.from(slots).find(el => el.textContent.trim() === slot);

        if (selectedSlot) {
            selectedSlot.classList.add('selected');
        } else {
            console.error('Slot not found');
        }
    }


    document.getElementById('bookAppointmentBtn').addEventListener('click', function () {
        if (!selectedSlot) {
            alert('Please select a slot.');
            return;
        }

        const date = appointmentDate.value;
        const timeSlot = selectedSlot.textContent;
        const doctorId = selectedDoctorId;

        fetch('/book_appointment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    doctor_id: doctorId,
                    date: date,
                    time_slot: timeSlot
                })
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                loadAppointments(); // Refresh appointments
            })
            .catch(error => console.error('Error booking appointment:', error));
    });

    function notifyDoctor(doctorId, appointmentId) {
        fetch('/notify_doctor', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    doctor_id: doctorId,
                    appointment_id: appointmentId
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Doctor notified:', data);
            })
            .catch(error => console.error('Error notifying doctor:', error));
    }
});


document.getElementById('confirmAppointment').addEventListener('click', function () {
    const selectedDoctor = document.querySelector('.doctor-item.selected');
    const selectedSlot = document.querySelector('.slot.selected');
    if (!selectedDoctor) {
        alert('Please select a doctor.');
        return;
    }

    const doctorId = selectedDoctor.dataset.id;
    const date = document.getElementById('appointmentDate').value;
    const timeSlot = selectedSlot ? selectedSlot.textContent : null;

    if (!timeSlot) {
        alert('Please select a time slot.');
        return;
    }

    fetch('/book_appointment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                doctor_id: doctorId,
                date: date,
                time_slot: timeSlot
            })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            const appointmentsList = document.getElementById('appointmentsList');
            if (!appointmentsList) {
                console.error('Element with ID "appointmentsList" not found');
                return;
            }

            fetch("/get_user_appointments")
                .then(response => response.json())
                .then(appointments => {
                    appointmentsList.innerHTML = ''; // Clear previous appointments

                    if (appointments.length === 0) {
                        appointmentsList.innerHTML = "<p>No appointments scheduled.</p>";
                        return;
                    }

                    appointments.forEach(appointment => {
                        const appointmentElement = document.createElement('div');
                        appointmentElement.classList.add('appointment-item');
                        appointmentElement.innerHTML = `
                        <h4>${appointment.doctor_name} (${appointment.specialty})</h4>
                        <p>Date: ${new Date(appointment.appointment_date).toLocaleDateString()}</p>
                        <p>Time: ${appointment.time_slot}</p>
                        <p class = "status-${appointment.status}">Status: ${appointment.status}</p>
                        <p>Memo: ${appointment.doctor_memo || "N/A"}</p>
                    `;
                        appointmentsList.appendChild(appointmentElement);
                    });
                })
                .catch(error => {
                    console.error("Error loading appointments:", error);
                    appointmentsList.innerHTML = "<p>Error loading appointments. Please try again later.</p>";
                }); // Refresh appointments
        })
        .catch(error => console.error('Error booking appointment:', error));
});

document.getElementById('doctorList').addEventListener('click', function (e) {
    if (e.target.classList.contains('doctor-item')) {
        document.querySelectorAll('.doctor-item').forEach(item => item.classList.remove('selected'));
        e.target.classList.add('selected');
    }
});

document.querySelector('.close').addEventListener('click', function () {
    document.getElementById('scheduleModal').style.display = 'none';
    document.getElementById("myAppointments").style.display = "block";
});

window.onclick = function (event) {
    if (event.target === document.getElementById('scheduleModal')) {
        document.getElementById('scheduleModal').style.display = 'none';
    }
};

let selectedDoctorId = null;

function selectDoctor(doctorId) {
    selectedDoctorId = doctorId;
    const dateInput = document.getElementById('appointmentDate');
    dateInput.style.display = 'block'; // Show date input
    dateInput.addEventListener('change', () => fetchAvailableSlots(dateInput.value));
}

function fetchAvailableSlots(date) {
    if (!selectedDoctorId) return;

    fetch('/get_available_slots', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                date: date,
                doctor_id: selectedDoctorId
            })
        })
        .then(response => response.json())
        .then(availableSlots => {
            const slotsContainer = document.getElementById('slotsContainer');
            slotsContainer.innerHTML = ''; // Clear previous slots

            const allSlots = Array.from({
                length: 12
            }, (_, i) => `${9 + i}:00`); // 9 AM to 8 PM
            allSlots.forEach(slot => {
                const slotElement = document.createElement('div');
                slotElement.textContent = slot;
                slotElement.classList.add('slot');

                if (availableSlots.includes(slot)) {
                    slotElement.classList.add('available');
                    slotElement.addEventListener('click', () => bookAppointment(slot, date));
                } else {
                    slotElement.classList.add('booked');
                }

                slotsContainer.appendChild(slotElement);
            });
        })
        .catch(error => console.error('Error fetching slots:', error));
}

function bookAppointment(slot, date) {
    fetch('/book_appointment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                doctor_id: selectedDoctorId,
                date: date,
                time_slot: slot
            })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            loadAppointments(); // Refresh appointments// Optionally refresh the slots or clear selections
        })
        .catch(error => console.error('Error booking appointment:', error));
}

function notifyDoctor(doctorId, appointmentId) {
    fetch('/notify_doctor', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                doctor_id: doctorId,
                appointment_id: appointmentId
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Doctor notified:', data);
        })
        .catch(error => console.error('Error notifying doctor:', error));
}
