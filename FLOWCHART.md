# Lumina Clinics - Booking Process Flowchart

Below is the standard user booking journey from accessing the website to appointment confirmation.

```mermaid
flowchart TD
    A[Start: Client visits Lumina Website] --> B[Select Branch & Treatment]
    B --> C[Select Date & Time Slot]
    C --> D{Is Senior Facialist Selected?}
    
    D -- Yes --> E{Is Client a Member?}
    E -- No --> F[Reject: Senior Facialist is Member-Only]
    E -- Yes --> G[Check 15-min Room Buffer]
    D -- No --> G
    
    G --> H{Room / Buffer Conflict?}
    H -- Yes --> I[Prompt: Slot Unavailable, Choose Another Time]
    H -- No --> J[Capture ID Number & DOB for Laser Consent]
    
    J --> K{Is Client a Member?}
    K -- Yes --> L[Waive Deposit - Instant Booking Confirmation]
    K -- No --> M[Generate Idempotent $300 WhatsApp Deposit Link]
    
    M --> N[Client Completes Deposit Payment]
    N --> O[Booking Status: Confirmed]
    L --> O
    O --> P[End: Send Confirmation SMS / WhatsApp]