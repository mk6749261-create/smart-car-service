# Smart Car Service & Maintenance System

## System Requirements Specification

### 1. Functional Requirements

#### FR-01: User Registration

The system shall allow new users to create an account using their required personal information and credentials.

#### FR-02: User Authentication

The system shall allow registered users to securely log in and log out.

#### FR-03: User Profile

The system shall allow authenticated users to view and update their profile information.

#### FR-04: Role-Based Access Control

The system shall support the following user roles:

* Customer
* Technician
* Manager

The system shall restrict access to features and actions according to the user's assigned role.

---

### 2. Vehicle Management Requirements

#### FR-05: Add Vehicle

The system shall allow a Customer to register a vehicle in their account.

Vehicle information shall include, as applicable:

* Make
* Model
* Manufacturing year
* License plate
* Vehicle identification information

#### FR-06: View Vehicles

The system shall allow a Customer to view the vehicles associated with their account.

#### FR-07: Update Vehicle

The system shall allow an authorized Customer to update their vehicle information.

#### FR-08: Delete Vehicle

The system shall allow an authorized Customer to remove a vehicle from their account, subject to related-data constraints.

#### FR-09: Vehicle Ownership

The system shall ensure that a Customer can only access and modify vehicles that belong to their account.

---

### 3. Maintenance Management Requirements

#### FR-10: Create Maintenance Request

The system shall allow an authorized user to create a maintenance request for a vehicle.

A maintenance request shall contain relevant information such as:

* Vehicle
* Service type
* Description
* Priority
* Status
* Request date

#### FR-11: View Maintenance Requests

The system shall allow authorized users to view maintenance requests according to their role and permissions.

#### FR-12: Maintenance Request Status

The system shall support maintenance request statuses such as:

* Pending
* Assigned
* In Progress
* Completed
* Cancelled

#### FR-13: Assign Technician

The system shall allow a Manager to assign an appropriate Technician to a maintenance request.

#### FR-14: Update Maintenance Status

The system shall allow an assigned Technician to update the status of an authorized maintenance request.

#### FR-15: Maintenance History

The system shall maintain a history of maintenance activities associated with each vehicle.

#### FR-16: Maintenance History Access

The system shall ensure that Customers can only access the maintenance history of vehicles they own.

---

### 4. Service and Appointment Requirements

#### FR-17: Service Management

The system shall maintain available vehicle maintenance services.

Each service may include:

* Service name
* Description
* Estimated duration
* Required information

#### FR-18: Service Availability

The system shall allow authorized users to view available service appointment slots.

#### FR-19: Book Appointment

The system shall allow an authorized Customer to book an available appointment for one of their vehicles.

#### FR-20: Appointment Validation

Before booking an appointment, the system shall validate:

* User authentication
* Vehicle ownership
* Service validity
* Slot availability
* Required parameters

#### FR-21: Prevent Double Booking

The system shall prevent multiple appointments from being booked for the same unavailable slot.

#### FR-22: View Appointments

The system shall allow users to view appointments relevant to their role.

#### FR-23: Cancel Appointment

The system shall allow an authorized user to cancel an appointment according to the system's cancellation rules.

---

### 5. AI Assistant Requirements

#### FR-24: AI Assistant Interface

The system shall provide an AI Assistant integrated into the authenticated user's dashboard.

#### FR-25: Context-Aware Assistance

The AI Assistant shall use the authenticated user's application context when responding to requests.

#### FR-26: Vehicle Information Queries

The AI Assistant shall be able to retrieve information about vehicles owned by the authenticated Customer.

#### FR-27: Maintenance Information Queries

The AI Assistant shall be able to retrieve and summarize relevant maintenance information for authorized vehicles.

#### FR-28: Appointment Queries

The AI Assistant shall be able to retrieve available appointment slots and relevant appointment information.

#### FR-29: Invalid Request Handling

The AI Assistant shall provide an appropriate response when a user's request is invalid, incomplete, unsupported, or cannot be executed.

---

### 6. Agentic AI Requirements

#### FR-30: Goal Understanding

The Agent shall interpret the user's high-level request and determine the required action.

#### FR-31: Tool Selection

The Agent shall select an appropriate backend tool based on the user's request.

#### FR-32: Tool Execution

The Agent shall execute backend tools only through predefined Django business logic.

#### FR-33: User Permission Validation

Every Agent tool execution shall validate the authenticated user's identity and permissions before performing the requested action.

#### FR-34: Parameter Validation

The system shall validate all parameters supplied to Agent tools before execution.

#### FR-35: Vehicle Retrieval Tool

The Agent shall provide a tool for retrieving vehicles owned by the authenticated user.

Example:

```text
get_user_vehicles()
```

#### FR-36: Maintenance History Tool

The Agent shall provide a tool for retrieving maintenance history for an authorized vehicle.

Example:

```text
get_maintenance_history(vehicle_id)
```

#### FR-37: Available Slots Tool

The Agent shall provide a tool for retrieving available appointment slots for a requested service.

Example:

```text
get_available_slots(service_id)
```

#### FR-38: Appointment Booking Tool

The Agent shall provide a tool for booking an appointment after validating the user, vehicle, service, and appointment slot.

Example:

```text
book_appointment(vehicle_id, service_id, slot_id)
```

#### FR-39: Multi-Step Agent Workflow

The Agent shall be capable of executing multiple tools sequentially when a user's request requires multiple steps.

Example workflow:

```text
User Request
     ↓
Get User Vehicles
     ↓
Get Maintenance History
     ↓
Get Available Slots
     ↓
Ask for Confirmation
     ↓
Book Appointment
```

#### FR-40: Confirmation for Critical Actions

The system shall require explicit user confirmation before executing actions that create or significantly modify data, such as booking an appointment.

#### FR-41: Unauthorized Tool Prevention

The Agent shall not execute a tool when the authenticated user does not have permission to perform the requested action.

#### FR-42: No Direct Database Access

The Agent shall not access the PostgreSQL database directly.

All database operations initiated by the Agent shall pass through validated Django business logic.

---

# 7. Security Requirements

#### NFR-01: Password Security

The system shall store user passwords using secure password hashing mechanisms provided by Django.

#### NFR-02: Authentication Protection

Protected pages and backend operations shall require authentication.

#### NFR-03: Authorization

The system shall enforce role-based permissions for protected operations.

#### NFR-04: Object-Level Authorization

Users shall not be able to access or modify resources belonging to other users unless explicitly authorized by their role.

#### NFR-05: Input Validation

User inputs and Agent tool parameters shall be validated before processing.

#### NFR-06: Database Integrity

The system shall use appropriate database constraints to maintain data consistency.

#### NFR-07: Destructive Action Protection

Actions that modify or delete important data shall include appropriate validation and confirmation mechanisms.

---

# 8. Database Requirements

#### DB-01: PostgreSQL

The system shall use PostgreSQL as its primary relational database.

#### DB-02: Relational Design

The database shall use normalized relational tables with appropriate primary keys and foreign keys.

#### DB-03: Data Integrity

The database shall enforce appropriate constraints such as:

* Primary Key
* Foreign Key
* Unique constraints
* NOT NULL constraints
* Appropriate indexes

#### DB-04: Relationships

The database shall support the required relationships between users, vehicles, maintenance records, services, technicians, and appointments.

#### DB-05: Single Source of Truth

Application data shall be stored and retrieved through the PostgreSQL database rather than hard-coded application data.

---

# 9. Frontend Requirements

#### UI-01: Responsive Interface

The system shall provide a usable web interface for the supported screen sizes.

#### UI-02: Dashboard

Authenticated users shall have access to a dashboard appropriate to their role.

#### UI-03: Navigation

Users shall be able to navigate between the features available to their role.

#### UI-04: AI Chat Interface

The dashboard shall include an integrated chat interface for interacting with the AI Assistant.

#### UI-05: Feedback

The interface shall provide appropriate feedback for successful operations, validation errors, and failed operations.

---

# 10. Performance and Reliability Requirements

#### NFR-08: Response Time

Normal application operations should provide responses within an acceptable time under the expected project workload.

#### NFR-09: Error Handling

The system shall handle application and tool execution errors without exposing sensitive technical information to users.

#### NFR-10: Consistency

The system shall maintain consistent database state when operations succeed or fail.

---

# 11. Maintainability Requirements

#### NFR-11: Modular Architecture

The system shall separate authentication, business logic, AI services, tools, and presentation responsibilities into appropriate modules.

#### NFR-12: Code Quality

The codebase shall follow clear naming conventions and maintainable Python and Django practices.

#### NFR-13: Documentation

Important architectural decisions, AI tools, database design, and project setup shall be documented.

---

# 12. Git and Version Control Requirements

#### GIT-01: Repository

The project shall be maintained in a public GitHub repository.

#### GIT-02: Continuous Commits

Development progress shall be committed continuously throughout the project.

#### GIT-03: Feature Branches

Major features should be developed using separate feature branches.

Example:

```text
feature/auth
feature/vehicles
feature/maintenance
feature/appointments
feature/ai-agent
feature/frontend
```

#### GIT-04: Pull Requests

Major features should be merged through Pull Requests.

#### GIT-05: Commit Convention

The project shall use clear and consistent commit messages.

Examples:

```text
feat: add vehicle management
feat: implement maintenance requests
feat: add appointment booking
feat: integrate AI agent tools
fix: prevent unauthorized vehicle access
docs: update project requirements
```

---

# 13. Out of Scope Requirements

The following features are outside the scope of Version 1:

* Online payment
* GPS/live vehicle tracking
* Mobile application
* SMS notifications
* Real-world spare-parts purchasing
* RAG
* Vector database
* Embedding-based retrieval
* Complex cloud orchestration
* Autonomous actions outside the application's defined tools
