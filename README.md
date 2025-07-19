# 🏥 Healthcare System – Django & React

A complete **Healthcare Management System** where **patients can book appointments with doctors**, and **admins can manage doctors, appointments, and generate reports**.

---

## 📌 **1. Project Overview**

This system includes:

✅ **User Roles:**
- **Patient** – Register, search doctors, book appointments.  
- **Doctor** – Manage own schedules, update profile.  
- **Admin** – Manage doctors, appointments, and generate monthly reports.

✅ **Key Features:**
- Doctor search by **specialization, location, and availability**.
- Appointment booking with **time validation** (business hours, no past bookings).
- **JWT authentication** for all users.
- **Celery background tasks** – sends appointment reminders 24 hours before.
- **Admin Panel APIs** for:
  - Viewing/updating doctors and appointments.
  - Monthly reports (total visits, appointments, and revenue per doctor).

✅ **Tech Stack:**
- **Backend:** Django, Django REST Framework, Celery, Redis
- **Frontend:** React, Bootstrap
- **Database:** PostgreSQL / SQLite (development)

---

## 📌 **2. Project Architecture**

```
healthcare-system-backend/
│── healthcare/                # Main Django project
│   ├── settings.py            # Django settings (Celery, JWT configured)
│   ├── celery.py              # Celery app configuration
│── users/                     # Handles User (Patient, Doctor, Admin)
│── appointments/              # Appointment & schedule management
│── admin_panel/               # Admin APIs & reports
│── templates/ (optional)      # For email templates
│── requirements.txt
│── manage.py
│
frontend-healthcare/           # React frontend
│── src/
│   ├── pages/
│   │   ├── Home.jsx           # Doctor listing + search
│   │   ├── DoctorDetails.jsx  # Booking page
│   ├── components/
│   │   ├── Layout.jsx
```

---

## 📌 **3. Setup Instructions**

### ✅ **Backend Setup**

1. **Clone & Install Dependencies**
   ```bash
   git clone <repo-url>
   cd healthcare-system-backend
   python3 -m vvenv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Environment Variables**  
   Create a `.env` file:
   ```
   SECRET_KEY=your-secret-key
   DEBUG=True
   DATABASE_URL=postgres://user:password@localhost:5432/healthcare
   ```

3. **Run Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Start Server**
   ```bash
   python manage.py runserver
   ```

5. **Celery & Redis (Background Tasks)**
   ```bash
   redis-server   # Start Redis
   celery -A healthcare worker -l info
   ```

---

### ✅ **Frontend Setup**

1. **Install & Run**
   ```bash
   cd frontend-healthcare
   npm install
   npm run dev
   ```

2. Access at: **http://localhost:5173**

---

## 📌 **4. API Documentation & Usage Examples**

### **🔹 Authentication**

**Register Patient**  
`POST /api/auth/register/`  
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "mobile_number": "+8801711223344",
  "password": "StrongPass@1",
  "role": "patient"
}
```

**Doctor Signup**  
`POST /api/auth/doctor-signup/`  
```json
{
  "full_name": "Dr. Smith",
  "email": "smith@hospital.com",
  "mobile_number": "+8801911223344",
  "password": "StrongPass@1",
  "license_number": "LIC12345",
  "experience_years": 10,
  "consultation_fee": 500,
  "specialization": "Cardiology",
  "location": "Dhaka",
  "available_timeslots": [
    { "date": "2025-07-25", "start_time": "10:00", "end_time": "13:00" }
  ]
}
```

---

### **🔹 Search Doctors**

`GET /api/users/doctors/?location=Dhaka&available=2025-07-19&specialization=Cardiology`

---

### **🔹 Book Appointment (Patient)**

`POST /api/appointments/`  
```json
{
  "doctor": 5,
  "schedule": 10,
  "appointment_time": "10:30",
  "notes": "General check-up"
}
```

---

### **🔹 Admin Reports**

`GET /api/admin-panel/reports/?month=07&year=2025`  
```json
{
  "monthly_report": [
    {
      "month": "July 2025",
      "doctor_id": 5,
      "doctor_name": "Dr. Abu 12",
      "total_patient_visits": 5,
      "total_appointments": 8,
      "total_earned": 4000
    }
  ]
}
```

---

## 📌 **5. Database Schema (Important Tables)**

### **User Table**
| Field          | Type          | Notes                             |
|----------------|--------------|------------------------------------|
| id            | Integer (PK)  |                                    |
| full_name     | CharField     |                                    |
| email         | EmailField    | Unique                             |
| mobile_number | CharField     | Unique, starts with `+88`          |
| role          | ChoiceField   | patient / doctor / admin           |

### **DoctorDetail Table**
| Field            | Type          |
|-------------------|--------------|
| license_number    | CharField    |
| experience_years  | Integer      |
| consultation_fee  | Integer      |
| specialization    | CharField    |
| location          | CharField    |

### **DoctorSchedule Table**
| Field       | Type      | Notes                  |
|-------------|----------|-------------------------|
| doctor      | FK (User)| Only doctors            |
| date        | DateField| Unique per doctor       |
| start_time  | TimeField| Business hours enforced |

### **AppointmentBooking Table**
| Field            | Type      |
|-------------------|----------|
| doctor           | FK (User)|
| patient          | FK (User)|
| schedule         | FK (Schedule)|
| appointment_time | TimeField|
| status           | ChoiceField (pending/completed)|

---

## 📌 **6. Challenges & Assumptions**

### ✅ **Challenges**
- Enforcing **unique schedules** per doctor.
- Handling **time zone issues** (`offset-aware` vs `naive` datetimes).
- **Celery reminder** scheduling using database tasks.

### ✅ **Assumptions**
- Doctors must **complete their profiles** (license, fee, specialization) to be available for booking.
- Appointment slots are fixed **30 minutes** apart.
- Admin is the only one allowed to deactivate users or doctors.

---
account details:
--------------------------healthcare system
admin---
01757427414
admin

------------------
role: patient
{
  "mobile_number": "01711223344",
  "password": "123456789"
}
{
  "full_name": "abu1",
  "mobile_number": "01711223345",
  "password": "123456789",
  "address": "Dhaka, Bangladesh"
}
---------
role: doctor
{
  "full_name": "Dr. abu",
  "mobile_number": "01711224345",
  "password": "123456789",
  "address": "Dhaka, Bangladesh",
  "role": "doctor"
}
{
  "full_name": "Dr. abu 1",
  "mobile_number": "01711225345",
  "password": "123456789",
  "address": "Dhaka, Bangladesh",
  "role": "doctor"
}
{
  "mobile_number": "01711225315",
  "password": "123456789"
}
{
    "id": 18,
    "full_name": "Dr. Sufian",
    "mobile_number": "01711234845",
    "role": "doctor",
    "address": "Dhaka, Bangladesh",
    "profile_image": null
}
{
    "id": 22,
    "full_name": "Dr. Rahman 3",
    "mobile_number": "+8801711223366",
    "role": "doctor",
    "address": "Dhaka, Bangladesh",
    "profile_image": null
}
{
    "mobile_number": "+8801711214344",
    "password": "Sani0175@",
}
{
    "mobile_number": "+8801721214344",
    "password": "Sani0175@",
    "email": "adu23@email.com",
}