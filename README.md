# Student QR Attendance System

A Flask-based web application that modernizes student attendance tracking through QR code technology, eliminating manual attendance processes with instant, contactless attendance marking.

## 🚀 Features

### Core Functionality
- **Student Registration**: Register students with roll number and name
- **QR Code Generation**: Automatic QR code creation for each student
- **QR Code Scanning**: Camera-based real-time QR code detection
- **Attendance Tracking**: Daily attendance marking per subject
- **Multi-Subject Support**: DBMS, JAVA, CN, and Lab sessions
- **Download QR Codes**: PNG format for printing/sharing

### Technical Features
- Single-page responsive web application
- Real-time feedback with modal popups
- Duplicate prevention for roll numbers and attendance
- Automatic timestamp recording
- Local file storage for QR codes
- SQLite database with referential integrity

## ✅ Advantages

- **Instant Process**: QR scanning provides immediate attendance recording
- **Contactless**: Reduces physical interaction and paperwork
- **Accurate Tracking**: Automatic logging with precise timestamps
- **Easy Management**: Simple registration and QR generation workflow
- **Mobile Compatible**: Bootstrap responsive design works on all devices
- **Offline Capable**: Local SQLite database ensures functionality without internet
- **Containerized**: Docker support for easy deployment
- **Cost Effective**: No additional hardware required beyond camera-enabled devices
- **Scalable**: Can handle multiple subjects and large student databases

## ❌ Disadvantages

- **Camera Dependency**: Requires devices with functional cameras
- **Browser Limitations**: Needs modern browsers with camera API support
- **QR Code Management**: Students must carry/access their QR codes
- **Single Point Scanning**: One device scans at a time (no simultaneous scanning)
- **HTTPS Requirement**: Camera access requires HTTPS in production
- **Manual Subject Selection**: Faculty must manually select subject for each scan
- **No Bulk Operations**: Individual student registration only
- **Limited Reporting**: Basic attendance tracking without advanced analytics

## 🛠️ Development Process

### Phase 1: Planning & Design
1. **Requirement Analysis**: Identified need for contactless attendance system
2. **Technology Selection**: Chose Flask for simplicity and Python ecosystem
3. **Database Design**: Created normalized schema with three tables
4. **UI/UX Planning**: Designed single-page application workflow

### Phase 2: Backend Development
1. **Flask Application Setup**: Created main app.py with route structure
2. **Database Implementation**: SQLite schema with foreign key relationships
3. **QR Code Generation**: Integrated qrcode library with Pillow for image processing
4. **API Endpoints**: RESTful endpoints for registration and scanning
5. **Error Handling**: Comprehensive exception management

### Phase 3: Frontend Development
1. **HTML Structure**: Single-page layout with Bootstrap components
2. **JavaScript Integration**: Camera API and jsQR library implementation
3. **Form Handling**: Registration and scanning form validation
4. **Modal Components**: Real-time feedback and student information display
5. **Responsive Design**: Mobile-first approach with Bootstrap grid

### Phase 4: Integration & Testing
1. **Database Testing**: Verified foreign key constraints and data integrity
2. **QR Code Testing**: Validated generation, storage, and scanning workflow
3. **Cross-browser Testing**: Ensured camera API compatibility
4. **Error Scenario Testing**: Handled duplicates, missing data, and database errors

### Phase 5: Containerization
1. **Dockerfile Creation**: Python 3.9-slim base image configuration
2. **Docker Compose**: Service orchestration with volume mapping
3. **Volume Management**: Persistent storage for database and QR codes
4. **Port Configuration**: Host-container networking setup

## 📁 Code Structure

```
Project on Flask/
├── app.py                 # Main Flask application
│   ├── Database initialization
│   ├── QR code generation functions
│   ├── API endpoints (/register, /scan)
│   └── Error handling
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Docker orchestration
├── templates/            # HTML templates
│   └── index.html        # Single-page interface
│       ├── Bootstrap UI components
│       ├── Camera integration
│       ├── QR scanning logic
│       └── Form handling
├── data/                 # Database storage
│   └── attendance.db     # SQLite database
└── qr_codes/            # Generated QR images
    └── {roll_no}.png    # Individual QR files
```

### Key Components

#### Flask Application (`app.py`)
- **Database Manager**: SQLite connection handling with try-finally blocks
- **QR Generator**: Creates PNG images with base64 encoding
- **API Endpoints**: JSON request/response handling
- **Error Handling**: Catches IntegrityError and generic exceptions

#### Frontend (`templates/index.html`)
- **Bootstrap Framework**: Responsive UI components
- **Camera Integration**: getUserMedia API for video stream
- **QR Scanning**: jsQR library for real-time detection
- **Form Validation**: Client-side input validation

## 🗄️ Database Design

### Schema Structure

#### Students Table
```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL
);
```

#### Subjects Table
```sql
CREATE TABLE subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id TEXT UNIQUE NOT NULL,
    subject_name TEXT NOT NULL
);
```

#### Attendance Table
```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    attendance_date DATE NOT NULL,
    scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Present',
    FOREIGN KEY (roll_no) REFERENCES students (roll_no),
    FOREIGN KEY (subject_id) REFERENCES subjects (subject_id),
    UNIQUE(roll_no, subject_id, attendance_date)
);
```

### Database Features
- **Referential Integrity**: Foreign key constraints between tables
- **Unique Constraints**: Prevents duplicate students and daily attendance
- **Auto-increment IDs**: Primary keys for all tables
- **Timestamp Tracking**: Automatic scan time recording
- **Default Values**: Present status and current timestamp

## 🔧 Tools & Technologies

### Backend Stack
- **Python 3.9**: Primary programming language
- **Flask 2.3.3**: Lightweight web framework
- **SQLite3**: File-based relational database
- **QRCode 7.4.2**: QR code generation library
- **Pillow 10.0.1**: Image processing and manipulation

### Frontend Stack
- **HTML5**: Semantic markup with form validation
- **CSS3**: Bootstrap framework integration
- **JavaScript ES6+**: Modern async/await patterns
- **Bootstrap 5.1.3**: Responsive UI framework
- **jsQR 1.4.0**: Client-side QR code scanning

### Development Tools
- **Docker**: Application containerization
- **Docker Compose 3.8**: Service orchestration
- **Git**: Version control system

### Browser APIs
- **getUserMedia**: Camera access for QR scanning
- **Canvas API**: Image processing for QR detection
- **File API**: QR code download functionality
- **Fetch API**: HTTP requests to Flask endpoints

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Modern web browser with camera support
- Camera-enabled device

### Installation

1. **Clone Repository**
```bash
git clone <repository-url>
cd "Project on Flask"
```

2. **Docker Deployment**
```bash
docker-compose up --build
```

3. **Local Development**
```bash
pip install -r requirements.txt
python app.py
```

4. **Access Application**
```
http://localhost:5000
```

### Usage Workflow

1. **Register Student**: Enter roll number and name
2. **Generate QR Code**: System creates unique QR code
3. **Download QR**: Save PNG file for student use
4. **Scan Attendance**: Select subject and scan student QR code
5. **View Confirmation**: Modal displays student info and attendance status

## 📊 System Requirements

### Development Environment
- Docker 20.10+
- Docker Compose 1.29+
- 100MB disk space
- Camera-enabled device

### Browser Compatibility
- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+

### Production Deployment
- HTTPS certificate (required for camera access)
- Persistent storage for data directory
- Docker runtime environment

## 🔮 Future Enhancements

- **Bulk Registration**: CSV import for multiple students
- **Advanced Reporting**: Attendance analytics and reports
- **Mobile App**: Native mobile application
- **Cloud Integration**: Database synchronization
- **Biometric Integration**: Fingerprint or face recognition
- **Real-time Dashboard**: Live attendance monitoring
- **Email Notifications**: Automated attendance reports

## 📝 License

This project is developed as a minor project for college coursework.
