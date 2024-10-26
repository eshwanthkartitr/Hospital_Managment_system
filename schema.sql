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

CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    room_number VARCHAR(10) NOT NULL,
    room_type VARCHAR(50) NOT NULL,
    capacity INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'available'
);

CREATE TABLE IF NOT EXISTS beds (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES rooms(id),
    bed_number VARCHAR(10) NOT NULL,
    status VARCHAR(20) DEFAULT 'available'
);

-- Billing and Payments
CREATE TABLE IF NOT EXISTS bills (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id),
    appointment_id INTEGER REFERENCES appointments(id),
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'unpaid',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    bill_id INTEGER REFERENCES bills(id),
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(20),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inventory Management
CREATE TABLE IF NOT EXISTS inventory (
    id SERIAL PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL,
    threshold INTEGER NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);