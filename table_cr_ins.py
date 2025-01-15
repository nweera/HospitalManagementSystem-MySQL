import mysql.connector
import bcrypt


# ============= Database Initialization Section =============
def project():
    """
    Initializes the clinic management database and required tables.
    Creates the database and tables if they don't exist.
    Tables created:
    - admin: Stores administrator credentials
    - appointments: Stores appointment information
    """
    try:
        # Establish initial database connection
        conn = mysql.connector.connect(
            user="eya",
            password="admin"
        )
        cursor = conn.cursor()

        # Create main database
        cursor.execute("CREATE DATABASE IF NOT EXISTS clinic_manager")
        print("Database 'clinic_manager' created or already exists.")

        # Switch to the clinic_manager database
        conn.database = "clinic_manager"

        # Create admin table for authentication
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin (
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            )
        """)
        print("Table 'admin' created or already exists.")

        # Create appointments table with all necessary fields
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_name VARCHAR(100),
                doctor_name VARCHAR(100) NOT NULL,
                appointment_date DATE NOT NULL,
                appointment_time TIME NOT NULL,
                availability BOOLEAN DEFAULT TRUE,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Table 'appointments' created or already exists.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        cursor.close()
        conn.close()


# Initialize database and tables
project()


# ============= Admin Account Setup Section =============
def insert_admin():
    """
    Creates a default admin account in the database.
    - Username: admin88
    - Password: admin123 (stored as hashed value)
    Uses bcrypt for password hashing for security.
    """
    try:
        conn = mysql.connector.connect(
            user="eya",
            password="admin",
            database="clinic_manager"
        )
        cursor = conn.cursor()

        # Hash the admin password before storing
        hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())

        # Insert admin account, IGNORE prevents duplicate entry errors
        cursor.execute("""
            INSERT IGNORE INTO admin (username, password)
            VALUES (%s, %s)
        """, ('admin88', hashed_password))
        conn.commit()
        print("Admin account created successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()


# Create default admin account
insert_admin()


# ============= Database Connection Function =============
def connect_db():
    """
    Creates and returns a connection to the clinic_manager database.
    Used by other functions to establish database connections.

    Returns:
        mysql.connector.connection: Active database connection
    """
    return mysql.connector.connect(
        user="eya",
        password="admin",
        database="clinic_manager"
    )


# ============= Appointment Management Functions =============
def add_appointment(doctor_name, appointment_date, appointment_time):
    """
    Adds a new appointment to the database.

    Args:
        doctor_name (str): Name of the doctor
        appointment_date (str): Date of appointment (YYYY-MM-DD)
        appointment_time (str): Time of appointment (HH:MM:SS)
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO appointments (doctor_name, appointment_date, appointment_time, availability)
            VALUES (%s, %s, %s, %s)
        """, (doctor_name, appointment_date, appointment_time, True))
        conn.commit()
        print("Appointment added successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        cursor.close()
        conn.close()


def view_appointments():
    """
    Retrieves all appointments from the database.
    Orders results by availability (available first),
    then by date and time.

    Returns:
        list: List of appointment tuples containing all appointment information
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
                    SELECT * FROM appointments
                    ORDER BY availability DESC, appointment_date, appointment_time
                """)
        appointments = cursor.fetchall()
        return appointments

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        cursor.close()
        conn.close()


def update_appointment(appointment_id, doctor_name, appointment_date, appointment_time):
    """
    Updates an existing appointment's information.

    Args:
        appointment_id (int): ID of appointment to update
        doctor_name (str): Updated doctor name
        appointment_date (str): Updated date (YYYY-MM-DD)
        appointment_time (str): Updated time (HH:MM:SS)
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE appointments
            SET doctor_name = %s, appointment_date = %s, appointment_time = %s
            WHERE id = %s
        """, (doctor_name, appointment_date, appointment_time, appointment_id))
        conn.commit()
        print("Appointment updated successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        cursor.close()
        conn.close()


def delete_appointment(appointment_id):
    """
    Deletes an appointment from the database.

    Args:
        appointment_id (int): ID of appointment to delete

    Raises:
        Exception: If deletion fails
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM appointments WHERE id = %s", (appointment_id,))
        conn.commit()

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error deleting appointment: {e}")
        raise e