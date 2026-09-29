# Database Design

## Smart Car Service & Maintenance System

### 1. Database Overview

The system uses PostgreSQL as the primary relational database.

The database is designed to support:

* User authentication and role-based access control
* Vehicle management
* Maintenance requests
* Maintenance history
* Vehicle maintenance services
* Service appointment slots
* Appointment booking

The database follows a normalized relational structure and uses primary keys, foreign keys, unique constraints, indexes, and appropriate validation rules to maintain data integrity.

---

# 2. Entities

The system contains the following main entities:

1. User
2. Vehicle
3. Service
4. MaintenanceRequest
5. MaintenanceRecord
6. ServiceSlot
7. Appointment

The Technician is represented by the `User` entity with the role `Technician`, rather than using a separate Technician table.

---

# 3. User

The User entity represents all authenticated users of the system.

Supported roles:

* Customer
* Technician
* Manager

### Attributes

| Field       | Type      | Key | Required | Constraints                     |
| ----------- | --------- | --- | -------- | ------------------------------- |
| id          | BIGINT    | PK  | Yes      | Auto-generated                  |
| username    | VARCHAR   | —   | Yes      | Unique                          |
| email       | VARCHAR   | —   | Yes      | Unique                          |
| password    | VARCHAR   | —   | Yes      | Django password hashing         |
| first_name  | VARCHAR   | —   | Yes      | —                               |
| last_name   | VARCHAR   | —   | Yes      | —                               |
| role        | VARCHAR   | —   | Yes      | Customer / Technician / Manager |
| is_active   | BOOLEAN   | —   | Yes      | Default: True                   |
| date_joined | TIMESTAMP | —   | Yes      | Auto-generated                  |

### Notes

The project should use Django's built-in authentication system or a custom user model based on Django authentication rather than implementing password hashing manually.

---

# 4. Vehicle

The Vehicle entity stores vehicles owned by Customers.

### Attributes

| Field         | Type         | Key | Required | Constraints        |
| ------------- | ------------ | --- | -------- | ------------------ |
| id            | BIGINT       | PK  | Yes      | Auto-generated     |
| owner_id      | BIGINT       | FK  | Yes      | References User    |
| make          | VARCHAR(100) | —   | Yes      | —                  |
| model         | VARCHAR(100) | —   | Yes      | —                  |
| year          | INTEGER      | —   | Yes      | Valid vehicle year |
| license_plate | VARCHAR(30)  | —   | Yes      | Unique             |
| created_at    | TIMESTAMP    | —   | Yes      | Auto-generated     |
| updated_at    | TIMESTAMP    | —   | Yes      | Auto-updated       |

### Relationships

```text
User 1 ─────── N Vehicle
```

One Customer can own multiple vehicles.

A vehicle belongs to exactly one Customer.

---

# 5. Service

The Service entity represents maintenance services offered by the service center.

Examples:

* Oil Change
* Brake Inspection
* Tire Replacement
* Engine Check
* Periodic Maintenance

### Attributes

| Field              | Type         | Key | Required | Constraints         |
| ------------------ | ------------ | --- | -------- | ------------------- |
| id                 | BIGINT       | PK  | Yes      | Auto-generated      |
| name               | VARCHAR(150) | —   | Yes      | Unique              |
| description        | TEXT         | —   | No       | —                   |
| estimated_duration | INTEGER      | —   | Yes      | Duration in minutes |
| is_active          | BOOLEAN      | —   | Yes      | Default: True       |
| created_at         | TIMESTAMP    | —   | Yes      | Auto-generated      |

### Relationships

```text
Service 1 ─────── N MaintenanceRequest

Service 1 ─────── N MaintenanceRecord

Service 1 ─────── N ServiceSlot
```

---

# 6. MaintenanceRequest

The MaintenanceRequest entity represents a customer's request for vehicle maintenance.

### Attributes

| Field         | Type        | Key | Required | Constraints                                              |
| ------------- | ----------- | --- | -------- | -------------------------------------------------------- |
| id            | BIGINT      | PK  | Yes      | Auto-generated                                           |
| vehicle_id    | BIGINT      | FK  | Yes      | References Vehicle                                       |
| service_id    | BIGINT      | FK  | Yes      | References Service                                       |
| technician_id | BIGINT      | FK  | No       | References User                                          |
| description   | TEXT        | Yes | Yes      | —                                                        |
| priority      | VARCHAR(20) | —   | Yes      | Low / Medium / High / Critical                           |
| status        | VARCHAR(30) | —   | Yes      | Pending / Assigned / In Progress / Completed / Cancelled |
| created_at    | TIMESTAMP   | —   | Yes      | Auto-generated                                           |
| updated_at    | TIMESTAMP   | —   | Yes      | Auto-updated                                             |

### Relationships

```text
Vehicle 1 ─────── N MaintenanceRequest

Service 1 ─────── N MaintenanceRequest

User (Technician) 1 ─────── N MaintenanceRequest
```

A vehicle can have multiple maintenance requests.

A service can be requested many times.

A Technician can be assigned to multiple maintenance requests.

---

# 7. MaintenanceRecord

The MaintenanceRecord entity stores completed maintenance activities and forms the maintenance history of a vehicle.

### Attributes

| Field                  | Type          | Key | Required | Constraints                   |
| ---------------------- | ------------- | --- | -------- | ----------------------------- |
| id                     | BIGINT        | PK  | Yes      | Auto-generated                |
| vehicle_id             | BIGINT        | FK  | Yes      | References Vehicle            |
| service_id             | BIGINT        | FK  | Yes      | References Service            |
| technician_id          | BIGINT        | FK  | Yes      | References User               |
| maintenance_request_id | BIGINT        | FK  | No       | References MaintenanceRequest |
| description            | TEXT          | No  | No       | —                             |
| cost                   | DECIMAL(10,2) | —   | No       | >= 0                          |
| performed_at           | TIMESTAMP     | —   | Yes      | —                             |
| created_at             | TIMESTAMP     | —   | Yes      | Auto-generated                |

### Relationships

```text
Vehicle 1 ─────── N MaintenanceRecord

Service 1 ─────── N MaintenanceRecord

User (Technician) 1 ─────── N MaintenanceRecord

MaintenanceRequest 1 ─────── 0..N MaintenanceRecord
```

### Purpose

`MaintenanceRequest` represents requested/current work.

`MaintenanceRecord` represents completed historical work.

This separation allows the AI Agent to analyze a vehicle's maintenance history without confusing previous completed services with current requests.

---

# 8. ServiceSlot

The ServiceSlot entity represents an available time slot for a particular service and technician.

### Attributes

| Field         | Type        | Key | Required | Constraints                  |
| ------------- | ----------- | --- | -------- | ---------------------------- |
| id            | BIGINT      | PK  | Yes      | Auto-generated               |
| service_id    | BIGINT      | FK  | Yes      | References Service           |
| technician_id | BIGINT      | FK  | Yes      | References User              |
| start_time    | TIMESTAMP   | —   | Yes      | —                            |
| end_time      | TIMESTAMP   | —   | Yes      | Must be after start_time     |
| status        | VARCHAR(20) | —   | Yes      | Available / Booked / Blocked |
| created_at    | TIMESTAMP   | —   | Yes      | Auto-generated               |

### Relationships

```text
Service 1 ─────── N ServiceSlot

User (Technician) 1 ─────── N ServiceSlot
```

A service can have multiple available slots.

A Technician can have multiple slots.

---

# 9. Appointment

The Appointment entity represents an actual booking made by a Customer.

### Attributes

| Field      | Type        | Key | Required | Constraints                       |
| ---------- | ----------- | --- | -------- | --------------------------------- |
| id         | BIGINT      | PK  | Yes      | Auto-generated                    |
| vehicle_id | BIGINT      | FK  | Yes      | References Vehicle                |
| slot_id    | BIGINT      | FK  | Yes      | References ServiceSlot            |
| status     | VARCHAR(20) | —   | Yes      | Confirmed / Cancelled / Completed |
| notes      | TEXT        | No  | No       | —                                 |
| created_at | TIMESTAMP   | —   | Yes      | Auto-generated                    |
| updated_at | TIMESTAMP   | —   | Yes      | Auto-updated                      |

### Relationships

```text
Vehicle 1 ─────── N Appointment

ServiceSlot 1 ─────── 0..1 Appointment
```

A Customer books an appointment for one of their vehicles.

A ServiceSlot can be associated with at most one active appointment.

---

# 10. Relationship Summary

| Relationship                           | Cardinality |
| -------------------------------------- | ----------- |
| User → Vehicle                         | 1 : N       |
| Vehicle → MaintenanceRequest           | 1 : N       |
| Service → MaintenanceRequest           | 1 : N       |
| Technician(User) → MaintenanceRequest  | 1 : N       |
| Vehicle → MaintenanceRecord            | 1 : N       |
| Service → MaintenanceRecord            | 1 : N       |
| Technician(User) → MaintenanceRecord   | 1 : N       |
| MaintenanceRequest → MaintenanceRecord | 1 : 0..N    |
| Service → ServiceSlot                  | 1 : N       |
| Technician(User) → ServiceSlot         | 1 : N       |
| Vehicle → Appointment                  | 1 : N       |
| ServiceSlot → Appointment              | 1 : 0..1    |

---

# 11. Important Database Constraints

The database and Django application should enforce the following constraints:

### User

* Username must be unique.
* Email must be unique.
* Role must be one of the supported roles.

### Vehicle

* License plate must be unique.
* Vehicle year must contain a valid value.
* A vehicle must have an owner.

### Service

* Service name must be unique.
* Estimated duration must be greater than zero.

### MaintenanceRequest

* Vehicle must exist.
* Service must exist.
* Assigned technician must have the Technician role.
* Priority must use a valid value.
* Status must use a valid value.

### MaintenanceRecord

* Cost cannot be negative.
* Vehicle, service, and technician must exist.
* Technician must have the Technician role.

### ServiceSlot

* End time must be after start time.
* Technician must have the Technician role.
* Slot status must use a valid value.

### Appointment

* Vehicle must exist.
* Slot must exist.
* A booked slot cannot be booked again.
* The vehicle must belong to the authenticated Customer before booking.

---

# 12. Indexes

Indexes should be added to fields frequently used for searching and filtering.

Recommended indexes include:

```text
Vehicle.owner_id
Vehicle.license_plate

MaintenanceRequest.vehicle_id
MaintenanceRequest.technician_id
MaintenanceRequest.status

MaintenanceRecord.vehicle_id
MaintenanceRecord.performed_at

ServiceSlot.service_id
ServiceSlot.technician_id
ServiceSlot.start_time
ServiceSlot.status

Appointment.vehicle_id
Appointment.slot_id
Appointment.status
```

---

# 13. Normalization

The database is designed to follow relational normalization principles and target Third Normal Form (3NF).

Examples:

* User information is stored in User rather than duplicated in Vehicle or Appointment.
* Service information is stored once in Service.
* Technician information is represented by User rather than duplicated in multiple tables.
* Maintenance history is separated from active maintenance requests.
* Appointment information references a ServiceSlot rather than duplicating slot details.

This reduces data duplication and improves consistency.

---

# 14. AI Agent Database Interaction

The AI Agent shall never access PostgreSQL directly.

The Agent communicates with validated Django tools.

Example:

```text
User
  ↓
AI Agent
  ↓
Django Tool
  ↓
Permission Validation
  ↓
Business Logic
  ↓
Django ORM
  ↓
PostgreSQL
  ↓
Tool Result
  ↓
AI Agent
  ↓
User
```

Example:

```text
get_maintenance_history(vehicle_id)
```

The Django tool must verify that the requested vehicle belongs to the authenticated user before retrieving its maintenance history.

---

# 15. Database Design Decision

The final database design uses seven main entities:

```text
User
Vehicle
Service
MaintenanceRequest
MaintenanceRecord
ServiceSlot
Appointment
```

The design provides the required foundation for authentication, vehicle management, maintenance management, appointment booking, and Agentic AI tool execution.
