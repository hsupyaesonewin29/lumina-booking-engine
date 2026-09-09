# Proposal: Lumina Clinics Online Booking Engine (Phase 1)

**Prepared for:** Founder & Executive Team, Lumina Clinics  
**Delivery Timeline:** 6 Weeks  

---

## 1. Executive Summary & Vision
Lumina Clinics has built an exceptional reputation across its 6 branches through personalized aesthetics care and strong client relationships. As business grows, relying solely on paper diaries and manual phone/WhatsApp bookings creates operational friction—leading to double-bookings, missed deposit collections, and receptionist overload.

This proposal outlines a **modern, streamlined Online Booking Engine** designed specifically for Lumina Clinics. The system automates routine appointment scheduling, secures deposit payments, eliminates double-booking errors, and seamlessly integrates with your existing front-desk workflows without replacing your valued reception team.

---

## 2. Key Challenges & Proposed Solutions

### Challenge 1: Double-Booking Risks (e.g., Christmas Laser Overbooking)
* **The Problem:** Simultaneous bookings via phone/WhatsApp leading to client conflict.
* **Our Solution:** Atomic database transactions and real-time room/therapist availability locks. Once a slot is selected, it is temporarily held until confirmed, guaranteeing zero double-bookings.

### Challenge 2: Deposit Collection & Page Hang Double-Payments
* **The Problem:** Clients experience page timeouts and accidentally pay deposit links twice via WhatsApp.
* **Our Solution:** Unique idempotent payment link generation. If a page hangs or a client clicks twice, the system verifies the transaction status and prevents duplicate charges.

### Challenge 3: Legacy Shared Hosting Limitations ("No Background Jobs")
* **The Problem:** Current shared hosting cannot execute scheduled background tasks.
* **Our Solution:** Event-driven architecture with lazy-evaluation algorithms. Appointment cleanup buffers (15-minute post-treatment) and membership checks are calculated instantly on HTTP request evaluation rather than relying on background cron jobs.

### Challenge 4: Staff Apprehension (Receptionists)
* **The Problem:** Receptionists fear the automated system will replace their jobs.
* **Our Solution:** The booking engine acts as an **assistant, not a replacement**. It handles after-hours booking traffic and standard slots, freeing receptionists to focus on premium in-clinic client hospitality and complex patient consultations.

---

## 3. Core Business Rules Enforced

1. **Flexible Treatment Durations**: Supports 30, 60, and 90-minute treatment slots aligned to half-hour/on-the-hour schedules.
2. **Mandatory Room Cleanup Buffer**: Enforces a 15-minute room cleaning and sterilization buffer after every appointment.
3. **Senior Facialist Exemption**: Senior therapists (Practitioner ID: 1) are exempted from the 15-minute break restriction to allow back-to-back prep, while being exclusively reserved for registered members.
4. **Deposit & Membership Rules**: $300 deposit requirement automatically waived for verified members.
5. **Medical Compliance**: Secure capture of Client ID and Date of Birth required for laser consent safety.

---

## 4. 6-Week Implementation Roadmap

* **Weeks 1–2 (Core Engine & Schema)**: Database architecture, availability calculation algorithms, and room locking logic.
* **Weeks 3–4 (Deposit & Integration)**: WhatsApp payment link integration, idempotency checks, and member privilege engine.
* **Week 5 (Receptionist Dashboard & Testing)**: Internal view for receptionists to manage bookings and view diary status.
* **Week 6 (UAT & Go-Live)**: Branch staff training, dry runs, and official public launch.