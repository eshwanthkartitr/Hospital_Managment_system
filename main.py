from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from psycopg2 import pool
import spacy
import PyPDF2
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a real secret key
app.config['UPLOAD_FOLDER'] = 'uploads'  # Ensure this folder exists

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
                print(check_password_hash(user[2], password))
                
                if user and check_password_hash(user[2], password):  # Assuming password is at index 3
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
    
    return "Dashboard - To be implemented"

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
                # Add more specializations as needed
            }

            job_description = job_descriptions.get(specialization, "Generic medical professional with relevant experience")

            similarity_score, top_words, missing_words = review_resume(resume_text, job_description)

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

if __name__ == '__main__':
    app.run(debug=True)
