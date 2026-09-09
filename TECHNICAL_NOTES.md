# Technical Notes: Lumina Clinics Booking Engine

This document details the system architecture, data models, and business logic enforcement for developers maintaining or extending the Lumina Clinics Booking Engine.

---

## 1. System Architecture & Tech Stack

- **Framework**: FastAPI (Python 3.13)
- **Database**: SQLite with SQLAlchemy ORM (ACID compliant)
- **Validation Engine**: Pydantic v2 (EmailStr, Datetime parsing)
- **Test Suite**: Pytest (Automated unit & integration tests)

---

## 2. Database Schema Design (Data Model)

### Entity: `Client`
- `id` (Integer, Primary Key)
- `name` (String, Required)
- `email` (String, Unique, Indexed)
- `phone` (String, Required)
- `id_number` (String, Required - Laser Consent Compliance)
- `dob` (String, Required - Format: YYYY-MM-DD)
- `is_member` (Boolean, Default: False)

### Entity: `Practitioner`
- `id` (Integer, Primary Key)
- `name` (String, Required)
- `is_senior` (Boolean, Default: False)

### Entity: `Booking`
- `id` (Integer, Primary Key)
- `client_id` (Integer, ForeignKey -> client.id)
- `practitioner_id` (Integer, ForeignKey -> practitioner.id)
- `start_time` (DateTime, ISO Format)
- `end_time` (DateTime, ISO Format - Includes treatment duration)
- `status` (String - `confirmed`, `cancelled`)

---

## 3. Business Logic & Rule Enforcement Matrix

| Rule Description | Enforced In File | Line / Function | Enforcement Logic |
| :--- | :--- | :--- | :--- |
| **Member-Only Senior Facialist** | `main.py` | `create_booking` | Validates if `practitioner_id == 1`. If `client.is_member` is `False`, raises HTTP 400. |
| **15-Min Room Cleanup Buffer** | `main.py` | `create_booking` | Checks existing bookings. Unless therapist is Senior, checks if `new_start < existing_end + 15 mins`. Raises HTTP 400 on conflict. |
| **Laser Consent Data Capture** | `main.py` | `BookingCreate` Schema | Enforces `id_number` and `dob` payload validation. |
| **Deposit Waiver Logic** | `main.py` | Response Payload | Calculates `deposit_required = 0` if `is_member == True`, else `$300`. |