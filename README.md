# Lumina Clinics Booking Engine API

A robust FastAPI backend service for handling clinic bookings, enforcing business rules, and managing cleanup buffer times.

## Features
- **Senior Facialist Restriction**: Senior Facialists (Practitioner ID: 1) are strictly reserved for members.
- **15-Minute Cleanup Buffer**: Automatically enforces a 15-minute post-appointment buffer between bookings.
- **Data Validation**: Email validation using Pydantic.
- **Automated Testing**: Comprehensive test coverage with Pytest (7 test scenarios).

## Setup & Run Instructions

1. **Activate Virtual Environment**:
   ```cmd
   venv\Scripts\activate
   