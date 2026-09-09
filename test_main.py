import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from main import app, get_db, Base

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# 1. Senior Facialist Non-Member Reject Test
def test_senior_facialist_non_member_rejected():
    payload = {
        "full_name": "John Doe",
        "email": "john@example.com",
        "phone": "0812345678",
        "dob": "1990-01-01",
        "is_member": False,
        "practitioner_id": 1,
        "start_time": "2026-10-01T10:00:00",
        "duration_minutes": 60
    }
    response = client.post("/bookings", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Senior Facialist is strictly reserved for Members."

# 2. Senior Facialist Member Allowed Test
def test_senior_facialist_member_allowed():
    payload = {
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "0812345678",
        "dob": "1992-05-10",
        "is_member": True,
        "practitioner_id": 1,
        "start_time": "2026-10-01T10:00:00",
        "duration_minutes": 60
    }
    response = client.post("/bookings", json=payload)
    assert response.status_code == 200
    assert response.json()["message"] == "Booking successful"

# 3. Non-Member with Regular Practitioner Success Test
def test_regular_practitioner_non_member_allowed():
    payload = {
        "full_name": "Alice Smith",
        "email": "alice@example.com",
        "phone": "0833333333",
        "dob": "1996-08-12",
        "is_member": False,
        "practitioner_id": 2, # Regular practitioner
        "start_time": "2026-10-01T10:00:00",
        "duration_minutes": 60
    }
    response = client.post("/bookings", json=payload)
    assert response.status_code == 200
    assert response.json()["message"] == "Booking successful"

# 4. Cleanup Buffer Conflict Test (Within 15 mins)
def test_cleanup_buffer_conflict():
    booking1 = {
        "full_name": "Client One",
        "email": "client1@example.com",
        "phone": "0811111111",
        "dob": "1995-03-15",
        "is_member": True,
        "practitioner_id": 2,
        "start_time": "2026-10-01T10:00:00",
        "duration_minutes": 60
    }
    client.post("/bookings", json=booking1)

    # 10:00 - 11:00 booking + 15 min buffer = 11:15 မှ ရမည်။
    # 11:10 မှာ လာတင်ရင် Conflict ဖြစ်ရမည်။
    booking2 = {
        "full_name": "Client Two",
        "email": "client2@example.com",
        "phone": "0822222222",
        "dob": "1998-07-20",
        "is_member": False,
        "practitioner_id": 2,
        "start_time": "2026-10-01T11:10:00",
        "duration_minutes": 60
    }
    response = client.post("/bookings", json=booking2)
    assert response.status_code == 400
    assert response.json()["detail"] == "Time slot unavailable (15-min cleanup buffer conflict)."

# 5. Booking Success After Buffer Time (At/After 15 mins)
def test_booking_allowed_after_buffer():
    booking1 = {
        "full_name": "Client One",
        "email": "client1@example.com",
        "phone": "0811111111",
        "dob": "1995-03-15",
        "is_member": True,
        "practitioner_id": 2,
        "start_time": "2026-10-01T10:00:00",
        "duration_minutes": 60
    }
    client.post("/bookings", json=booking1)

    # 10:00 - 11:00 + 15 mins buffer = 11:15 တွင် အသစ်တင်လျှင် အဆင်ပြေရမည်။
    booking2 = {
        "full_name": "Client Three",
        "email": "client3@example.com",
        "phone": "0833333333",
        "dob": "1997-04-10",
        "is_member": False,
        "practitioner_id": 2,
        "start_time": "2026-10-01T11:15:00",
        "duration_minutes": 60
    }
    response = client.post("/bookings", json=booking2)
    assert response.status_code == 200
    assert response.json()["message"] == "Booking successful"

# 6. Overlap Booking Test (Same exact start time)
def test_exact_overlap_rejected():
    booking1 = {
        "full_name": "Client A",
        "email": "clienta@example.com",
        "phone": "0811111111",
        "dob": "1995-03-15",
        "is_member": True,
        "practitioner_id": 2,
        "start_time": "2026-10-01T14:00:00",
        "duration_minutes": 60
    }
    client.post("/bookings", json=booking1)

    # အချိန် အတိအကျ ထပ်တူ တင်မည်
    booking2 = {
        "full_name": "Client B",
        "email": "clientb@example.com",
        "phone": "0822222222",
        "dob": "1998-07-20",
        "is_member": True,
        "practitioner_id": 2,
        "start_time": "2026-10-01T14:00:00",
        "duration_minutes": 60
    }
    response = client.post("/bookings", json=booking2)
    assert response.status_code == 400

# 7. Invalid Email Format Test
def test_invalid_email_format():
    payload = {
        "full_name": "Bad Email",
        "email": "not-an-email",
        "phone": "0812345678",
        "dob": "1990-01-01",
        "is_member": True,
        "practitioner_id": 2,
        "start_time": "2026-10-01T16:00:00",
        "duration_minutes": 60
    }
    response = client.post("/bookings", json=payload)
    assert response.status_code == 422 # Pydantic Validation Error