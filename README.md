
# Healthcare System API

## Project Overview and Architecture

This Healthcare System backend is a RESTful API built with **Django** and **Django REST Framework**. It supports core functionalities for managing doctors, patients, appointments, and schedules. The system enables:

- User roles: doctors, patients, and admins with role-based access control.
- Doctor profiles with detailed info like specialization, consultation fees, and availability schedules.
- Patients can book 30-minute appointment slots with doctors.
- Admin users manage all data and generate reports.
- Secure authentication via JWT tokens.

The project follows a modular app structure with clear separation of concerns:

- `users`: user accounts, roles, and profiles.
- `appointments`: booking, updating, and managing appointment data.
- `admin_panel`: administrative APIs for reports and management.
- `doctors`: doctor-specific data and scheduling.

---

## Setup Instructions

### Prerequisites

- Python 3.10+
- PostgreSQL (recommended) or SQLite for dev
- `pip` package manager

### Installation

1. Clone the repo:

```bash
git clone https://github.com/yourusername/healthcare-system.git
cd healthcare-system
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure your database in `settings.py`. Example for PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'healthcare_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

5. Run migrations:

```bash
python manage.py migrate
```

6. Create superuser for admin access:

```bash
python manage.py createsuperuser
```

7. Run the development server:

```bash
python manage.py runserver
```

---

## API Documentation and Usage Examples

### Authentication

- **Login:**  
  `POST /api/token/`  
  Body:  
  ```json
  {
    "mobile_number": "01712345678",
    "password": "yourpassword"
  }
  ```  
  Response: JWT access and refresh tokens.

- **Use JWT token** in Authorization header:  
  `Authorization: Bearer <access_token>`

---

### User Profile

- **Get profile:**  
  `GET /api/profile/`  
  Returns user details, including doctor schedules if role is doctor.

- **Update profile:**  
  `PUT /api/profile/`  
  Body contains fields to update, including nested doctor details and schedules for doctors.

---

### Doctors

- **List doctors:**  
  `GET /api/doctors/?specialization=cardiology&location=Dhaka&available=true`  
  Filters by specialization, location, and availability.

---

### Appointments

- **Book appointment:**  
  `POST /api/appointments/book/`  
  Body example:  
  ```json
  {
    "doctor": 15,
    "schedule": 4,
    "appointment_time": "11:00",
    "notes": "Please be on time"
  }
  ```

- **Update appointment status and notes:**  
  `PATCH /api/appointments/{id}/` (Admin only)

- **List booked appointments for user:**  
  `GET /api/profile/appointments/`

---

### Admin APIs

- **Manage doctors, patients, and appointments:** CRUD APIs with admin permissions.

- **Reports:**  
  `GET /api/admin-panel/reports/`  
  Returns total appointments per doctor, total revenue, and patient appointment details.

---

## Database Schema Explanation

- **User:** Custom user model with roles (`patient`, `doctor`, `admin`). Stores profile and authentication info.

- **DoctorDetail:** OneToOne with User for doctors. Stores license, specialization, experience, fees, and location.

- **DoctorSchedule:** ForeignKey to User (doctor), with date and start/end times defining availability slots.

- **AppointmentBooking:** Links patient, doctor, schedule, and appointment time. Enforces unique booking per slot. Status tracks appointment progress.

- **AdminPanel:** (if separate) for admin-specific data or audit trails.

---

## Challenges Faced or Assumptions Made

- **Challenge:** Handling nested serialization and updates for complex doctor schedules and details required careful override of serializer `update` methods.

- **Assumption:** Appointment slots are fixed 30-minute intervals within doctor schedules.

- **Challenge:** Preventing double booking with unique constraints plus validation logic.

- **Assumption:** Patients can only book appointments for future dates; no past bookings allowed.

- **Challenge:** Role-based access control was essential to secure endpoints properly.

- **Assumption:** Admin users manage all data and can override any appointments or user data.

---

If you need more detailed docs or Postman collections, I can help prepare those too!

---

Would you like me to generate the **requirements.txt** or example `.env` config next?
