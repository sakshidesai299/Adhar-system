import psycopg2
import streamlit as st
import datetime

# Database connection function
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname="Adhar system",
            user="postgres",
            password="Sakshi@299",
            host="localhost"
        )
        return conn
    except psycopg2.OperationalError as e:
        st.error(f"Database connection failed: {e}")
        return None

# --- CRUD Operations ---

# Create: Add a new citizen record
def create_citizen(aadhaar_id, name, dob, gender, address, biometric_id):
    conn = get_db_connection()
    if not conn: return False

    with conn.cursor() as cur:
        try:
            # Check for biometric ID duplication
            cur.execute("SELECT COUNT(*) FROM citizens WHERE biometric_id = %s;", (biometric_id,))
            if cur.fetchone()[0] > 0:
                # Log de-duplication conflict
                cur.execute("INSERT INTO deduplication_log (biometric_id, conflict_date) VALUES (%s, %s);",
                            (biometric_id, datetime.datetime.now()))
                conn.commit()
                st.warning("De-duplication conflict flagged. Manual review required.")
                return False

            # Insert new citizen record
            cur.execute(
                """
                INSERT INTO citizens (aadhaar_id, name, dob, gender, address, biometric_id, enrollment_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """,
                (aadhaar_id, name, dob, gender, address, biometric_id, datetime.datetime.now())
            )
            conn.commit()
            return True
        except psycopg2.Error as e:
            st.error(f"An error occurred during enrollment: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

# Read: Retrieve citizen records
def read_citizens():
    conn = get_db_connection()
    if not conn: return []

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM citizens ORDER BY enrollment_date DESC;")
        records = cur.fetchall()
        conn.close()
        return records

def read_citizen_by_aadhaar_id(aadhaar_id):
    conn = get_db_connection()
    if not conn: return None

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM citizens WHERE aadhaar_id = %s;", (aadhaar_id,))
        record = cur.fetchone()
        conn.close()
        return record

# Update: Update citizen's demographic details
def update_citizen(aadhaar_id, name, dob, gender, address):
    conn = get_db_connection()
    if not conn: return False

    with conn.cursor() as cur:
        try:
            cur.execute(
                """
                UPDATE citizens
                SET name = %s, dob = %s, gender = %s, address = %s
                WHERE aadhaar_id = %s;
                """,
                (name, dob, gender, address, aadhaar_id)
            )
            conn.commit()
            return True
        except psycopg2.Error as e:
            st.error(f"An error occurred during update: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

# Delete: Delete a citizen record (not used in this app, but good practice)
def delete_citizen(aadhaar_id):
    conn = get_db_connection()
    if not conn: return False
    with conn.cursor() as cur:
        try:
            cur.execute("DELETE FROM citizens WHERE aadhaar_id = %s;", (aadhaar_id,))
            conn.commit()
            return True
        except psycopg2.Error as e:
            st.error(f"An error occurred during deletion: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

# --- Authentication ---
def authenticate(aadhaar_id, submitted_biometric_id):
    conn = get_db_connection()
    if not conn: return False, "Database error."

    with conn.cursor() as cur:
        try:
            cur.execute("SELECT biometric_id FROM citizens WHERE aadhaar_id = %s;", (aadhaar_id,))
            record = cur.fetchone()
            
            is_successful = False
            message = ""

            if record and record[0] == submitted_biometric_id:
                is_successful = True
                message = "Authentication successful."
            else:
                is_successful = False
                message = "Authentication failed. Aadhaar ID or Biometric ID is incorrect."

            # Log authentication attempt
            cur.execute(
                """
                INSERT INTO authentication_log (aadhaar_id, attempt_date, is_successful)
                VALUES (%s, %s, %s);
                """,
                (aadhaar_id, datetime.datetime.now(), is_successful)
            )
            conn.commit()
            return is_successful, message
        except psycopg2.Error as e:
            st.error(f"An error occurred during authentication: {e}")
            conn.rollback()
            return False, "Database error."
        finally:
            conn.close()

# --- Business Intelligence & Reporting ---
def get_dashboard_metrics():
    conn = get_db_connection()
    if not conn: return {}

    metrics = {}
    with conn.cursor() as cur:
        # Total enrollments
        cur.execute("SELECT COUNT(*) FROM citizens;")
        metrics['total_enrollments'] = cur.fetchone()[0]

        # Auth attempts
        cur.execute("SELECT COUNT(*) FROM authentication_log;")
        metrics['total_auth_attempts'] = cur.fetchone()[0]

        # Successful auths
        cur.execute("SELECT COUNT(*) FROM authentication_log WHERE is_successful = TRUE;")
        metrics['successful_auths'] = cur.fetchone()[0]
        
        # Failed auths
        metrics['failed_auths'] = metrics['total_auth_attempts'] - metrics['successful_auths']

        # Recent auth attempts (for alerts)
        cur.execute(
            """
            SELECT is_successful, COUNT(*) 
            FROM authentication_log 
            WHERE attempt_date >= NOW() - INTERVAL '1 hour' 
            GROUP BY is_successful;
            """
        )
        recent_auths = {status: count for status, count in cur.fetchall()}
        metrics['recent_failed_auths'] = recent_auths.get(False, 0)
        
        # Deduplication conflicts
        cur.execute("SELECT COUNT(*) FROM deduplication_log;")
        metrics['dedup_conflicts'] = cur.fetchone()[0]

    conn.close()
    return metrics

def get_enrollment_history():
    conn = get_db_connection()
    if not conn: return []
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM citizens ORDER BY enrollment_date DESC;")
        history = cur.fetchall()
        conn.close()
        return history

def get_authentication_log():
    conn = get_db_connection()
    if not conn: return []
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM authentication_log ORDER BY attempt_date DESC;")
        log = cur.fetchall()
        conn.close()
        return log

def get_deduplication_log():
    conn = get_db_connection()
    if not conn: return []
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM deduplication_log ORDER BY conflict_date DESC;")
        log = cur.fetchall()
        conn.close()
        return log

# --- Database Setup (Run this once to initialize your DB) ---
def setup_database():
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="your_postgres_password",
        host="localhost"
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        try:
            cur.execute("CREATE DATABASE aadhaar_db;")
            st.success("Database 'aadhaar_db' created.")
        except psycopg2.errors.DuplicateDatabase:
            st.info("Database 'aadhaar_db' already exists.")

    conn.close()
    
    conn = get_db_connection()
    if not conn: return

    with conn.cursor() as cur:
        cur.execute(
            """
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
            """
        )
    conn.commit()
    conn.close()
    st.success("Tables created successfully.")