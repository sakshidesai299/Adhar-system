# Adhar-system
chumma
Aadhaar Management System
This is a small-scale Aadhaar management system designed to simulate key functionalities of a real-world Aadhaar enrollment and authentication process. The application allows a system administrator to manage citizen enrollments, handle authentication requests, and monitor system performance through a dynamic dashboard.

Table of Contents
Business Context

Features

Technology Stack

Setup and Installation

Database Schema

Usage

Business Context
The system is designed for a system administrator to manage enrollments, process authentication requests, and monitor system usage. A key feature is a dynamic dashboard that provides a real-time overview of new enrollments, authentication statuses, and system performance.

Features
Enrollment Management: Add, view, and update citizen records, including demographic and biometric information. The system performs a de-duplication check based on a unique biometric ID to ensure data integrity.

Authentication: Process authentication requests by matching a given Aadhaar ID with a submitted biometric ID. The system logs all attempts, marking them as successful or failed.

eKYC Function: Retrieve and display a citizen's demographic information upon successful authentication.

Dynamic Dashboard: A real-time dashboard displays key metrics such as total enrollments, and a breakdown of successful vs. failed authentication attempts.

Business Insights: Generate detailed reports and charts on enrollment history, authentication logs, and de-duplication conflicts.

Alerts: Provides warnings for a significant increase in failed authentication attempts or when a de-duplication conflict is detected.

Technology Stack
Frontend: Python with the Streamlit library.

Backend: Python with the psycopg2 library.

Database: PostgreSQL.

Setup and Installation
1. Prerequisites
Python 3.8 or higher.

PostgreSQL installed and running.

pip for Python package installation.

2. Database Setup
First, you need to set up the PostgreSQL database and create the required tables. You can use the psql command-line tool or a GUI like pgAdmin.

SQL

-- Create a new database
CREATE DATABASE aadhaar_db;

-- Connect to the database
\c aadhaar_db;

-- Create the necessary tables
CREATE TABLE IF NOT EXISTS citizens (
    aadhaar_id VARCHAR(12) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    dob DATE NOT NULL,
    gender VARCHAR(10) NOT NULL,
    address TEXT NOT NULL,
    biometric_id TEXT NOT NULL UNIQUE,
    enrollment_date TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS authentication_log (
    log_id SERIAL PRIMARY KEY,
    aadhaar_id VARCHAR(12) NOT NULL,
    attempt_date TIMESTAMP NOT NULL,
    is_successful BOOLEAN NOT NULL,
    FOREIGN KEY (aadhaar_id) REFERENCES citizens (aadhaar_id)
);

CREATE TABLE IF NOT EXISTS deduplication_log (
    log_id SERIAL PRIMARY KEY,
    biometric_id TEXT NOT NULL,
    conflict_date TIMESTAMP NOT NULL
);

-- Optional: Create a dedicated user for the application
CREATE USER aadhaar_user WITH PASSWORD 'aadhaar_password';
GRANT ALL PRIVILEGES ON DATABASE aadhaar_db TO aadhaar_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO aadhaar_db TO aadhaar_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO aadhaar_user;
3. Python Environment
Install the required Python libraries.

Bash

pip install streamlit psycopg2-binary
4. Running the Application
The application is split into backend.py and frontend.py. You will need both files in the same directory.

backend.py: Contains all the database logic, including CRUD operations, authentication functions, and business insights queries.

frontend.py: Contains the Streamlit code for the user interface, which calls the functions from backend.py.

To start the application, navigate to the directory where the files are saved and run the following command:

Bash

streamlit run frontend.py
Your browser will automatically open the application.

Database Schema
SQL

citizens
- aadhaar_id (VARCHAR(12), PRIMARY KEY)
- name (VARCHAR(100), NOT NULL)
- dob (DATE, NOT NULL)
- gender (VARCHAR(10), NOT NULL)
- address (TEXT, NOT NULL)
- biometric_id (TEXT, NOT NULL, UNIQUE)
- enrollment_date (TIMESTAMP, NOT NULL)

authentication_log
- log_id (SERIAL, PRIMARY KEY)
- aadhaar_id (VARCHAR(12), NOT NULL)
- attempt_date (TIMESTAMP, NOT NULL)
- is_successful (BOOLEAN, NOT NULL)

deduplication_log
- log_id (SERIAL, PRIMARY KEY)
- biometric_id (TEXT, NOT NULL)
- conflict_date (TIMESTAMP, NOT NULL)
Usage
Dashboard: The main page provides a high-level overview of system metrics.

Enrollment Management: Use this tab to enroll new citizens or update existing records.

Authentication: Use this tab to perform a simulated authentication and retrieve eKYC information.

Business Insights: This section offers detailed reports and charts on system usage, enrollment trends, and security-related logs.
