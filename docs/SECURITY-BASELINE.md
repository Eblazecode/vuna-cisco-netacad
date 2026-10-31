# Security baseline and production blockers

- JWT access tokens are short-lived and refresh rotation is enabled. Add token blacklist support and privileged MFA enforcement before production.
- Django's password validators enforce a 12-character minimum and standard password checks.
- Public registration is throttled and creates a pending/inactive account.
- Management APIs require authentication and explicit role allow-lists.
- Student approval/rejection/suspension creates a status-history row and audit event.
- Audit records are application-level append-only; production should additionally enforce immutability through database permissions/WORM storage and monitor privileged database access.
- Production must use HTTPS, managed secrets, encrypted database/object storage, malware scanning, file size/type validation, backups, restore drills, log monitoring and an approved retention schedule.
- Do not configure live Paystack keys until the payment module has server-side verification, signature verification, idempotency and reconciliation tests.
- Complete a Nigerian Data Protection Act 2023 privacy impact assessment and approve privacy notice, data retention, data-subject request and breach-response procedures.
