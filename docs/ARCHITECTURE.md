# System architecture — VUNA Cisco NetAcad 2.0

```mermaid
flowchart TB
  subgraph Clients[Presentation clients]
    Admin[Management and Academy Admin Portal]
    Faculty[Faculty and Department Portal]
    Instructor[Instructor Portal]
    Student[Student Self-Service Portal]
    Auditor[Auditor Read-only Portal]
  end
  subgraph API[Application layer — Django REST Framework]
    Auth[Identity, JWT and RBAC]
    Registry[Student Registry and Academics]
    Training[Training Catalogue and Enrolment]
    Delivery[Timetable, Attendance and Assessment]
    Finance[Finance and Certification]
    Services[Notifications, Helpdesk and Assets]
    Insights[Analytics and Reporting]
    Audit[Audit and Administration]
  end
  subgraph Data[Data and asynchronous processing]
    PG[(PostgreSQL)]
    Redis[(Redis)]
    Celery[Celery Workers]
    Files[(Private Object Storage)]
  end
  subgraph External[Approved integrations]
    SIS[University SIS Adapter]
    Cisco[Cisco Learning Platform Adapter]
    Paystack[Paystack]
    Mail[Email and SMS Provider]
  end
  Clients --> Auth
  Clients --> Registry
  Clients --> Training
  Clients --> Delivery
  Clients --> Insights
  API --> PG
  API --> Files
  API --> Redis
  Redis --> Celery
  Celery --> PG
  API -. approved APIs .-> SIS
  API -. approved APIs .-> Cisco
  API -. signed webhooks .-> Paystack
  Celery --> Mail
  API --> Audit
```

The architecture is a modular monolith, not a microservice estate. Each domain module owns its business rules and data boundaries while sharing a single PostgreSQL deployment. External integrations are adapters and remain disabled until the institution authorises access and supplies supported interfaces.
