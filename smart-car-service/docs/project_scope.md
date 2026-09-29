#1.Smart Car Service & Maintenance System

**2. Problem Statement**
Car owners and service centers often face difficulties in tracking vehicle maintenance history, identifying overdue services, managing maintenance requests, and scheduling suitable service appointments. The system provides a centralized platform for managing vehicles, maintenance records, service requests, technicians, and appointments, while an AI Agent assists users and performs authorized actions through the application.


**3. Project Objective**
The objective of the Smart Car Service & Maintenance System is to provide
a centralized web-based platform for managing vehicle maintenance operations,
including vehicle records, maintenance history, service requests, technicians,
and appointments.

The system also integrates a context-aware AI Assistant and an Agentic AI
workflow capable of retrieving application data and executing authorized
actions through validated Django backend tools.


**4. Target Users**

1-Customer
Register/Login
Manage profile
Add vehicles
View vehicles
View maintenance history
Create maintenance requests
View appointments
Use AI Assistant


2-Technician
View assigned maintenance requests
Update maintenance status
View relevant vehicle/service information


3-Manager
Manage maintenance requests
Manage technicians
Assign technicians
Manage appointments
View vehicles and maintenance operations
Use AI Agent for management actions


**5. Core Features**

1-Authentication
Register
Login
Logout
Profile
Role-based access

2-Vehicle Management
Add vehicle
View vehicle
Edit vehicle
Delete vehicle
View vehicle details

3-Maintenance Management
Create maintenance request
View maintenance history
Track request status
Set priority
Assign technician
Update maintenance status

4-Appointment Management
View available slots
Book appointment
View appointments
Update appointment
Cancel appointment

4-AI Assistant
Ask about vehicle information
Ask about maintenance history
Ask about appointments
Summarize maintenance information

5-Agentic AI
Retrieve user's vehicles
Retrieve maintenance history
Find available appointments
Book appointment


**6. Project Scope**
In Scope
✓ Vehicle management
✓ Maintenance management
✓ Technician management
✓ Appointment management
✓ Authentication
✓ RBAC
✓ PostgreSQL
✓ AI chatbot
✓ Agentic AI
✓ Tool Calling
✓ Permission validation
✓ Input validation


**7.AI Agent Scope**
Tool 1
get_user_vehicles()

Purpose:
Retrieve vehicles owned by the authenticated user.

Tool 2
get_maintenance_history(vehicle_id)

Purpose:
Retrieve maintenance records for a vehicle owned by the authenticated user.

Tool 3
get_available_slots(service_id)

Purpose:
Retrieve available maintenance appointment slots.

Tool 4
book_appointment(vehicle_id, service_id, slot_id)

Purpose:
Book an appointment after validating the user's permissions and the availability of the selected slot.



**7.Agent Workflow**

User
  ↓
AI Assistant
  ↓
Understand User Goal
  ↓
Select Tool
  ↓
Validate Parameters
  ↓
Check User Permissions
  ↓
Execute Django Function
  ↓
Database
  ↓
Return Tool Result
  ↓
AI
  ↓
Final Response

