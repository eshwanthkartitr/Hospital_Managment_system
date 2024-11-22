# Easy Healthcare Management System (EHMS)

A comprehensive healthcare management system built with Flask, providing secure and efficient healthcare management solutions for patients, doctors, and administrators.

## 🌟 Overview
EHMS is a web-based platform that streamlines healthcare operations, enhances patient care, and improves administrative efficiency through digital transformation of healthcare services.The integration with https://hmsv2.netlify.app allows for seamless onboarding and interaction for all users.

## 🚀 Features

### For Patients
- User registration and authentication
- Book appointments with doctors
- View medical records
- Real-time chat with doctors
- View room assignments and directions
- Manage bills and payments
- Update profile and profile picture

### For Doctors
- Application submission system
- Appointment management
- Patient communication
- Medical record access
- Response system for appointment requests
- Profile management

### For Administrators
- Review doctor applications
- Manage users (doctors and patients)
- Room and bed assignment
- Billing management
- System monitoring

## 🛠️ Technical Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **Session Management**: Redis
- **Natural Language Processing**: spaCy
- **Document Processing**: PyPDF2
- **Email Service**: Flask

## ⚙️ Configuration

### Database Configuration
```python
db_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dbname="ehms",
    user="postgres",
    password="your_password",
    host="localhost",
    port="5432"
)
```

### Redis Configuration
```python
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')
```

### Email Configuration
```python
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_app_password'
```

## 🚀 Installation

1. Clone the repository
```bash
git clone [repository-url]
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Install spaCy English language model
```bash
python -m spacy download en_core_web_sm
```

4. Start the application
```bash
python main.py
```

## 🔒 Security Features
- Password hashing with Werkzeug
- Session management with Redis
- Role-based access control
- Input validation and sanitization

## 📁 Project Structure
```
.
├── main.py
├── README.md
```

## 📧 Contact
For support or queries, please contact [eshwanthkartik@gmail.com]

## 📝 License
This project is licensed under the MIT License - see the LICENSE file for details.
