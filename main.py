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
                cur.execute("SELECT * FROM patients WHERE name = %s", (patient_name,))
                user = cur.fetchone()
                
                if user and check_password_hash(user[4], password):  # Assuming password is at index 4
                    session['user_id'] = user[0]  # Store user ID in session
                    session['name']=user[1]
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

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, email, phone, gender, medical_record, profile_pic FROM patients WHERE id = %s", (session['user_id'],))
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
            cur.execute("SELECT password FROM patients WHERE id = %s", (session['user_id'],))
            stored_password = cur.fetchone()[0]

            if check_password_hash(stored_password, current_password):
                hashed_new_password = generate_password_hash(new_password)
                cur.execute("UPDATE patients SET password = %s WHERE id = %s", (hashed_new_password, session['user_id']))
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
                cur.execute("UPDATE patients SET profile_pic = %s WHERE id = %s", (psycopg2.Binary(file_data), session['user_id']))
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

    top_words = sorted(word_importance.items(), key=lambda x: x[1], reverse=True)[:10]
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
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_filename)
            resume.save(resume_path)

            resume_text = extract_text_from_pdf(resume_path)

            job_descriptions = {
                "ENT": "Seeking an experienced ENT specialist with skills in diagnosis and treatment of ear, nose, and throat disorders.",
                "Cardiology": "Looking for a cardiologist with expertise in heart disease diagnosis, ECG interpretation, and cardiac catheterization.",
            }

            job_description = job_descriptions.get(specialization, "Generic medical professional with relevant experience")

            similarity_score, top_words, missing_words = review_resume(resume_text, job_description)

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

@app.route('/admin/review_applications')
def review_applications():
    if not session.get('is_admin'):
        flash('Access denied. Admins only.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM doctor_applications ORDER BY similarity_score DESC")
            applications = cur.fetchall()
        return render_template('hr_review.html', applications=applications)
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        flash('Error retrieving applications', 'error')
        return redirect(url_for('dashboard'))
    finally:
        release_db_connection(conn)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({"message": "Please log in to update your profile."}), 401

    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    gender = request.form['gender']
    medical_record = request.form['medical_record']

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE patients 
                SET name = %s, email = %s, phone = %s, gender = %s, medical_record = %s 
                WHERE id = %s
            """, (name, email, phone, gender, medical_record, session['user_id']))
        conn.commit()
        return jsonify({"message": "Profile updated successfully"}), 200
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Database error: {e}")
        return jsonify({"message": "Profile update failed. Please try again."}), 500
    finally:
        release_db_connection(conn)

@app.route('/get_available_doctors', methods=['GET'])
def get_available_doctors():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, specialization FROM doctors WHERE is_active = TRUE")
            doctors = cur.fetchall()
        return jsonify(doctors), 200
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return jsonify({"message": "Error fetching doctors"}), 500
    finally:
        release_db_connection(conn)

@app.route('/get_available_slots', methods=['POST'])
def get_available_slots():
    doctor_id = request.json['doctor_id']
    date = request.json['date']
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT time_slot FROM appointments 
                WHERE doctor_id = %s AND appointment_date = %s
            """, (doctor_id, date))
            booked_slots = [row[0] for row in cur.fetchall()]
            
            all_slots = [f"{h:02d}:00" for h in range(9, 18)]  # 9 AM to 5 PM 
            available_slots = [slot for slot in all_slots if slot not in booked_slots]
            
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
            cur.execute("""
                INSERT INTO appointments (patient_id, doctor_id, appointment_date, time_slot)
                VALUES (%s, %s, %s, %s)
            """, (session['user_id'], doctor_id, date, time_slot))
        conn.commit()
        return jsonify({"message": "Appointment booked successfully"}), 200
    except psycopg2.Error as e:
        conn.rollback()
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
                SELECT a.id, d.name, d.specialization, a.appointment_date, a.time_slot
                FROM appointments a
                JOIN doctors d ON a.doctor_id = d.id
                WHERE a.patient_id = %s
                ORDER BY a.appointment_date, a.time_slot
            """, (session['user_id'],))
            appointments = cur.fetchall()
        return jsonify(appointments), 200
    except psycopg2.Error as e:
        print(f"Database error: {e}")
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
            job_description = f"Doctor specializing in {specialization} with {experience} years of experience"
            similarity_score, top_words, missing_words = review_resume(file_path, job_description)
            
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
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, email, specialization, experience, resume_path FROM doctor_applications WHERE status = 'pending'")
            applications = cur.fetchall()

        if request.method == 'POST':
            job_description = request.form['job_description']
            application_id = request.form['application_id']
            
            # Get the selected application
            selected_application = next((app for app in applications if app[0] == int(application_id)), None)
            if selected_application:
                resume_path = selected_application[5]
                similarity_score, top_words, missing_words = review_resume(resume_path, job_description)

                return render_template('hr_review.html', applications=applications, selected_application=selected_application, similarity_score=similarity_score, top_words=top_words, missing_words=missing_words)

        return render_template('hr_review.html', applications=applications)
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        flash('Error retrieving applications', 'error')
        return redirect(url_for('dashboard'))
    finally:
        release_db_connection(conn)

@app.route('/hr/approve/<int:app_id>', methods=['POST'])
def approve_application(app_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Get application details
            cur.execute("SELECT * FROM doctor_applications WHERE id = %s", (app_id,))
            application = cur.fetchone()
            
            if application:
                # Insert into doctors table
                cur.execute("""
                    INSERT INTO doctors (name, email, specialization,"Tr@310305")
                    VALUES (%s, %s, %s)
                """, (application[1], application[2], application[3]))
                
                # Update application status
                cur.execute("UPDATE doctor_applications SET status = 'accepted' WHERE id = %s", (app_id,))
                conn.commit()
                
                # Send approval email
                send_approval_email(application[2])
                
                flash('Application approved and doctor added to the system', 'success')
            else:
                flash('Application not found', 'error')
    except psycopg2.Error as e:
        conn.rollback()
        flash('Error processing application', 'error')
    finally:
        release_db_connection(conn)
    return redirect(url_for('hr_review'))

@app.route('/hr/reject/<int:app_id>', methods=['POST'])
def reject_application(app_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Check if the application exists
            cur.execute("SELECT email FROM doctor_applications WHERE id = %s", (app_id,))
            application = cur.fetchone()
            
            if application:
                # Update application status
                cur.execute("UPDATE doctor_applications SET status = 'rejected' WHERE id = %s", (app_id,))
                conn.commit()
                
                # Send rejection email
                send_rejection_email(application[0])  # Use the email from the fetched application
                
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
    # Implement doctor dashboard logic
    return render_template('doctor_dashboard.html')

# Add a route for patient-doctor communication
@app.route('/send_message', methods=['POST'])
def send_message():
    sender_id = request.form['sender_id']
    receiver_id = request.form['receiver_id']
    message = request.form['message']
    sender_type = request.form['sender_type']
    receiver_type = 'doctor' if sender_type == 'patient' else 'patient'
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO notifications (user_id, user_type, message)
        VALUES (%s, %s, %s)
    """, (receiver_id, receiver_type, message))
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({'status': 'success', 'message': 'Message sent'})

@app.route('/get_notifications')
def get_notifications():
    user_id = request.args.get('user_id')
    user_type = request.args.get('user_type')
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM notifications
        WHERE user_id = %s AND user_type = %s
        ORDER BY created_at DESC
    """, (user_id, user_type))
    notifications = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify({'notifications': notifications})

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'eshwanthkartitr@gmail.com'
app.config['MAIL_PASSWORD'] = 'Tr@310305'

mail = Mail(app)

def send_approval_email(email):
    msg = Message('Application Approved', sender='eshwanthkartitr@gmail.com', recipients=[email])
    msg.body = "Congratulations! Your application to join our medical team has been approved."
    mail.send(msg)

def send_rejection_email(email):
    msg = Message('Application Status Update', sender='eshwanthkartitr@gmail.com', recipients=[email])
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
    if not session.get('is_admin'):
        flash('Access denied. Admins only.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM doctors WHERE id = %s", (doctor_id,))
        conn.commit()
        flash('Doctor removed successfully.', 'success')
    except psycopg2.Error as e:
        conn.rollback()
        flash('Error removing doctor.', 'error')
    finally:
        release_db_connection(conn)
    return redirect(url_for('review_applications'))

@app.route('/admin/remove_patient/<int:patient_id>', methods=['POST'])
def remove_patient(patient_id):
    if not session.get('is_admin'):
        flash('Access denied. Admins only.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM patients WHERE id = %s", (patient_id,))
        conn.commit()
        flash('Patient removed successfully.', 'success')
    except psycopg2.Error as e:
        conn.rollback()
        flash('Error removing patient.', 'error')
    finally:
        release_db_connection(conn)
    return redirect(url_for('review_applications'))

if __name__ == '__main__':
    app.run(debug=True)