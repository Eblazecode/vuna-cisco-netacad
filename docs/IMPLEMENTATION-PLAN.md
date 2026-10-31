# VUNA Cisco NetAcad 2.0 — Implementation plan

## Requirements baseline

This plan is derived from the uploaded SRS v1.0. The product covers all registered Veritas University students and the professional training academy. It does not replace the University's SIS or Cisco's learning platform.

## Delivery increments

| Increment | Scope | Principal SRS mapping | Exit criteria |
|---|---|---|---|
| 0 — Engineering foundation | Repo, Django config, PostgreSQL, CI, API docs, audit baseline | Architecture, FR-01, FR-18 | Clean checks, repeatable setup, migrations and CI green |
| 1 — Identity and student registry | 11 roles, authentication, scoped permissions, self/admin registration, student profile, CSV import/export, approvals | FR-01–04 | Role tests, duplicate prevention, approval workflow, faculty/department data integrity |
| 2 — Academy catalogue and enrolment | Training programmes, course catalogue, instructor assignment, prerequisites, capacity, enrolment approval/withdrawal | FR-05–06 | Student records remain separate from course enrolment; capacity and state transitions tested |
| 3 — Delivery and assessment | Timetables, class sessions, attendance, QR attendance, assessments, submissions, results approval/publication | FR-07, FR-08, FR-11 | Only authorised instructors can manage assigned classes; unpublished results remain private |
| 4 — Finance and certification | Fee plans, invoices, payment verification, signed webhooks, receipts, refunds, certificates | FR-09–10 | Reconciliation tests; idempotent webhooks; no client-side payment trust |
| 5 — Dashboards and reporting | Management/academy/student dashboards, filters, CSV/PDF exports, finance reconciliation metrics | FR-13–14 | Every KPI is sourced from filtered verified records; role and scope restrictions tested |
| 6 — Student services and operations | Notifications, support tickets, assets/labs, alumni/career tracking | FR-12, FR-15–17 | End-to-end workflows and service-level audit events |
| 7 — Integration and hardening | Approved SIS/Cisco adapters, MFA, monitoring, load/security tests, backup/recovery, UAT | FR-01, FR-18, NFRs | Security sign-off, recovery drill, performance tests, institutional UAT acceptance |

## Role baseline (11 SRS categories)

`SUPER_ADMIN`, `UNIVERSITY_MANAGEMENT`, `ACADEMY_DIRECTOR`, `ACADEMY_COORDINATOR`, `FACULTY_ADMIN`, `DEPARTMENT_ADMIN`, `FINANCE_OFFICER`, `INSTRUCTOR`, `LAB_OFFICER`, `STUDENT`, `AUDITOR`.

Role membership is not sufficient on its own for faculty/department access. Every scoped query must additionally constrain the user's assigned faculty or department. Auditors are read-only. Finance users must not receive unrestricted access to student academic data; instructors must be restricted to assigned classes; students must only access their own records.

## Planned domain modules

- `accounts`: users, roles, permissions, staff scope, MFA, authentication events.
- `academics`: faculties, departments, programmes of study, academic sessions and levels.
- `students`: profiles, status history, documents, import/export, identity lifecycle.
- `training`: professional programmes, courses, instructors, cohorts, enrolments.
- `delivery`: timetable, class schedules, attendance sessions/records, assessments, submissions, results.
- `finance`: fee plans, invoices, payments, receipts, refunds, reconciliation.
- `certifications`: certificate issue, verification and expiry/revocation tracking.
- `communications`: notifications, templates and delivery logs.
- `operations`: laboratories, assets, reservations, support tickets.
- `insights`: role-specific dashboard aggregates and report exports.
- `audit`: append-only business/security audit events and export trails.
- `integrations`: Paystack, email/SMS, approved SIS connector, Cisco adapter.

## Non-functional acceptance gates from the SRS

- Performance targets: page response under 3 seconds, dashboards under 5 seconds, API response under 1 second under agreed test conditions; support 500 concurrent users; 99.5% monthly availability target.
- Daily backup and a demonstrated restore/recovery test.
- HTTPS, secure password hashing, CSRF protection where cookie sessions are used, input validation, rate limits, safe upload handling, signed webhook verification, restricted exports, tamper-evident audit strategy.
- Nigerian Data Protection Act 2023 compliance review, privacy notices, lawful-purpose assessment, data minimisation, retention and access controls.

## Release gates / unresolved institutional inputs

The SRS does not supply authoritative faculty/department/programme records, academic session data, approved fee schedule, Cisco catalogue mappings, official SIS API credentials, SMTP/SMS credentials, Paystack production credentials, retention schedule, or designated data-protection contacts. These must be supplied/approved by Veritas University before production configuration. Never seed invented institutional records or operational metrics.
