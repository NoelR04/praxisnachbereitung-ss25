# Domänenmodell „Inventar“


## Mermaid ERD

```mermaid
erDiagram
    EMPLOYEE ||--o{ ASSIGNMENT : receives
    DEVICE ||--o{ ASSIGNMENT : is_assigned_in
    LOCATION ||--o{ DEVICE : stores
    LOCATION ||--o{ EMPLOYEE : works_at

    EMPLOYEE {
        int employee_id PK
        string personnel_number UK
        string full_name
        string department
        int location_id FK
    }

    DEVICE {
        int device_id PK
        string device_type
        string model
        date purchase_date
        decimal net_purchase_price
        int location_id FK
        boolean in_use
    }

    LOCATION {
        int location_id PK
        string name UK
    }

    ASSIGNMENT {
        int assignment_id PK
        int employee_id FK
        int device_id FK
        date assigned_from
        date assigned_until
    }
```
### Fachregeln

**R1**  
Ein Gerät darf zu einem Zeitpunkt maximal eine aktive Zuweisung haben.

**R2**  
Eine Zuweisung ist aktiv, wenn `assigned_until` leer ist.

**R3**  
Zuweisungen für dasselbe Gerät dürfen sich zeitlich nicht überschneiden.

**R4**  
Das Enddatum (`assigned_until`) darf nicht vor dem Startdatum (`assigned_from`) liegen.

**R5**  
Der Netto-Kaufpreis eines Geräts darf nicht negativ sein.

**R6**  
Ein Gerät kann nur ausgeliehen werden, wenn es nicht bereits aktiv in Benutzung ist (`in_use = false`).

**R7**  
Nach Rückgabe eines Geräts (wenn `assigned_until` gesetzt wird), muss der Status `in_use` wieder auf `false` gesetzt werden.