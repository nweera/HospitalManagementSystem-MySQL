from table_cr_ins import connect_db, add_appointment, view_appointments, update_appointment, delete_appointment
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import bcrypt
from datetime import datetime

# ============= Admin Authentication Section =============
def admin_login_page():
    """
    Creates and manages the admin login interface.
    - Displays username and password entry fields
    - Handles authentication against database
    - Opens main menu upon successful login
    """
    login_window = tk.Toplevel()
    login_window.title("Admin Login")
    tk.Label(login_window, text="Username").grid(row=0, column=0)
    tk.Label(login_window, text="Password").grid(row=1, column=0)

    username_entry = tk.Entry(login_window)
    password_entry = tk.Entry(login_window, show="*")  # Password field shows asterisks
    username_entry.grid(row=0, column=1)
    password_entry.grid(row=1, column=1)

    def verify_login():
        """
        Verifies admin credentials against the database:
        1. Retrieves hashed password for given username
        2. Compares input password with stored hash
        3. Opens main menu on success or shows error on failure
        """
        username = username_entry.get()
        password = password_entry.get()

        try:
            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("SELECT password FROM admin WHERE username = %s", (username,))
            result = cursor.fetchone()

            if result:
                hashed_password = result[0]
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                    messagebox.showinfo("Login", "Login successful!")
                    login_window.destroy()
                    open_main_menu()
                else:
                    messagebox.showerror("Login", "Incorrect password.")
            else:
                messagebox.showerror("Login", "Username not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")
        finally:
            cursor.close()
            conn.close()

    tk.Button(login_window, text="Login", command=verify_login).grid(row=2, column=1)
    login_window.mainloop()

# ============= Admin Main Menu Section =============
def open_main_menu():
    """
    Creates the main menu interface for administrators.
    Provides access to appointment management functions.
    """
    main_menu = tk.Toplevel()
    main_menu.title("Clinic Management System - Main Menu")
    tk.Label(main_menu, text="Welcome to the Clinic Management System!").pack()
    tk.Button(main_menu, text="View Appointments", command=view_appointments_gui).pack()

# ============= Appointment Management Section =============
def view_appointments_gui():
    """
    Creates the appointment viewing interface with a table showing all appointments.
    Includes buttons for CRUD operations (Create, Read, Update, Delete).
    Uses TreeView for organized display of appointment data.
    """
    view_window = tk.Toplevel()
    view_window.title("View Appointments")

    columns = ("ID","Availability","Patient Name","Doctor Name", "Date", "Time")
    tree = ttk.Treeview(view_window, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)

    tree.pack()

    def refresh_tree():
        """Refreshes the appointment list display with current database data"""
        for row in tree.get_children():
            tree.delete(row)
        appointments = view_appointments()
        for appointment in appointments:
            tree.insert("", "end", values=(appointment[0], appointment[5], appointment[1],
                       appointment[2], appointment[3], appointment[4]))

    refresh_tree()

    # CRUD operation buttons
    tk.Button(view_window, text="Add Appointment",
              command=lambda: add_appointment_gui(refresh_tree)).pack()
    tk.Button(view_window, text="Update Appointment",
              command=lambda: update_appointment_gui(refresh_tree)).pack()
    tk.Button(view_window, text="Delete Appointment",
              command=lambda: delete_appointment_gui(refresh_tree)).pack()

# ============= Appointment CRUD Operations Section =============
def add_appointment_gui(refresh_tree):
    """
    Interface for adding new appointments.
    Collects doctor name, date, and time information.
    Validates input format before adding to database.
    """
    add_window = tk.Toplevel()
    add_window.title("Add Appointment")

    # Entry fields setup
    tk.Label(add_window, text="Doctor Name").grid(row=1, column=0)
    tk.Label(add_window, text="Appointment Date (YYYY-MM-DD)").grid(row=2, column=0)
    tk.Label(add_window, text="Appointment Time (HH:MM:SS)").grid(row=3, column=0)

    doctor_name_entry = tk.Entry(add_window)
    appointment_date_entry = tk.Entry(add_window)
    appointment_time_entry = tk.Entry(add_window)

    doctor_name_entry.grid(row=1, column=1)
    appointment_date_entry.grid(row=2, column=1)
    appointment_time_entry.grid(row=3, column=1)

    def add_appointment_action():
        """Validates and processes the appointment addition"""
        doctor_name = doctor_name_entry.get()
        appointment_date = appointment_date_entry.get()
        appointment_time = appointment_time_entry.get()

        try:
            datetime.strptime(appointment_time, "%H:%M:%S")
            add_appointment(doctor_name, appointment_date, appointment_time)
            messagebox.showinfo("Success", "Appointment added successfully!")
            refresh_tree()
            add_window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid time format. Use HH:MM:SS.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add appointment: {e}")

    tk.Button(add_window, text="Add Appointment", command=add_appointment_action).grid(row=4, column=1)

# ============= Patient Interface Section =============
def patient_main_page():
    """
    Creates the main interface for patient access.
    Provides options to view and book available appointments.
    """
    patient_window = tk.Toplevel()
    patient_window.title("Clinic Management System - Patient")
    tk.Label(patient_window, text="Welcome to the Patient Portal!").pack()
    tk.Button(patient_window, text="View Available Appointments",
              command=view_available_appointments_gui).pack()

def view_available_appointments_gui():
    """
    Displays available appointments to patients.
    Shows appointment details in a table format.
    Includes functionality to book appointments.
    """
    view_window = tk.Toplevel()
    view_window.title("Available Appointments")

    columns = ("ID", "Doctor Name", "Date", "Time", "Availability")
    tree = ttk.Treeview(view_window, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)

    tree.pack()

    def refresh_tree():
        """Updates the display with current appointment availability"""
        for row in tree.get_children():
            tree.delete(row)
        appointments = view_appointments()
        for appointment in appointments:
            tree.insert("", "end", values=(appointment[0], appointment[2],
                       appointment[3], appointment[4], appointment[5]))

    refresh_tree()
    tk.Button(view_window, text="Book Appointment",
              command=lambda: book_appointment_gui(tree, refresh_tree)).pack()

# ============= Main Application Window =============
root = tk.Tk()
root.title("Clinic Management System")

# Setup main interface elements
tk.Label(root, text="Welcome to the Clinic Management System!",
         font=("Helvetica", 16)).pack(pady=10)
tk.Button(root, text="Admin Login", command=admin_login_page, width=20).pack(pady=5)
tk.Button(root, text="Patient Portal", command=patient_main_page, width=20).pack(pady=5)

# Start the application
root.mainloop()