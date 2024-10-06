CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    password VARCHAR(255) NOT NULL,
    gender VARCHAR(20) NOT NULL,
    medical_record TEXT,
    profile_pic BYTEA
);

-- Create doctor_applications table
CREATE TABLE IF NOT EXISTS doctor_applications (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    experience INTEGER NOT NULL,
    resume_path VARCHAR(255) NOT NULL,
    similarity_score FLOAT,
    status VARCHAR(20) DEFAULT 'pending'
);

CREATE TABLE doctors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    specialty VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255)
);

CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER REFERENCES doctors(id),
    patient_name VARCHAR(100),
    appointment_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending'
);

CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    specialty VARCHAR(100),
    resume_path VARCHAR(255)
);

-- Modify appointments table to include more details
ALTER TABLE appointments 
ADD COLUMN IF NOT EXISTS patient_id INTEGER REFERENCES patients(id),
ADD COLUMN IF NOT EXISTS time_slot TIME,
ADD COLUMN IF NOT EXISTS specialty VARCHAR(100),
ADD COLUMN IF NOT EXISTS reason TEXT,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Create chat_rooms table for doctor-patient communication
CREATE TABLE IF NOT EXISTS chat_rooms (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER REFERENCES doctors(id),
    patient_id INTEGER REFERENCES patients(id),
    appointment_id INTEGER REFERENCES appointments(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(doctor_id, patient_id, appointment_id)
);

-- Create messages table for storing chat history
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    chat_room_id INTEGER REFERENCES chat_rooms(id),
    sender_type VARCHAR(10) CHECK (sender_type IN ('doctor', 'patient')),
    sender_id INTEGER,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE
);

-- Add notifications table for appointment updates
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    user_type VARCHAR(10) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE
);

-- Sample queries for patients table
-- Insert a new patient
INSERT INTO patients (name, email, phone, password, gender, medical_record)
VALUES ($1, $2, $3, $4, $5, $6);

-- Update patient's profile picture
UPDATE patients SET profile_pic = $1 WHERE id = $2;

-- Get patient information
SELECT * FROM patients WHERE id = $1;

-- Sample queries for doctor_applications table
-- Insert a new doctor application
INSERT INTO doctor_applications (name, email, specialization, experience, resume_path, similarity_score)
VALUES ($1, $2, $3, $4, $5, $6);

-- Get all doctor applications ordered by similarity score
SELECT * FROM doctor_applications ORDER BY similarity_score DESC;