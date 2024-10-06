document.addEventListener('DOMContentLoaded', function() {
    const themeSwitch = document.getElementById('theme-switch');
    const htmlElement = document.documentElement;

    function setTheme(theme) {
        htmlElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        themeSwitch.checked = theme === 'dark';
    }   

    themeSwitch.addEventListener('change', function() {
        setTheme(this.checked ? 'dark' : 'light');
    });

    // Check for saved theme preference or respect OS preference
    const savedTheme = localStorage.getItem('theme');
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    
    if (savedTheme) {
        setTheme(savedTheme);
    } else if (prefersDarkScheme.matches) {
        setTheme('dark');
    }

    // Custom cursor GIF logic
    const scheduleButton = document.getElementById('scheduleButton');
    const cursorGif = document.querySelector('.cursor-gif');

    scheduleButton.addEventListener('mouseenter', function(e) {
        cursorGif.style.display = 'block';
        document.body.classList.add('hide-cursor'); // Add this line
        moveCursor(e);
        document.addEventListener('mousemove', moveCursor);
    });

    scheduleButton.addEventListener('mouseleave', function() {
        cursorGif.style.display = 'none';
        document.body.classList.remove('hide-cursor'); // Add this line
        document.removeEventListener('mousemove', moveCursor);
    });

    function moveCursor(e) {
        cursorGif.style.left = e.clientX + 'px';
        cursorGif.style.top = e.clientY + 'px';
    }

    // Your existing JavaScript for handling navigation and other functionalities
    // ...

    // Add this at the end of the file
    const appointmentCard = document.getElementById('appointmentCard');
    const appointmentsContainer = document.getElementById('appointmentsContainer');
    const noAppointments = document.getElementById('noAppointments');
    const appointmentsTable = document.getElementById('appointmentsTable');
    const appointmentsTableBody = document.getElementById('appointmentsTableBody');
    const bookAppointmentBtn = document.getElementById('bookAppointmentBtn');
    const appointmentModal = document.getElementById('appointmentModal');
    const appointmentForm = document.getElementById('appointmentForm');
    const doctorSelect = document.getElementById('doctorSelect');
    const appointmentDate = document.getElementById('appointmentDate');
    const appointmentTime = document.getElementById('appointmentTime');

    function loadAppointments() {
        fetch('/get_user_appointments')
            .then(response => response.json())
            .then(appointments => {
                if (appointments.length === 0) {
                    noAppointments.style.display = 'block';
                    appointmentsTable.style.display = 'none';
                } else {
                    noAppointments.style.display = 'none';
                    appointmentsTable.style.display = 'table';
                    appointmentsTableBody.innerHTML = '';
                    appointments.forEach(appointment => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${appointment[3]}</td>
                            <td>${appointment[4]}</td>
                            <td>${appointment[1]}</td>
                            <td>${appointment[2]}</td>
                            <td><button class="btn-reschedule" data-id="${appointment[0]}">Reschedule</button></td>
                        `;
                        appointmentsTableBody.appendChild(row);
                    });
                    updateNextAppointment(appointments[0]);
                }
            })
            .catch(error => console.error('Error:', error));
    }

    function updateNextAppointment(appointment) {
        if (appointment) {
            appointmentCard.querySelector('p').textContent = `${appointment[3]} at ${appointment[4]}`;
        } else {
            appointmentCard.querySelector('p').textContent = 'No upcoming appointments';
        }
    }

    bookAppointmentBtn.addEventListener('click', () => {
        appointmentModal.style.display = 'block';
        loadDoctors();
    });

    appointmentModal.querySelector('.close').addEventListener('click', () => {
        appointmentModal.style.display = 'none';
    });

    function loadDoctors() {
        fetch('/get_available_doctors')
            .then(response => response.json())
            .then(doctors => {
                doctorSelect.innerHTML = '<option value="">Select a doctor</option>';
                doctors.forEach(doctor => {
                    const option = document.createElement('option');
                    option.value = doctor[0];
                    option.textContent = `${doctor[1]} - ${doctor[2]}`;
                    doctorSelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error:', error));
    }

    appointmentDate.addEventListener('change', loadAvailableSlots);
    doctorSelect.addEventListener('change', loadAvailableSlots);

    function loadAvailableSlots() {
        const doctorId = doctorSelect.value;
        const date = appointmentDate.value;
        if (doctorId && date) {
            fetch('/get_available_slots', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ doctor_id: doctorId, date: date }),
            })
                .then(response => response.json())
                .then(slots => {
                    appointmentTime.innerHTML = '<option value="">Select a time</option>';
                    slots.forEach(slot => {
                        const option = document.createElement('option');
                        option.value = slot;
                        option.textContent = slot;
                        appointmentTime.appendChild(option);
                    });
                })
                .catch(error => console.error('Error:', error));
        }
    }

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
            body: JSON.stringify({ doctor_id: doctorId, date: date, time_slot: time }),
        })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                appointmentModal.style.display = 'none';
                loadAppointments();
            })
            .catch(error => console.error('Error:', error));
    });

    loadAppointments();
});