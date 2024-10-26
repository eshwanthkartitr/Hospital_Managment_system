from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_admin import Admin, BaseView, expose
from flask_admin import AdminIndexView
from flask_admin.menu import MenuLink
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import psycopg2
from psycopg2 import pool
import spacy
import PyPDF2
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
import redis
import base64
from datetime import datetime, timedelta
from resume import review_resume
from flask_mail import Mail, Message

# Create the Flask application instance
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a real secret key

# Redis Configuration
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')

# Initialize the session extension
Session(app)

# Load the English language model
nlp = spacy.load("en_core_web_sm")

# Create a PostgreSQL connection pool
db_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dbname="ehms",
    user="postgres",
    password="Tr@310305",
    host="localhost",
    port="5432"
)


def get_db_connection():
    return db_pool.getconn()


def release_db_connection(conn):
    db_pool.putconn(conn)


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file_pdf(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        gender = request.form['gender']
        medical_record = request.form['medical_record']

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO patients (name, email, phone, password, gender, medical_record)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (name, email, phone, hashed_password, gender, medical_record))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return jsonify({"message": "Registration successful"}), 200
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Database error: {e}")
            return jsonify({"message": "Registration failed. Please try again."}), 500
        finally:
            release_db_connection(conn)

    return render_template('patient_register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        patient_name = request.form['id']
        password = request.form['password']
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT name,password FROM admins")
                user = cur.fetchall()
                for i in user:
                    if patient_name == i[0]:
                        if password == i[1]:
                            session['is_admin'] = True
                            break
            print(session)
            print(user)
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return jsonify({"message": "Login failed. Please try again."}), 500
        finally:
            release_db_connection(conn)

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM patients WHERE name = %s", (patient_name,))
                user = cur.fetchone()

                # Assuming password is at index 4
                if user and check_password_hash(user[4], password):
                    session['user_id'] = user[0]  # Store user ID in session
                    session['name'] = user[1]
                    session['user_type'] = 'patient'
                    flash('Logged in successfully!', 'success')
                    return jsonify({"message": "Login successful"}), 200
                else:
                    flash('Invalid credentials. Please try again.', 'error')
                    return jsonify({"message": "Invalid credentials"}), 401
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return jsonify({"message": "Login failed. Please try again."}), 500
        finally:
            release_db_connection(conn)

    return render_template('patient_login.html')


@app.route('/doctor/login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        doctor_name = request.form['id']
        password = request.form['password']

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM doctors WHERE name = %s", (doctor_name,))
                doctor = cur.fetchone()

                if doctor:
                    if doctor[4] == password:  # Assuming password is at index 4
                        session['user_id'] = doctor[0]
                        session['user_type'] = 'doctor'
                        session['name'] = doctor[1]
                        print(session)
                        flash('Logged in successfully!', 'success')
                        return redirect(url_for('doctor_dashboard'))
                    else:
                        flash('Invalid credentials. Please try again.', 'error')
                        return redirect(url_for('doctor_login'))
                else:
                    flash('Doctor not found. Please apply first.', 'info')
                    return redirect(url_for('doctor_apply'))
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return jsonify({"message": "Login failed. Please try again."}), 500
        finally:
            release_db_connection(conn)

    return render_template('doctor_login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('login'))

    if session.get('user_type') == 'doctor':
        return redirect(url_for('doctor_dashboard'))

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, email, phone, gender, medical_record, profile_pic FROM patients WHERE id = %s", (session['user_id'],))
            user = cur.fetchone()
            if user and user[6]:
                profile_pic_base64 = base64.b64encode(user[6]).decode('utf-8')
            else:
                profile_pic_base64 = None
        return render_template('patient_dashboard.html', user=user, profile_pic=profile_pic_base64)
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        flash('Error fetching user data', 'error')
        return redirect(url_for('login'))
    finally:
        release_db_connection(conn)


@app.route('/change_password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return jsonify({"message": "Please log in to change your password."}), 401

    current_password = request.form['current_password']
    new_password = request.form['new_password']

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT password FROM patients WHERE id = %s",
                        (session['user_id'],))
            stored_password = cur.fetchone()[0]

            if check_password_hash(stored_password, current_password):
                hashed_new_password = generate_password_hash(new_password)
                cur.execute("UPDATE patients SET password = %s WHERE id = %s",
                            (hashed_new_password, session['user_id']))
                conn.commit()
                flash('Password updated successfully!', 'success')
                return jsonify({"message": "Password updated successfully"}), 200
            else:
                flash('Current password is incorrect.', 'error')
                return jsonify({"message": "Current password is incorrect"}), 400
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Database error: {e}")
        return jsonify({"message": "Password update failed. Please try again."}), 500
    finally:
        release_db_connection(conn)


@app.route('/update_profile_pic', methods=['POST'])
def update_profile_pic():
    if 'user_id' not in session:
        return jsonify({"message": "Please log in to update your profile picture."}), 401

    if 'profile_pic' not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files['profile_pic']

    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    if file and allowed_file(file.filename):
        file_data = file.read()

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE patients SET profile_pic = %s WHERE id = %s",
                            (psycopg2.Binary(file_data), session['user_id']))
            conn.commit()
            flash('Profile picture updated successfully!', 'success')
            return jsonify({"message": "Profile picture updated successfully"}), 200
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Database error: {e}")
            return jsonify({"message": "Profile picture update failed. Please try again."}), 500
        finally:
            release_db_connection(conn)
    else:
        return jsonify({"message": "File type not allowed"}), 400


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_type', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Function to extract text from a PDF file


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

# Preprocess the text for NLP


def preprocess_text(text):
    doc = nlp(text.lower())
    return [token.lemma_ for token in doc if not token.is_stop and not token.is_punct and token.has_vector]

# Get document embeddings using spaCy


def get_document_embedding(text):
    doc = nlp(" ".join(preprocess_text(text)))
    return doc.vector

# Calculate similarity between two vectors


def calculate_similarity(vec1, vec2):
    return cosine_similarity(vec1.reshape(1, -1), vec2.reshape(1, -1))[0][0]

# Review the resume against a job description


def review_resume(resume_text, job_description):
    resume_processed = preprocess_text(resume_text)
    job_processed = preprocess_text(job_description)

    resume_embedding = get_document_embedding(resume_text)
    job_embedding = get_document_embedding(job_description)

    similarity_score = calculate_similarity(resume_embedding, job_embedding)

    resume_words = set(resume_processed)
    job_words = set(job_processed)
    common_words = resume_words.intersection(job_words)

    word_importance = {}
    for word in common_words:
        word_vec = nlp(word).vector
        importance = calculate_similarity(word_vec, job_embedding)
        word_importance[word] = importance

    top_words = sorted(word_importance.items(),
                       key=lambda x: x[1], reverse=True)[:10]
    missing_words = list(job_words - resume_words)[:5]

    return similarity_score, top_words, missing_words


@app.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        specialization = request.form['specialization']
        experience = request.form['experience']
        resume = request.files['resume']

        if resume:
            resume_filename = f"{name.replace(' ', '_')}_resume.pdf"
            resume_path = os.path.join(
                app.config['UPLOAD_FOLDER'], resume_filename)
            resume.save(resume_path)

            resume_text = extract_text_from_pdf(resume_path)

            job_descriptions = {
                "ENT": "Seeking an experienced ENT specialist with skills in diagnosis and treatment of ear, nose, and throat disorders.",
                "Cardiology": "Looking for a cardiologist with expertise in heart disease diagnosis, ECG interpretation, and cardiac catheterization.",
            }

            job_description = job_descriptions.get(
                specialization, "Generic medical professional with relevant experience")

            similarity_score, top_words, missing_words = review_resume(
                resume_text, job_description)

            similarity_score = float(similarity_score)

            conn = get_db_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO doctor_applications (name, email, specialization, experience, resume_path, similarity_score)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (name, email, specialization, experience, resume_path, similarity_score))
                    application_id = cur.fetchone()[0]
                conn.commit()
                flash('Application submitted successfully!', 'success')
                return jsonify({
                    "message": "Application submitted successfully",
                    "application_id": application_id,
                    "similarity_score": similarity_score,
                    "top_words": dict(top_words),
                    "missing_words": missing_words
                }), 200
            except psycopg2.Error as e:
                conn.rollback()
                print(f"Database error: {e}")
                return jsonify({"message": "Application submission failed. Please try again."}), 500
            finally:
                release_db_connection(conn)

    return render_template('doctor_apply.html')


@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({"message": "Please log in to update your profile."}), 401

    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    gender = request.form['gender']
    medical_record = request.form['medical_record']
    specialty = request.form.get('specialty')

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            if session.get('user_type') == 'doctor':
                cur.execute("""
                    UPDATE doctors
                    SET name = %s, email = %s, phone = %s, specialty = %s
                    WHERE id = %s
                """, (name, email, phone, specialty, session['user_id']))
            else:
                cur.execute("""
                    UPDATE patients
                    SET name = %s, email = %s, phone = %s
                    WHERE id = %s
                """, (name, email, phone, session['user_id']))
        conn.commit()
        return jsonify({"message": "Profile updated successfully"}), 200
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Database error: {e}")
        return jsonify({"message": "Profile update failed. Please try again."}), 500
    finally:
        release_db_connection(conn)


@app.route('/get_appointments', methods=['GET'])
def get_appointments():
    if 'user_id' not in session:
        return jsonify({"message": "Please log in to view appointments."}), 401

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id,patient_name, time_slot,appointment_date FROM appointments WHERE doctor_id = %s", (session['user_id'],))
            appointments = cur.fetchall()
            appointment_list = []
            for appointment in appointments:
                appointment_dict = {
                    "id": appointment[0],   
                    "patient_name": appointment[1],
                    "time_slot": appointment[2].strftime('%H:%M:%S'),
                    "Date": appointment[3]
                }
                appointment_list.append(appointment_dict)

            return jsonify(appointment_list), 200
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return jsonify({"message": "Error fetching appointments"}), 500
    finally:
        release_db_connection(conn)


@app.route('/get_available_doctors', methods=['GET'])
def get_available_doctors():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, specialty FROM doctors")
            doctors = cur.fetchall()
            print(doctors)
        return jsonify(doctors), 200
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return jsonify({"message": "Error fetching doctors"}), 500
    finally:
        release_db_connection(conn)


@app.route('/get_available_slots', methods=['POST'])
def get_available_slots():
    if 'user_id' not in session:
        return jsonify({"message": "Please log in to view available slots."}), 401

    date = request.json['date']
    doctor_id = request.json['doctor_id']

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT time_slot FROM appointments
                WHERE doctor_id = %s AND appointment_date = %s
            """, (doctor_id, date))
            booked_slots = [row[0] for row in cur.fetchall()]

            # 8 AM to 8 PM, excluding 1 PM
            all_slots = [f"{h:02d}:00" for h in range(8, 21) if h != 13]
            available_slots = [
                slot for slot in all_slots if slot not in booked_slots]

        return jsonify(available_slots), 200
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return jsonify({"message": "Error fetching available slots"}), 500
    finally:
        release_db_connection(conn)


@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    if 'user_id' not in session:
        return jsonify({"message": "Please log in to book an appointment."}), 401

    doctor_id = request.json['doctor_id']
    date = request.json['date']
    time_slot = request.json['time_slot']

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Fetch the doctor's specialty from the doctors table
            cur.execute("""
                SELECT specialty FROM doctors WHERE id = %s
            """, (doctor_id,))

            doctor_specialty = cur.fetchone()

            # Check if the doctor exists and has a specialty
            if doctor_specialty is None:
                return jsonify({"message": "Doctor not found or specialty missing."}), 404

            specialty = doctor_specialty[0]  # Extract the specialty value

            cur.execute("""
                INSERT INTO appointments (patient_id, doctor_id, appointment_date, time_slot, specialty, patient_name)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (session['user_id'], doctor_id, date, time_slot, specialty, session['name']))

        # Commit the transaction
        conn.commit()
        return jsonify({"message": "Appointment booked successfully"}), 200
    except psycopg2.Error as e:
        conn.rollback()  # Rollback in case of error
        print(f"Database error: {e}")
        return jsonify({"message": "Appointment booking failed. Please try again."}), 500
    finally:
        release_db_connection(conn)


@app.route('/get_user_appointments', methods=['GET'])
def get_user_appointments():
    if 'user_id' not in session:
        return jsonify({"message": "Please log in to view appointments."}), 401

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT a.id, d.name, d.specialty, a.appointment_date, a.time_slot, a.status, a.doctor_memo
                FROM appointments a
                JOIN doctors d ON a.doctor_id = d.id
                WHERE a.patient_id = %s
                ORDER BY a.appointment_date, a.time_slot
            """, (session['user_id'],))
            appointments = cur.fetchall()

            # Convert time_slot to string
            appointments = [
                {
                    "id": a[0],
                    "doctor_name": a[1],
                    "specialty": a[2],
                    "appointment_date": a[3].isoformat(),
                    "time_slot": a[4].strftime("%H:%M"),
                    "status": a[5],
                    "doctor_memo": a[6]
                }
                for a in appointments
            ]

        return jsonify(appointments), 200
    except psycopg2.Error as e:
        return jsonify({"message": "Error fetching appointments"}), 500
    finally:
        release_db_connection(conn)


@app.route('/doctor/apply', methods=['GET', 'POST'])
def doctor_apply():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        specialization = request.form['specialization']
        experience = request.form['experience']

        if 'resume' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        file = request.files['resume']

        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        if file and allowed_file_pdf(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Process the resume
            job_description = f"Doctor specializing in {
                specialization} with {experience} years of experience"
            similarity_score, top_words, missing_words = review_resume(
                file_path, job_description)

            # Convert similarity_score to a standard Python float
            similarity_score = float(similarity_score)

            conn = get_db_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO doctor_applications (name, email, specialization, experience, resume_path, similarity_score, status)
                        VALUES (%s, %s, %s, %s, %s, %s, 'pending')
                    """, (name, email, specialization, experience, file_path, similarity_score))
                conn.commit()
                flash('Application submitted successfully', 'success')
                return redirect(url_for('application_tracker'))
            except psycopg2.Error as e:
                conn.rollback()
                print(f"Database error: {e}")
                return jsonify({"message": "Application submission failed. Please try again."}), 500
            finally:
                release_db_connection(conn)

    return render_template('doctor_apply.html')


@app.route('/application_tracker')
def application_tracker():
    if 'user_id' not in session:
        flash('Please log in to view your applications.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, email, specialization, experience, resume_path, status
                FROM doctor_applications
                WHERE name = %s
            """, (session['name'],))
            applications = cur.fetchall()
            print(applications)
        return render_template('application_tracker.html', applications=applications)
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        flash('Error retrieving applications', 'error')
        return redirect(url_for('doctor_dashboard'))
    finally:
        release_db_connection(conn)


@app.route('/hr/review', methods=['GET', 'POST'])
def hr_review():
    conn = get_db_connection()
    if not session.get('is_admin'):
        return redirect(url_for('dashboard'))
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, email, specialization, experience, resume_path FROM doctor_applications WHERE status = 'pending'")
            applications = cur.fetchall()
            cur.execute("SELECT id, name, specialty FROM doctors")
            doctors = cur.fetchall()
            cur.execute("SELECT id, name, email FROM patients")
            patients = cur.fetchall()

        if request.method == 'POST':
            job_description = request.form.get('job_description')
            application_id = request.form.get('application_id')

            # Get the selected application
            selected_application = next(
                (app for app in applications if app[0] == int(application_id)), None)
            if selected_application:
                resume_path = selected_application[5]
                similarity_score, top_words, missing_words = review_resume(
                    resume_path, job_description)

                return render_template('hr_review.html', applications=applications, selected_application=selected_application, similarity_score=similarity_score, top_words=top_words, missing_words=missing_words, doctors=doctors, patients=patients)
        print(patients,doctors,applications)
        return render_template('hr_review.html', patients=patients, doctors=doctors, applications=applications)
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        flash('Error retrieving data', 'error')
        return redirect(url_for('dashboard'))
    finally:
        release_db_connection(conn)


@app.route('/hr/approve/<int:app_id>', methods=['POST'])
def approve_application(app_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Get application details
            cur.execute(
                "SELECT * FROM doctor_applications WHERE id = %s", (app_id,))
            application = cur.fetchone()

            if application:
                # Insert into doctors table
                cur.execute("""
                    INSERT INTO doctors (name,specialty,email,password)
                    VALUES (%s, %s, %s,%s)
                """, (application[1], application[2], application[3], application[4]))

                # Update application status
                cur.execute(
                    "UPDATE doctor_applications SET status = 'accepted' WHERE id = %s", (app_id,))
                conn.commit()

                # Send approval email
                send_approval_email(application[2])

                flash('Application approved and doctor added to the system', 'success')
            else:
                flash('Application not found', 'error')
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error updating application status: {e}")
        flash('Error approving application', 'error')
    finally:
        release_db_connection(conn)
    return redirect(url_for('hr_review'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/hr/reject/<int:app_id>', methods=['POST'])
def reject_application(app_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Check if the application exists
            cur.execute(
                "SELECT email FROM doctor_applications WHERE id = %s", (app_id,))
            application = cur.fetchone()

            if application:
                # Update application status
                cur.execute(
                    "UPDATE doctor_applications SET status = 'rejected' WHERE id = %s", (app_id,))
                conn.commit()

                send_rejection_email(application[0])

                flash('Application rejected', 'success')
            else:
                flash('Application not found', 'error')
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Database error: {e}")
        flash('Error processing application', 'error')
    finally:
        release_db_connection(conn)
    return redirect(url_for('hr_review'))

# Add a route for doctor dashboard


@app.route('/doctor/dashboard')
def doctor_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('doctor_login'))

    user_id = session['user_id']
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT name, specialty FROM doctors WHERE id = %s", (user_id,))
            doctor = cur.fetchone()
            if not doctor:
                flash('Doctor not found', 'error')
                return redirect(url_for('doctor_login'))

            doctor_info = {'name': doctor[0], 'specialty': doctor[1]}
            return render_template('doctor_dashboard.html', user=doctor_info)
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        flash('Error loading dashboard', 'error')
        return redirect(url_for('doctor_login'))
    finally:
        release_db_connection(conn)



@app.route('/send_message', methods=['POST'])
def send_message():
    user_id = session.get('user_id')
    user_type = session.get('user_type')
    partner_id = request.json['partner_id']  
    message = request.json['message']
    print(f"User ID: {user_id}, User Type: {user_type}")  # Debug print

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Check if a chat room already exists
            cur.execute("""
                SELECT id FROM chat_rooms
                WHERE (doctor_id = %s AND patient_id = %s) OR (doctor_id = %s AND patient_id = %s)
            """, (user_id, partner_id, partner_id, user_id))
            chat_room = cur.fetchone()
            if not chat_room:
                # Create a new chat room if it doesn't exist
                if user_type == 'doctor':
                    cur.execute("""
                        INSERT INTO chat_rooms (doctor_id, patient_id, created_at)
                        VALUES (%s, %s, NOW()) RETURNING id
                    """, (user_id, partner_id))
                else:
                    cur.execute("""
                        INSERT INTO chat_rooms (doctor_id, patient_id, created_at)
                        VALUES (%s, %s, NOW()) RETURNING id
                    """, (partner_id, user_id))

                chat_room_id = cur.fetchone()[0]
            else:
                chat_room_id = chat_room[0]

            print(f"User ID: {user_id}, User Type: {user_type}")  # Debug print
            cur.execute("""
                INSERT INTO messages (chat_room_id, sender_type, sender_id, message, created_at, is_read)
                VALUES (%s, %s, %s, %s, NOW(), FALSE)
            """, (chat_room_id, user_type, user_id, message))
            print("Hello : ",user_type)
            conn.commit()
            return jsonify({'message': 'Message sent successfully', 'chat_room_id': chat_room_id}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        release_db_connection(conn)


@app.route('/get_messages/<int:chat_room_id>', methods=['GET'])
def get_messages(chat_room_id):
    print("chat_room_id : ", chat_room_id)
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT sender_type, message, created_at
                FROM messages
                WHERE chat_room_id = %s
                ORDER BY created_at ASC
            """, (chat_room_id,))
            messages = cur.fetchall()
            print(messages)
        return jsonify(messages)
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        release_db_connection(conn)


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'eshwanthkartitr@gmail.com'
app.config['MAIL_PASSWORD'] = 'jyxt iwfk aubt qdrg'

mail = Mail(app)


def send_approval_email(email):
    msg = Message('Application Approved',
                  sender='eshwanthkartitr@gmail.com', recipients=[email])
    msg.body = "Congratulations! Your application to join our medical team has been approved."
    mail.send(msg)


def send_rejection_email(email):
    msg = Message('Application Status Update',
                  sender='eshwanthkartitr@gmail.com', recipients=[email])
    msg.body = (
        "Dear Applicant,\n\n"
        "Thank you for your interest in joining our esteemed medical team. "
        "After careful consideration, we regret to inform you that we will not be proceeding with your application at this time. "
        "We appreciate the effort you put into your application and encourage you to apply again in the future.\n\n"
        "Best regards,\n"
        "The EHMS Team"
    )
    mail.send(msg)


@app.errorhandler(400)
def bad_request(e):
    return render_template('error.html', error=400), 400


@app.route('/admin/remove_doctor/<int:doctor_id>', methods=['POST'])
def remove_doctor(doctor_id):
    print("My acess : ",session.get('is_admin'))
    if not session.get('is_admin'):
        flash('Access denied. Admins only.', 'error')
        return redirect(url_for('login'))
    print("My acess : ",session.get('is_admin'),doctor_id)
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM appointments WHERE doctor_id = %s", (doctor_id,))
        conn.commit()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM chat_rooms WHERE doctor_id = %s", (doctor_id,))
        conn.commit()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM doctors WHERE id = %s", (doctor_id,))
        conn.commit()
        print("Doctor removed successfully.")
        flash('Doctor removed successfully.', 'success')
    except psycopg2.Error as e:
        conn.rollback()
        flash('Error removing doctor.', 'error')
    finally:
        release_db_connection(conn)
    print("My acess : ",session.get('is_admin'),doctor_id)
    return redirect(url_for('hr_review'))


@app.route('/admin/remove_patient/<int:patient_id>', methods=['POST'])
def remove_patient(patient_id):
    if not session.get('is_admin'):
        flash('Access denied. Admins only.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Step 1: Delete messages associated with the patient's chat rooms
            cur.execute("""
                DELETE FROM messages
                USING chat_rooms
                WHERE messages.chat_room_id = chat_rooms.id
                AND chat_rooms.patient_id = %s
            """, (patient_id,))
        conn.commit()

        with conn.cursor() as cur:
            # Step 2: Delete chat rooms associated with the patient
            cur.execute("DELETE FROM chat_rooms WHERE patient_id = %s", (patient_id,))
        conn.commit()

        with conn.cursor() as cur:
            # Step 3: Delete appointments associated with the patient
            cur.execute("DELETE FROM appointments WHERE patient_id = %s", (patient_id,))
        conn.commit()

        with conn.cursor() as cur:
            # Step 4: Delete the patient record
            cur.execute("DELETE FROM patients WHERE id = %s", (patient_id,))
        conn.commit()

        flash('Patient removed successfully.', 'success')
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error removing patient: {e}")
        flash('Error removing patient.', 'error')
    finally:
        release_db_connection(conn)
    return redirect(url_for('hr_review'))


@app.route('/create_chat_room', methods=['POST'])
def create_chat_room():
    user_id = session.get('user_id')
    user_type = session.get('user_type')
    partner_id = request.json['partner_id']
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id FROM chat_rooms
                WHERE (doctor_id = %s AND patient_id = %s) OR (doctor_id = %s AND patient_id = %s)
            """, (user_id, partner_id, partner_id, user_id))
            chat_room = cur.fetchone()

            if chat_room:
                return jsonify({'chat_room_id': chat_room[0]})

            # Create a new chat room
            if user_type == 'doctor':
                cur.execute("""
                    INSERT INTO chat_rooms (doctor_id, patient_id, created_at)
                    VALUES (%s, %s, NOW()) RETURNING id
                """, (user_id, partner_id))
            else:
                cur.execute("""
                    INSERT INTO chat_rooms (doctor_id, patient_id, created_at)
                    VALUES (%s, %s, NOW()) RETURNING id
                """, (partner_id, user_id))

            new_chat_room_id = cur.fetchone()[0]
            conn.commit()
            return jsonify({'chat_room_id': new_chat_room_id})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)})
    finally:
        release_db_connection(conn)


@app.route('/broadcast_message', methods=['POST'])
def broadcast_message():
    user_id = session.get('user_id')
    user_type = session.get('user_type')
    message = request.form['message']

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            if user_type == 'doctor':
                # Fetch all patient IDs
                cur.execute("SELECT id FROM patients")
                recipient_ids = cur.fetchall()
                sender_type = 'doctor'
            else:
                # Fetch all doctor IDs
                cur.execute("SELECT id FROM doctors")
                recipient_ids = cur.fetchall()
                sender_type = 'patient'

            # Create a chat room for each recipient if it doesn't exist
            for recipient_id in recipient_ids:
                cur.execute("""
                    INSERT INTO chat_rooms (doctor_id, patient_id, created_at)
                    VALUES (%s, %s, NOW())
                    ON CONFLICT DO NOTHING
                """, (user_id, recipient_id[0]))

                # Get the chat room ID
                cur.execute("""
                    SELECT id FROM chat_rooms WHERE doctor_id = %s AND patient_id = %s
                """, (user_id, recipient_id[0]))
                chat_room_id = cur.fetchone()[0]

                # Insert the message
                cur.execute("""
                    INSERT INTO messages (chat_room_id, sender_type, sender_id, message, created_at, is_read)
                    VALUES (%s, %s, %s, %s, NOW(), FALSE)
                """, (chat_room_id, sender_type, user_id, message))

            conn.commit()
            return jsonify({'status': 'Messages sent'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        release_db_connection(conn)


@app.route('/available_doctors', methods=['GET'])
def available_doctors():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM doctors")
            doctors = cur.fetchall()
        return jsonify({'doctors': doctors})
    finally:
        release_db_connection(conn)


def send_otp(phone_number, otp):
    account_sid = 'ACb76585657c40f7b84565e2ab6ae18d29'
    auth_token = '9fdde09dce41cc8137460abefb63aa4e'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=f"Your OTP is {otp}",
        from_='+918438967169',  # Your Twilio number
        to=phone_number
    )
    return message.sid


@app.route('/appointments/accept/<int:appointment_id>', methods=['POST'])
def accept_appointment(appointment_id):
    if 'user_id' not in session or session.get('user_type') != 'doctor':
        return jsonify({"message": "Unauthorized access."}), 403

    memo = request.json.get('memo')  # Use request.json to get JSON data
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE appointments
                SET status = 'accepted', doctor_memo = %s
                WHERE id = %s AND doctor_id = %s
            """, (memo, appointment_id, session['user_id']))
        conn.commit()
        return jsonify({"message": "Appointment accepted."}), 200
    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({"message": "Error accepting appointment."}), 500
    finally:
        release_db_connection(conn)


@app.route('/appointments/reject/<int:appointment_id>', methods=['POST'])
def reject_appointment(appointment_id):
    if 'user_id' not in session or session.get('user_type') != 'doctor':
        return jsonify({"message": "Unauthorized access."}), 403

    memo = request.json.get('memo')  # Use request.json to get JSON data
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE appointments
                SET status = 'rejected', doctor_memo = %s
                WHERE id = %s AND doctor_id = %s
            """, (memo, appointment_id, session['user_id']))
        conn.commit()
        return jsonify({"message": "Appointment rejected."}), 200
    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({"message": "Error rejecting appointment."}), 500
    finally:
        release_db_connection(conn)

@app.route('/get_chat_partners', methods=['GET'])
def get_chat_partners():
    user_id = session.get('user_id')
    user_type = session.get('user_type')
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Fetch all doctors and patients
            if(user_type == 'doctor'):
                cur.execute("SELECT id, name FROM patients")
                patients = cur.fetchall()
                partners = [{'id': pat[0], 'name': pat[1], 'type': 'patient'} for pat in patients]
            else:
                cur.execute("SELECT id, name FROM doctors")
                doctors = cur.fetchall()
                partners = [{'id': doc[0], 'name': doc[1], 'type': 'doctor'} for doc in doctors]
                
            cur.execute("""
                SELECT id, doctor_id, patient_id FROM chat_rooms
            """)
            chat_rooms = cur.fetchall()

            # Map chat rooms to partners
            for partner in partners:
                partner['chat_room_id'] = next(
                    (room[0] for room in chat_rooms if (room[1] == partner['id'] and user_type == 'patient') or
                     (room[2] == partner['id'] and user_type == 'doctor')), None)

            print("partners : ", partners)
        return jsonify(partners)
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        release_db_connection(conn)


@app.route('/respond_to_appointment', methods=['POST'])
def respond_to_appointment():
    if 'user_id' not in session or session.get('user_type') != 'doctor':
        return jsonify({"message": "Unauthorized access."}), 403

    appointment_id = request.json['appointment_id']
    response_message = request.json['message']

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE appointments
                SET status = 'responded', doctor_memo = %s
                WHERE id = %s
            """, (response_message, appointment_id))
        conn.commit()
        return jsonify({"message": "Response sent to patient."}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        release_db_connection(conn)


@app.route('/get_room_status', methods=['GET'])
def get_room_status():
    if 'user_id' not in session:
        return jsonify({"message": "Please log in to view room status."}), 401

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT rooms.room_number, rooms.room_type, rooms.capacity
                FROM rooms
                JOIN beds ON rooms.id = beds.room_id
                WHERE beds.patient_id = %s
            """, (session['user_id'],))
            room = cur.fetchone()

            if room:
                # Assuming you have a way to determine the floor and directions
                floor = "2nd Floor" 
                directions = "Take the elevator to the 2nd floor, turn left."
                return jsonify({
                    "room_assigned": True,
                    "room_number": room[0],
                    "floor": floor,
                    "directions": directions
                })
            else:
                return jsonify({"room_assigned": False})
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return jsonify({"message": "Error fetching room status"}), 500
    finally:
        release_db_connection(conn)

@app.route('/get_remaining_patients', methods=['GET'])
def get_remaining_patients():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM patients WHERE id NOT IN (SELECT patient_id FROM beds WHERE status = 'occupied')")
            remaining_patients = cur.fetchall()
            return jsonify(remaining_patients), 200
    finally:
        release_db_connection(conn)

@app.route('/assign_room', methods=['POST'])
def assign_room():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({"message": "Unauthorized access."}), 403

    patient_id = request.json['patient_id']
    room_id = request.json['room_id']
    bed_number = request.json['bed_number']

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:

            # Update bed status
            cur.execute("""
                UPDATE beds
                SET status = 'occupied', patient_id = %s
                WHERE room_id = %s AND bed_number = %s
            """, (patient_id, room_id, bed_number))

        conn.commit()
        return jsonify({"message": "Room and bed assigned successfully"}), 200
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Database error: {e}")
        return jsonify({"message": "Error assigning room"}), 500
    finally:
        release_db_connection(conn)

@app.route('/get_bills', methods=['GET'])
def get_bills():
    if 'user_id' not in session:
        return jsonify({"message": "Please log in to view bills."}), 401

    user_id = session['user_id']

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, total_amount, status, created_at
                FROM bills
                WHERE patient_id = %s
                ORDER BY created_at DESC
            """, (user_id,))
            bills = cur.fetchall()
            return jsonify(bills), 200
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return jsonify({"message": "Error fetching bills"}), 500
    finally:
        release_db_connection(conn)

@app.route('/make_payment', methods=['POST'])
def make_payment():
    if 'user_id' not in session:
        return jsonify({"message": "Please log in to make a payment."}), 401

    bill_id = request.json['bill_id']
    amount = request.json['amount']
    payment_method = request.json['payment_method']

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO payments (bill_id, amount, payment_method)
                VALUES (%s, %s, %s)
            """, (bill_id, amount, payment_method))

            cur.execute("""
                UPDATE bills
                SET status = 'paid'
                WHERE id = %s
            """, (bill_id,))

        conn.commit()
        return jsonify({"message": "Payment successful"}), 200
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Database error: {e}")
        return jsonify({"message": "Error processing payment"}), 500
    finally:
        release_db_connection(conn)

@app.route('/send_bill/<int:user_id>/<string:user_type>', methods=['POST'])
def send_bill(user_id, user_type):
    if not session.get('is_admin'):
        flash('Access denied. Admins only.', 'error')
        return redirect(url_for('login'))

    amount = request.form['amount']
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Insert a new bill
            cur.execute("""
                INSERT INTO bills (patient_id, total_amount, status, created_at)
                VALUES (%s, %s, 'unpaid', NOW())
            """, (user_id, amount))
        conn.commit()
        flash('Bill sent successfully.', 'success')
    except psycopg2.Error as e:
        conn.rollback()
        flash('Error sending bill.', 'error')
    finally:
        release_db_connection(conn)
    return redirect(url_for('review_applications'))


@app.route('/get_rooms_and_beds', methods=['GET'])
def get_rooms_and_beds():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT r.id, r.room_number, r.room_type, r.capacity, r.status, 
                       b.bed_number, b.status AS bed_status, p.name AS patient_name,p.id as patient_id
                FROM rooms r
                LEFT JOIN beds b ON r.id = b.room_id
                LEFT JOIN patients p ON b.patient_id = p.id
                ORDER BY r.room_number, b.bed_number
            """)
            rooms_and_beds = cur.fetchall()
        return jsonify(rooms_and_beds), 200
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return jsonify({"message": "Error fetching room and bed data"}), 500
    finally:
        release_db_connection(conn)


if __name__ == '__main__':
    app.run(debug=True)
