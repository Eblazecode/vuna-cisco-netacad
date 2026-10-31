# Initial data model

## Implemented in this foundation

- `User`: UUID identity, unique email login, one SRS role, account security flags and faculty/department scope assignment.
- `Faculty` → `Department` → `AcademicProgramme`.
- `AcademicSession` with explicit current/open-registration flags.
- `Student`: unique matriculation number, academic associations, contact details, status, optional user identity and verification metadata.
- `StudentStatusHistory`: append-only status transitions.
- `StudentDocument`: protected student file metadata and verification state.
- `AuditLog`: append-only event record with actor, action, target, metadata and request context fields.

## Integrity constraints

- Matriculation number is unique.
- Department must belong to the selected faculty.
- Programme must belong to the selected department.
- Status changes are recorded with actor, prior status, new status, reason and timestamp.
- A pending self-registered account is inactive until an authorised verification action activates it.

## Planned SRS entities

`training_programmes`, `courses`, `instructors`, `course_enrolments`, `class_schedules`, `attendance_sessions`, `attendance_records`, `assessments`, `submissions`, `results`, `invoices`, `payments`, `receipts`, `certificates`, `notifications`, `assets`, `support_tickets`, `alumni`, and expanded `audit_logs`.
