# Student QR Code Attendance System
# Flask web application for student registration and QR-based attendance tracking

from flask import Flask, render_template, request, jsonify
import qrcode
import sqlite3
import os
import base64
from io import BytesIO

app = Flask(__name__)

# Create necessary directories for QR codes and database storage
os.makedirs('qr_codes', exist_ok=True)  # Store generated QR code images
os.makedirs('data', exist_ok=True)       # Store SQLite database file

# Database initialization function
# Creates two separate databases with specified structure
def init_db():
    # Database 1: Student and Subject data
    conn1 = sqlite3.connect('data/student_data.db')
    c1 = conn1.cursor()
    
    # Students table - only roll_no and name
    c1.execute('''CREATE TABLE IF NOT EXISTS students (
        roll_no TEXT PRIMARY KEY,               -- Student roll number (unique identifier)
        name TEXT NOT NULL                      -- Student full name
    )''')
    
    # Subjects table - only subject_id and subject_name
    c1.execute('''CREATE TABLE IF NOT EXISTS subjects (
        subject_id TEXT PRIMARY KEY,            -- Subject code (e.g., BCA-501)
        subject_name TEXT NOT NULL              -- Subject name (e.g., DBMS)
    )''')
    
    # Insert default BCA subjects
    subjects = [
        ('BCA-501', 'DBMS'),
        ('BCA-502', 'JAVA'),
        ('BCA-503', 'CN'),
        ('BCA-504', 'DBMS-LAB'),
        ('BCA-505', 'JAVA-LAB'),
    ]
    
    for subject_id, subject_name in subjects:
        c1.execute('INSERT OR IGNORE INTO subjects (subject_id, subject_name) VALUES (?, ?)', 
                  (subject_id, subject_name))
    
    conn1.commit()
    conn1.close()
    
    # Database 2: Attendance data
    conn2 = sqlite3.connect('data/attendance.db')
    c2 = conn2.cursor()
    
    # Attendance table - log_id, roll_no, subject_id, date&time, status
    c2.execute('''CREATE TABLE IF NOT EXISTS attendance (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Attendance log ID
        roll_no TEXT NOT NULL,                      -- Student roll number
        subject_id TEXT NOT NULL,                   -- Subject code
        datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Date and time
        status TEXT CHECK(status IN ('Present', 'Absent')) NOT NULL  -- Attendance status
    )''')
    
    conn2.commit()
    conn2.close()

# QR Code generation function
# Creates QR code containing student roll number
def generate_qr_code(roll_no):
    # Create QR code instance with specific settings
    qr = qrcode.QRCode(
        version=1,      # Controls QR code size (1 is smallest)
        box_size=10,    # Size of each box in pixels
        border=5        # Border size around QR code
    )
    
    # Add roll number as QR code data
    qr.add_data(roll_no)
    qr.make(fit=True)
    
    # Generate QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code image to local folder for permanent storage
    img.save(f'qr_codes/{roll_no}.png')
    
    # Convert image to base64 string for web display
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

# Home page route - serves the main interface
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/register-page')
def register_page():
    return render_template('register_page.html')

@app.route('/scanner-page')
def scanner_page():
    return render_template('scanner_page.html')

@app.route('/data-page')
def data_page():
    return render_template('data_page.html')

# Student registration endpoint
# Accepts POST requests with student data and generates QR code
@app.route('/register', methods=['POST'])
def register_student():
    # Get JSON data from frontend
    data = request.get_json()
    roll_no = data['roll_no']
    name = data['name']
    
    # Connect to student data database
    conn = sqlite3.connect('data/student_data.db')
    c = conn.cursor()
    
    try:
        # Insert new student into database
        c.execute('INSERT INTO students (roll_no, name) VALUES (?, ?)', (roll_no, name))
        conn.commit()
        
        # Generate QR code for the student
        qr_code = generate_qr_code(roll_no)
        
        # Return success response with QR code
        return jsonify({'success': True, 'qr_code': qr_code})
        
    except sqlite3.IntegrityError:
        # Handle duplicate roll number error
        return jsonify({'success': False, 'error': 'Roll number already exists'})
    except Exception as e:
        # Handle any other errors
        return jsonify({'success': False, 'error': str(e)})
    finally:
        # Always close database connection
        conn.close()

# QR code scanning endpoint
# Processes scanned QR codes and marks attendance
@app.route('/clear-data', methods=['POST'])
def clear_data():
    """Clear all data from both databases"""
    try:
        # Clear student_data.db
        conn1 = sqlite3.connect('data/student_data.db')
        c1 = conn1.cursor()
        c1.execute('DELETE FROM students')
        conn1.commit()
        conn1.close()
        
        # Clear attendance.db
        conn2 = sqlite3.connect('data/attendance.db')
        c2 = conn2.cursor()
        c2.execute('DELETE FROM attendance')
        conn2.commit()
        conn2.close()
        
        return jsonify({'success': True, 'message': 'All data cleared successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/data')
def show_data():
    """Display all database data from both databases"""
    try:
        # Get data from student_data.db
        conn1 = sqlite3.connect('data/student_data.db')
        c1 = conn1.cursor()
        
        c1.execute('SELECT * FROM students')
        students = c1.fetchall()
        
        c1.execute('SELECT * FROM subjects ORDER BY subject_name')
        subjects = c1.fetchall()
        
        conn1.close()
        
        # Get data from attendance.db
        conn2 = sqlite3.connect('data/attendance.db')
        c2 = conn2.cursor()
        
        c2.execute('SELECT * FROM attendance ORDER BY datetime DESC')
        attendance = c2.fetchall()
        
        conn2.close()
        
        # Format data for display
        data = {
            'database1_student_data': {
                'students': [{
                    'roll_no': row[0], 'name': row[1]
                } for row in students],
                'subjects': [{
                    'subject_id': row[0], 'subject_name': row[1]
                } for row in subjects]
            },
            'database2_attendance': {
                'attendance': [{
                    'log_id': row[0], 'roll_no': row[1], 'subject_id': row[2],
                    'datetime': row[3], 'status': row[4]
                } for row in attendance]
            }
        }
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)})

# Global variable to store current subject
current_subject = {'subject_id': 'BCA-501', 'subject_name': 'DBMS'}

@app.route('/subject')
def subject_page():
    """Subject selection page"""
    return render_template('subject.html')

@app.route('/get-subjects')
def get_subjects():
    """Get all subjects for dropdown"""
    try:
        conn = sqlite3.connect('data/student_data.db')
        c = conn.cursor()
        c.execute('SELECT * FROM subjects ORDER BY subject_name')
        subjects = c.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'subjects': [{'subject_id': row[0], 'subject_name': row[1]} for row in subjects],
            'current': current_subject
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/set-subject', methods=['POST'])
def set_subject():
    """Set current subject for attendance"""
    global current_subject
    try:
        data = request.get_json()
        subject_id = data['subject_id']
        
        # Get subject name from database
        conn = sqlite3.connect('data/student_data.db')
        c = conn.cursor()
        c.execute('SELECT subject_name FROM subjects WHERE subject_id = ?', (subject_id,))
        result = c.fetchone()
        conn.close()
        
        if result:
            current_subject = {'subject_id': subject_id, 'subject_name': result[0]}
            return jsonify({'success': True, 'current': current_subject})
        else:
            return jsonify({'success': False, 'error': 'Subject not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/scan', methods=['POST'])
def scan_qr():
    # Get scanned data from frontend
    data = request.get_json()
    roll_no = data['roll_no']                           # Roll number from QR code
    subject_id = current_subject['subject_id']          # Use current selected subject
    
    try:
        # Check if student exists in student_data.db
        conn1 = sqlite3.connect('data/student_data.db')
        c1 = conn1.cursor()
        c1.execute('SELECT * FROM students WHERE roll_no = ?', (roll_no,))
        student = c1.fetchone()
        conn1.close()
        
        if student:
            # Student found - mark attendance in attendance.db
            conn2 = sqlite3.connect('data/attendance.db')
            c2 = conn2.cursor()
            
            # Insert or update attendance record
            c2.execute('''INSERT OR REPLACE INTO attendance 
                         (roll_no, subject_id, status) 
                         VALUES (?, ?, ?)''',
                      (roll_no, subject_id, 'Present'))
            conn2.commit()
            conn2.close()
            
            # Return student details with attendance status
            return jsonify({
                'success': True, 
                'student': {
                    'roll_no': student[0],      # Roll number (primary key)
                    'name': student[1],         # Student name
                    'subject_id': subject_id,   # Subject being attended
                    'status': 'Present'         # Attendance status
                }
            })
        else:
            # Student not found in database
            return jsonify({'success': False, 'error': 'Student not found'})
            
    except Exception as e:
        # Handle database or other errors
        return jsonify({'success': False, 'error': str(e)})

# Application entry point
if __name__ == '__main__':
    # Initialize database tables on startup
    init_db()
    
    # Start Flask development server
    # host='0.0.0.0' allows access from any IP (needed for Docker)
    # port=5000 is the default Flask port
    # debug=True enables auto-reload and error details
    app.run(debug=True, host='0.0.0.0', port=5000)