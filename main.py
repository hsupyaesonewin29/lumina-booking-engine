from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Database Setup
DATABASE_URL = "sqlite:///./lumina_booking.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)
    dob = Column(String, nullable=False)
    is_member = Column(Boolean, default=False)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    practitioner_id = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String, default="confirmed")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lumina Clinics Booking Engine API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class BookingCreate(BaseModel):
    full_name: str
    email: EmailStr  
    phone: str
    dob: str
    is_member: bool
    practitioner_id: int
    start_time: str
    duration_minutes: int

@app.post("/bookings")
def create_booking(payload: BookingCreate, db: Session = Depends(get_db)):
    # Rule 1: Senior Facialist Check
    if payload.practitioner_id == 1 and not payload.is_member:
        raise HTTPException(
            status_code=400, 
            detail="Senior Facialist is strictly reserved for Members."
        )
    
    # string ကို datetime object အဖြစ် ပြောင်းခြင်း
    start = datetime.fromisoformat(payload.start_time)
    service_end = start + timedelta(minutes=payload.duration_minutes)
    buffered_end = service_end + timedelta(minutes=15)
    
    # Rule 2: 15-Minute Cleanup Buffer Check
    existing_bookings = db.query(Booking).filter(
        Booking.practitioner_id == payload.practitioner_id,
        Booking.status == "confirmed"
    ).all()
    
    for b in existing_bookings:
        b_buffered_end = b.end_time + timedelta(minutes=15)
        if start < b_buffered_end and buffered_end > b.start_time:
            raise HTTPException(
                status_code=400, 
                detail="Time slot unavailable (15-min cleanup buffer conflict)."
            )
            
    client = db.query(Client).filter(Client.email == payload.email).first()
    if not client:
        client = Client(
            full_name=payload.full_name,
            email=payload.email,
            phone=payload.phone,
            dob=payload.dob,
            is_member=payload.is_member
        )
        db.add(client)
        db.commit()
        db.refresh(client)
        
    booking = Booking(
        client_id=client.id,
        practitioner_id=payload.practitioner_id,
        start_time=start,
        end_time=service_end,
        status="confirmed"
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    
    return {
        "message": "Booking successful", 
        "booking_id": booking.id,
        "client_id": client.id
    }

@app.get("/bookings")
def get_all_bookings(db: Session = Depends(get_db)):
    bookings = db.query(Booking).all()
    return bookings