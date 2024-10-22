# GuideAndSeek  
**Cause Google doesn’t have all the answers**

# Deployed Demo:
https://guideandseek.onrender.com/

## Project Overview
**GuideAndSeek** is an education platform connecting students with teachers for personalized learning sessions.

## Features
- **Profile Creation:** Separate profiles for both teachers and students.
- **Teacher Availability Scheduling:** Teachers can schedule and update their availability.
- **Appointment Request System:** Students can request appointments based on teacher availability.
- **Teacher Search and Sorting:** Search and filter teachers by subject, level, and country.
- **Feedback System:** Students leave reviews for teachers after lessons.


## Project Architecture
The project follows a typical client-server architecture with the following layers:

### 1. **Frontend**
- **Technologies Used:** HTML, CSS (Tailwind), JavaScript.
- **Description:** The frontend consists of responsive web pages for profile management, appointment requests, and teacher search, styled with Tailwind CSS for modern and clean UI design.

### 2. **Backend**
- **Technologies Used:** Python (Flask).
- **Description:** The backend manages user authentication, teacher availability, appointment requests, and handles the database connection.

### 3. **Database**
- **Database Used:** PostgreSQL.
- **Description:** For reletional data manage.

### 4. **APIs**
- **Description:** The backend provides APIs for user authentication, routing, and processing appointment requests.

### 5. **Third-Party Services**
- **Mailjet:** Used for email verification during registration.
- **Google Meet API (Planned):** To automate meeting link generation for sessions.

### 6. **Hosting**
- **Hosting Provider:** Render.
- **Description:** The entire application is hosted on Render, ensuring easy deployment and scalability.


## Technologies Used
- **Frontend:** HTML, Tailwind CSS, JavaScript.
- **Backend:** Python (Flask).
- **Database:** PostgreSQL.
- **APIs:** Custom-built APIs for authentication and appointment handling.
- **Third-party Services:** Mailjet for email verification.
- **Hosting:** Render.


## Setup Instructions

### Prerequisites
- Python 3.x
- PostgreSQL
- Mailjet API Key (for email verification)
- Flask and required dependencies (specified in `requirements.txt`)

### Step-by-Step Guide

1. **Clone the Repository**
   ```bash
   git clone https://github.com/hiba-emording/GuideAndSeek.git
   cd GuideAndSeek
   ```

2. **Set Up Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up PostgreSQL Database**
   - Create a PostgreSQL database.
   - Update the `config.py` file with your database credentials.
   ```python
   SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/your_db_name'
   ```

5. **Set Up Mailjet API**
   - Sign up for Mailjet and generate API keys.
   - Add your Mailjet credentials in the environment variables or in the `config.py` file:
   ```python
   MAILJET_API_KEY = 'your_api_key'
   MAILJET_API_SECRET = 'your_api_secret'
   ```

6. **Database Migration**
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

7. **Run the Application**
   ```bash
   flask run
   ```

8. **Access the App**
   - Go to `http://127.0.0.1:5000/` to access GuideAndSeek.


## Usage Guidelines

1. **Teacher Registration**
   - Teachers can create profiles and specify their availability.
   
2. **Student Registration**
   - Students can search for teachers using filters and request appointments.
   
3. **Requesting an Appointment**
   - A student can request an appointment based on a teacher’s available time slots.
   
4. **Accepting an Appointment**
   - Teachers can accept or decline appointment requests.
   
5. **Feedback and Reviews**
   - After each session, students can leave reviews which will be displayed on the teacher’s profile.


## Areas for Improvement
- **Notifications:** Implement real-time notifications for appointment confirmations.
- **Google Meet API Integration:** Automate the generation of Google Meet links through the Google Cloud API.
- **Cancellation Feature:** Add a feature for appointment cancellations and rescheduling.
- **UI/UX Enhancements:** Improve the user interface for a smoother and more intuitive experience.

