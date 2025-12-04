# Student QR Attendance System - Complete Technical Documentation

## 📋 Project Overview

A comprehensive Flask-based web application that revolutionizes student attendance tracking through QR code technology, providing instant, contactless attendance marking with real-time data processing.

## 🎨 Frontend Process

### Architecture & Design
- **Single Page Application (SPA)**: Unified interface combining registration and scanning
- **Responsive Design**: Bootstrap 5.1.3 framework for mobile-first approach
- **Component-Based Structure**: Modular sections for different functionalities

### User Interface Components

#### Registration Section
```html
<!-- Student Registration Form -->
<div class="card">
    <form id="registrationForm">
        <input type="text" id="rollNo" placeholder="Roll Number" required>
        <input type="text" id="studentName" placeholder="Student Name" required>
        <button type="submit">Register & Generate QR</button>
    </form>
</div>
```

#### QR Scanner Section
```html
<!-- Camera Integration -->
<video id="video" autoplay playsinline></video>
<canvas id="canvas" style="display: none;"></canvas>
<select id="subjectSelect">
    <option value="DBMS">Database Management System</option>
    <option value="JAVA">Java Programming</option>
    <option value="CN">Computer Networks</option>
    <option value="LAB">Laboratory</option>
</select>
```

### JavaScript Functionality

#### Camera Integration
```javascript
// Initialize camera for QR scanning
async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment' }
        });
        video.srcObject = stream;
        scanQRCode();
    } catch (error) {
        console.error('Camera access denied:', error);
    }
}
```

#### QR Code Detection
```javascript
// Real-time QR code scanning
function scanQRCode() {
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');
    
    function tick() {
        if (video.readyState === video.HAVE_ENOUGH_DATA) {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
            const code = jsQR(imageData.data, imageData.width, imageData.height);
            
            if (code) {
                handleQRScan(code.data);
            }
        }
        requestAnimationFrame(tick);
    }
    tick();
}
```

#### Form Handling & API Communication
```javascript
// Student registration with AJAX
async function registerStudent(rollNo, name) {
    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ roll_no: rollNo, name: name })
        });
        
        const result = await response.json();
        if (result.success) {
            displayQRCode(result.qr_code);
            showSuccessModal('Student registered successfully!');
        } else {
            showErrorModal(result.error);
        }
    } catch (error) {
        showErrorModal('Registration failed: ' + error.message);
    }
}
```

### UI/UX Features
- **Real-time Feedback**: Instant modal popups for success/error states
- **Progressive Enhancement**: Graceful degradation for older browsers
- **Accessibility**: ARIA labels and keyboard navigation support
- **Mobile Optimization**: Touch-friendly interface with proper viewport settings

## ⚙️ Backend Process

### Flask Application Architecture

#### Application Structure
```python
# Main Flask application setup
from flask import Flask, request, jsonify, render_template
import sqlite3
import qrcode
from PIL import Image
import base64
from io import BytesIO
import os
from datetime import datetime

app = Flask(__name__)

# Global configuration
DATABASE_PATH = 'data/attendance.db'
QR_CODES_DIR = 'qr_codes'
```

#### Database Connection Management
```python
def get_db_connection():
    """Establish database connection with error handling"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def init_db():
    """Initialize database with required tables"""
    conn = get_db_connection()
    if conn:
        try:
            # Create tables with foreign key constraints
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    roll_no TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_id TEXT UNIQUE NOT NULL,
                    subject_name TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS attendance (
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
            ''')
            
            # Insert default subjects
            subjects = [
                ('DBMS', 'Database Management System'),
                ('JAVA', 'Java Programming'),
                ('CN', 'Computer Networks'),
                ('LAB', 'Laboratory')
            ]
            
            conn.executemany(
                'INSERT OR IGNORE INTO subjects (subject_id, subject_name) VALUES (?, ?)',
                subjects
            )
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
        finally:
            conn.close()
```

#### QR Code Generation System
```python
def generate_qr_code(roll_no):
    """Generate QR code for student roll number"""
    try:
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=5,
        )
        
        # Add roll number data
        qr.add_data(roll_no)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to file
        os.makedirs(QR_CODES_DIR, exist_ok=True)
        file_path = f'{QR_CODES_DIR}/{roll_no}.png'
        img.save(file_path)
        
        # Convert to base64 for web display
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f'data:image/png;base64,{img_str}'
        
    except Exception as e:
        print(f"QR code generation error: {e}")
        return None
```

#### API Endpoints

##### Student Registration Endpoint
```python
@app.route('/register', methods=['POST'])
def register_student():
    """Register new student and generate QR code"""
    try:
        data = request.get_json()
        roll_no = data.get('roll_no', '').strip()
        name = data.get('name', '').strip()
        
        # Validate input
        if not roll_no or not name:
            return jsonify({
                'success': False, 
                'error': 'Roll number and name are required'
            }), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False, 
                'error': 'Database connection failed'
            }), 500
        
        try:
            # Insert student record
            conn.execute(
                'INSERT INTO students (roll_no, name) VALUES (?, ?)',
                (roll_no, name)
            )
            conn.commit()
            
            # Generate QR code
            qr_code = generate_qr_code(roll_no)
            if not qr_code:
                return jsonify({
                    'success': False, 
                    'error': 'QR code generation failed'
                }), 500
            
            return jsonify({
                'success': True,
                'qr_code': qr_code,
                'message': f'Student {name} registered successfully'
            })
            
        except sqlite3.IntegrityError:
            return jsonify({
                'success': False, 
                'error': 'Roll number already exists'
            }), 409
            
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': f'Registration failed: {str(e)}'
        }), 500
    finally:
        if conn:
            conn.close()
```

##### QR Scanning Endpoint
```python
@app.route('/scan', methods=['POST'])
def scan_qr():
    """Process QR code scan and mark attendance"""
    try:
        data = request.get_json()
        roll_no = data.get('roll_no', '').strip()
        subject_id = data.get('subject_id', '').strip()
        
        if not roll_no or not subject_id:
            return jsonify({
                'success': False, 
                'error': 'Roll number and subject are required'
            }), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False, 
                'error': 'Database connection failed'
            }), 500
        
        try:
            # Verify student exists
            student = conn.execute(
                'SELECT * FROM students WHERE roll_no = ?', 
                (roll_no,)
            ).fetchone()
            
            if not student:
                return jsonify({
                    'success': False, 
                    'error': 'Student not found'
                }), 404
            
            # Mark attendance
            today = datetime.now().date()
            conn.execute('''
                INSERT OR REPLACE INTO attendance 
                (roll_no, subject_id, attendance_date, scan_time, status) 
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, 'Present')
            ''', (roll_no, subject_id, today))
            conn.commit()
            
            return jsonify({
                'success': True,
                'student': {
                    'roll_no': student['roll_no'],
                    'name': student['name']
                },
                'subject_id': subject_id,
                'message': 'Attendance marked successfully'
            })
            
        except sqlite3.Error as e:
            return jsonify({
                'success': False, 
                'error': f'Database error: {str(e)}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': f'Scan processing failed: {str(e)}'
        }), 500
    finally:
        if conn:
            conn.close()
```

### Error Handling & Logging
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500
```

## 🗄️ Database Design & Management

### Database Schema Architecture

#### Entity Relationship Diagram
```
Students (1) -----> (M) Attendance (M) <----- (1) Subjects
   |                      |                      |
roll_no              roll_no, subject_id    subject_id
name                 attendance_date         subject_name
created_at           scan_time
                     status
```

#### Table Specifications

##### Students Table
```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT UNIQUE NOT NULL,           -- Unique student identifier
    name TEXT NOT NULL,                     -- Student full name
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_roll_no_format CHECK (length(roll_no) >= 3),
    CONSTRAINT chk_name_length CHECK (length(name) >= 2)
);

-- Indexes for performance
CREATE INDEX idx_students_roll_no ON students(roll_no);
CREATE INDEX idx_students_created_at ON students(created_at);
```

##### Subjects Table
```sql
CREATE TABLE subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id TEXT UNIQUE NOT NULL,        -- Subject code (DBMS, JAVA, etc.)
    subject_name TEXT NOT NULL,             -- Full subject name
    
    -- Constraints
    CONSTRAINT chk_subject_id_format CHECK (length(subject_id) >= 2),
    CONSTRAINT chk_subject_name_length CHECK (length(subject_name) >= 3)
);

-- Pre-populated data
INSERT INTO subjects (subject_id, subject_name) VALUES
('DBMS', 'Database Management System'),
('JAVA', 'Java Programming'),
('CN', 'Computer Networks'),
('LAB', 'Laboratory');
```

##### Attendance Table
```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT NOT NULL,                  -- Foreign key to students
    subject_id TEXT NOT NULL,               -- Foreign key to subjects
    attendance_date DATE NOT NULL,          -- Date of attendance
    scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Present',          -- Present/Absent/Late
    
    -- Foreign key constraints
    FOREIGN KEY (roll_no) REFERENCES students (roll_no) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects (subject_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    
    -- Business logic constraints
    UNIQUE(roll_no, subject_id, attendance_date),
    CONSTRAINT chk_status CHECK (status IN ('Present', 'Absent', 'Late'))
);

-- Indexes for query optimization
CREATE INDEX idx_attendance_roll_no ON attendance(roll_no);
CREATE INDEX idx_attendance_subject_id ON attendance(subject_id);
CREATE INDEX idx_attendance_date ON attendance(attendance_date);
CREATE INDEX idx_attendance_composite ON attendance(roll_no, subject_id, attendance_date);
```

### Database Operations & Queries

#### Common Query Patterns
```sql
-- Student registration check
SELECT COUNT(*) FROM students WHERE roll_no = ?;

-- Daily attendance summary
SELECT 
    s.subject_name,
    COUNT(a.id) as present_count,
    (SELECT COUNT(*) FROM students) as total_students,
    ROUND(COUNT(a.id) * 100.0 / (SELECT COUNT(*) FROM students), 2) as attendance_percentage
FROM attendance a
JOIN subjects s ON a.subject_id = s.subject_id
WHERE a.attendance_date = DATE('now')
GROUP BY a.subject_id, s.subject_name;

-- Student attendance history
SELECT 
    s.subject_name,
    a.attendance_date,
    a.scan_time,
    a.status
FROM attendance a
JOIN subjects s ON a.subject_id = s.subject_id
WHERE a.roll_no = ?
ORDER BY a.attendance_date DESC, a.scan_time DESC;

-- Monthly attendance report
SELECT 
    strftime('%Y-%m', a.attendance_date) as month,
    s.subject_name,
    COUNT(a.id) as classes_attended,
    COUNT(DISTINCT a.attendance_date) as total_classes
FROM attendance a
JOIN subjects s ON a.subject_id = s.subject_id
WHERE a.roll_no = ?
GROUP BY month, s.subject_name
ORDER BY month DESC;
```

### Data Integrity & Validation

#### Constraints Implementation
```python
def validate_student_data(roll_no, name):
    """Validate student registration data"""
    errors = []
    
    # Roll number validation
    if not roll_no or len(roll_no.strip()) < 3:
        errors.append("Roll number must be at least 3 characters")
    
    if not roll_no.isalnum():
        errors.append("Roll number must contain only letters and numbers")
    
    # Name validation
    if not name or len(name.strip()) < 2:
        errors.append("Name must be at least 2 characters")
    
    if not all(c.isalpha() or c.isspace() for c in name):
        errors.append("Name must contain only letters and spaces")
    
    return errors

def validate_attendance_data(roll_no, subject_id):
    """Validate attendance marking data"""
    errors = []
    
    # Check if student exists
    conn = get_db_connection()
    student = conn.execute(
        'SELECT id FROM students WHERE roll_no = ?', 
        (roll_no,)
    ).fetchone()
    
    if not student:
        errors.append("Student not found")
    
    # Check if subject exists
    subject = conn.execute(
        'SELECT id FROM subjects WHERE subject_id = ?', 
        (subject_id,)
    ).fetchone()
    
    if not subject:
        errors.append("Subject not found")
    
    conn.close()
    return errors
```

## 🐳 Docker Configuration & Containerization

### Dockerfile Architecture

#### Multi-stage Build Process
```dockerfile
# Use official Python runtime as base image
FROM python:3.9-slim

# Set working directory in container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data qr_codes

# Set proper permissions
RUN chmod -R 755 /app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Run application
CMD ["python", "app.py"]
```

### Docker Compose Configuration

#### Service Orchestration
```yaml
version: '3.8'

services:
  web:
    build: .
    container_name: qr_attendance_app
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./qr_codes:/app/qr_codes
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=0
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - qr_network

networks:
  qr_network:
    driver: bridge

volumes:
  qr_data:
    driver: local
  qr_codes:
    driver: local
```

#### Production Docker Compose
```yaml
version: '3.8'

services:
  web:
    build: .
    container_name: qr_attendance_prod
    ports:
      - "80:5000"
    volumes:
      - qr_data:/app/data
      - qr_codes:/app/qr_codes
      - ./logs:/app/logs
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=0
      - DATABASE_URL=sqlite:///data/attendance.db
    restart: always
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  nginx:
    image: nginx:alpine
    container_name: qr_nginx
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: always

volumes:
  qr_data:
    driver: local
  qr_codes:
    driver: local
```

### Container Management Commands

#### Development Workflow
```bash
# Build and start services
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop services
docker-compose down

# Remove volumes (clean slate)
docker-compose down -v

# Scale services
docker-compose up --scale web=3

# Execute commands in container
docker-compose exec web python -c "from app import init_db; init_db()"
```

#### Production Deployment
```bash
# Production build
docker-compose -f docker-compose.prod.yml up --build -d

# Monitor container health
docker-compose ps
docker stats

# Backup data
docker run --rm -v qr_data:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz /data

# Restore data
docker run --rm -v qr_data:/data -v $(pwd):/backup alpine tar xzf /backup/backup.tar.gz -C /
```

## 🔄 Jenkins CI/CD Pipeline

### Jenkinsfile Configuration

#### Complete Pipeline Setup
```groovy
pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'qr-attendance-system'
        DOCKER_TAG = "${BUILD_NUMBER}"
        REGISTRY_URL = 'your-registry.com'
        DEPLOY_SERVER = 'your-server.com'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(
                        script: "git rev-parse --short HEAD",
                        returnStdout: true
                    ).trim()
                }
            }
        }
        
        stage('Code Quality') {
            parallel {
                stage('Lint Python') {
                    steps {
                        sh '''
                            python -m flake8 app.py --max-line-length=88
                            python -m black --check app.py
                        '''
                    }
                }
                
                stage('Security Scan') {
                    steps {
                        sh '''
                            python -m bandit -r . -f json -o bandit-report.json
                        '''
                        publishHTML([
                            allowMissing: false,
                            alwaysLinkToLastBuild: true,
                            keepAll: true,
                            reportDir: '.',
                            reportFiles: 'bandit-report.json',
                            reportName: 'Security Report'
                        ])
                    }
                }
            }
        }
        
        stage('Test') {
            steps {
                sh '''
                    python -m pytest tests/ --junitxml=test-results.xml --cov=app --cov-report=xml
                '''
                publishTestResults testResultsPattern: 'test-results.xml'
                publishCoverage adapters: [coberturaAdapter('coverage.xml')], sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    def image = docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                    docker.withRegistry("https://${REGISTRY_URL}", 'registry-credentials') {
                        image.push()
                        image.push('latest')
                    }
                }
            }
        }
        
        stage('Deploy to Staging') {
            steps {
                script {
                    sshagent(['deploy-key']) {
                        sh """
                            ssh -o StrictHostKeyChecking=no ubuntu@${DEPLOY_SERVER} '
                                docker pull ${REGISTRY_URL}/${DOCKER_IMAGE}:${DOCKER_TAG}
                                docker stop qr-attendance-staging || true
                                docker rm qr-attendance-staging || true
                                docker run -d --name qr-attendance-staging \
                                    -p 5001:5000 \
                                    -v /opt/qr-data-staging:/app/data \
                                    -v /opt/qr-codes-staging:/app/qr_codes \
                                    ${REGISTRY_URL}/${DOCKER_IMAGE}:${DOCKER_TAG}
                            '
                        """
                    }
                }
            }
        }
        
        stage('Integration Tests') {
            steps {
                sh '''
                    sleep 30  # Wait for application to start
                    python -m pytest integration_tests/ --base-url=http://${DEPLOY_SERVER}:5001
                '''
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                input message: 'Deploy to production?', ok: 'Deploy'
                script {
                    sshagent(['deploy-key']) {
                        sh """
                            ssh -o StrictHostKeyChecking=no ubuntu@${DEPLOY_SERVER} '
                                # Blue-green deployment
                                docker pull ${REGISTRY_URL}/${DOCKER_IMAGE}:${DOCKER_TAG}
                                
                                # Start new container
                                docker run -d --name qr-attendance-green \
                                    -p 5002:5000 \
                                    -v /opt/qr-data:/app/data \
                                    -v /opt/qr-codes:/app/qr_codes \
                                    ${REGISTRY_URL}/${DOCKER_IMAGE}:${DOCKER_TAG}
                                
                                # Health check
                                sleep 30
                                curl -f http://localhost:5002/ || exit 1
                                
                                # Switch traffic
                                docker stop qr-attendance-blue || true
                                docker rename qr-attendance-prod qr-attendance-blue || true
                                docker rename qr-attendance-green qr-attendance-prod
                                
                                # Update port mapping
                                docker stop qr-attendance-prod
                                docker rm qr-attendance-prod
                                docker run -d --name qr-attendance-prod \
                                    -p 5000:5000 \
                                    -v /opt/qr-data:/app/data \
                                    -v /opt/qr-codes:/app/qr_codes \
                                    ${REGISTRY_URL}/${DOCKER_IMAGE}:${DOCKER_TAG}
                                
                                # Cleanup old container
                                docker rm qr-attendance-blue || true
                            '
                        """
                    }
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            slackSend(
                channel: '#deployments',
                color: 'good',
                message: "✅ QR Attendance System deployed successfully - Build #${BUILD_NUMBER}"
            )
        }
        failure {
            slackSend(
                channel: '#deployments',
                color: 'danger',
                message: "❌ QR Attendance System deployment failed - Build #${BUILD_NUMBER}"
            )
        }
    }
}
```

### Jenkins Configuration

#### Required Plugins
```bash
# Install Jenkins plugins
jenkins-cli install-plugin docker-workflow
jenkins-cli install-plugin pipeline-stage-view
jenkins-cli install-plugin blueocean
jenkins-cli install-plugin slack
jenkins-cli install-plugin ssh-agent
jenkins-cli install-plugin junit
jenkins-cli install-plugin coverage
jenkins-cli install-plugin htmlpublisher
```

#### Webhook Configuration
```bash
# GitHub webhook URL
http://your-jenkins-server/github-webhook/

# Webhook events
- Push events
- Pull request events
- Release events
```

## ☁️ AWS EC2 Deployment

### EC2 Instance Setup

#### Instance Configuration
```bash
# Launch EC2 instance
aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --instance-type t3.medium \
    --key-name your-key-pair \
    --security-group-ids sg-xxxxxxxxx \
    --subnet-id subnet-xxxxxxxxx \
    --user-data file://user-data.sh \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=QR-Attendance-Server}]'
```

#### User Data Script
```bash
#!/bin/bash
# user-data.sh

# Update system
yum update -y

# Install Docker
amazon-linux-extras install docker -y
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Git
yum install git -y

# Create application directory
mkdir -p /opt/qr-attendance
cd /opt/qr-attendance

# Clone repository
git clone https://github.com/your-username/qr-attendance-system.git .

# Create data directories
mkdir -p /opt/qr-data /opt/qr-codes /opt/logs

# Set permissions
chown -R ec2-user:ec2-user /opt/qr-attendance /opt/qr-data /opt/qr-codes /opt/logs

# Start application
docker-compose up -d

# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
rpm -U ./amazon-cloudwatch-agent.rpm
```

### Security Group Configuration
```bash
# Create security group
aws ec2 create-security-group \
    --group-name qr-attendance-sg \
    --description "Security group for QR Attendance System"

# Allow HTTP traffic
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxxx \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

# Allow HTTPS traffic
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxxx \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# Allow SSH access
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxxx \
    --protocol tcp \
    --port 22 \
    --cidr your-ip/32

# Allow application port
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxxx \
    --protocol tcp \
    --port 5000 \
    --cidr 0.0.0.0/0
```

### Load Balancer Setup

#### Application Load Balancer
```bash
# Create load balancer
aws elbv2 create-load-balancer \
    --name qr-attendance-alb \
    --subnets subnet-xxxxxxxx subnet-yyyyyyyy \
    --security-groups sg-xxxxxxxxx

# Create target group
aws elbv2 create-target-group \
    --name qr-attendance-targets \
    --protocol HTTP \
    --port 5000 \
    --vpc-id vpc-xxxxxxxxx \
    --health-check-path /

# Register targets
aws elbv2 register-targets \
    --target-group-arn arn:aws:elasticloadbalancing:region:account:targetgroup/qr-attendance-targets/xxxxxxxxx \
    --targets Id=i-xxxxxxxxx,Port=5000

# Create listener
aws elbv2 create-listener \
    --load-balancer-arn arn:aws:elasticloadbalancing:region:account:loadbalancer/app/qr-attendance-alb/xxxxxxxxx \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:region:account:targetgroup/qr-attendance-targets/xxxxxxxxx
```

### Auto Scaling Configuration

#### Launch Template
```bash
# Create launch template
aws ec2 create-launch-template \
    --launch-template-name qr-attendance-template \
    --launch-template-data '{
        "ImageId": "ami-0c02fb55956c7d316",
        "InstanceType": "t3.medium",
        "KeyName": "your-key-pair",
        "SecurityGroupIds": ["sg-xxxxxxxxx"],
        "UserData": "'$(base64 -w 0 user-data.sh)'",
        "IamInstanceProfile": {
            "Name": "EC2-CloudWatch-Role"
        },
        "TagSpecifications": [{
            "ResourceType": "instance",
            "Tags": [{"Key": "Name", "Value": "QR-Attendance-Auto"}]
        }]
    }'
```

#### Auto Scaling Group
```bash
# Create auto scaling group
aws autoscaling create-auto-scaling-group \
    --auto-scaling-group-name qr-attendance-asg \
    --launch-template LaunchTemplateName=qr-attendance-template,Version=1 \
    --min-size 1 \
    --max-size 3 \
    --desired-capacity 2 \
    --target-group-arns arn:aws:elasticloadbalancing:region:account:targetgroup/qr-attendance-targets/xxxxxxxxx \
    --vpc-zone-identifier "subnet-xxxxxxxx,subnet-yyyyyyyy"

# Create scaling policies
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name qr-attendance-asg \
    --policy-name scale-up \
    --policy-type TargetTrackingScaling \
    --target-tracking-configuration '{
        "TargetValue": 70.0,
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "ASGAverageCPUUtilization"
        }
    }'
```

### SSL/TLS Configuration

#### Certificate Manager
```bash
# Request SSL certificate
aws acm request-certificate \
    --domain-name qr-attendance.yourdomain.com \
    --validation-method DNS \
    --subject-alternative-names "*.yourdomain.com"

# Update load balancer listener for HTTPS
aws elbv2 create-listener \
    --load-balancer-arn arn:aws:elasticloadbalancing:region:account:loadbalancer/app/qr-attendance-alb/xxxxxxxxx \
    --protocol HTTPS \
    --port 443 \
    --certificates CertificateArn=arn:aws:acm:region:account:certificate/xxxxxxxxx \
    --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:region:account:targetgroup/qr-attendance-targets/xxxxxxxxx
```

### Monitoring & Logging

#### CloudWatch Configuration
```json
{
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/opt/logs/app.log",
                        "log_group_name": "/aws/ec2/qr-attendance/app",
                        "log_stream_name": "{instance_id}"
                    },
                    {
                        "file_path": "/var/log/docker",
                        "log_group_name": "/aws/ec2/qr-attendance/docker",
                        "log_stream_name": "{instance_id}"
                    }
                ]
            }
        }
    },
    "metrics": {
        "namespace": "QR-Attendance/Application",
        "metrics_collected": {
            "cpu": {
                "measurement": ["cpu_usage_idle", "cpu_usage_iowait"],
                "metrics_collection_interval": 60
            },
            "disk": {
                "measurement": ["used_percent"],
                "metrics_collection_interval": 60,
                "resources": ["*"]
            },
            "mem": {
                "measurement": ["mem_used_percent"],
                "metrics_collection_interval": 60
            }
        }
    }
}
```

## 📊 Git & GitHub Workflow

### Repository Structure

#### Branch Strategy
```
main (production)
├── develop (integration)
├── feature/qr-generation
├── feature/attendance-tracking
├── feature/ui-improvements
├── hotfix/security-patch
└── release/v1.0.0
```

#### Git Configuration
```bash
# Initialize repository
git init
git remote add origin https://github.com/username/qr-attendance-system.git

# Set up branch protection
gh api repos/username/qr-attendance-system/branches/main/protection \
    --method PUT \
    --field required_status_checks='{"strict":true,"contexts":["ci/jenkins"]}' \
    --field enforce_admins=true \
    --field required_pull_request_reviews='{"required_approving_review_count":2}' \
    --field restrictions=null
```

### Workflow Configuration

#### GitHub Actions
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest flake8 black bandit
    
    - name: Lint with flake8
      run: |
        flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 app.py --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Format check with black
      run: black --check app.py
    
    - name: Security check with bandit
      run: bandit -r . -f json -o bandit-report.json
    
    - name: Test with pytest
      run: pytest tests/ --junitxml=junit/test-results.xml --cov=app --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  build:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: docker build -t qr-attendance:${{ github.sha }} .
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'qr-attendance:${{ github.sha }}'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'

  deploy:
    needs: [test, build]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to AWS
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      run: |
        # Deploy using AWS CLI or Terraform
        aws ecs update-service --cluster qr-attendance --service qr-app --force-new-deployment
```

### Git Hooks

#### Pre-commit Hook
```bash
#!/bin/sh
# .git/hooks/pre-commit

# Run tests
python -m pytest tests/ --quiet

# Check code formatting
python -m black --check app.py

# Security scan
python -m bandit -r . -q

# If any command fails, prevent commit
if [ $? -ne 0 ]; then
    echo "Pre-commit checks failed. Please fix issues before committing."
    exit 1
fi
```

#### Pre-push Hook
```bash
#!/bin/sh
# .git/hooks/pre-push

# Run full test suite
python -m pytest tests/ --cov=app --cov-fail-under=80

# Build Docker image to ensure it works
docker build -t qr-attendance:test .

if [ $? -ne 0 ]; then
    echo "Pre-push checks failed. Please fix issues before pushing."
    exit 1
fi
```

### Release Management

#### Semantic Versioning
```bash
# Version tagging
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Changelog generation
git log --oneline --decorate --graph > CHANGELOG.md
```

#### Release Workflow
```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Create Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref }}
        release_name: Release ${{ github.ref }}
        draft: false
        prerelease: false
    
    - name: Build and push Docker image
      env:
        DOCKER_REGISTRY: ${{ secrets.DOCKER_REGISTRY }}
        DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
        DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
      run: |
        echo $DOCKER_PASSWORD | docker login $DOCKER_REGISTRY -u $DOCKER_USERNAME --password-stdin
        docker build -t $DOCKER_REGISTRY/qr-attendance:${{ github.ref_name }} .
        docker push $DOCKER_REGISTRY/qr-attendance:${{ github.ref_name }}
```

## 🔧 Additional Technologies & Tools

### Monitoring & Observability

#### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'qr-attendance'
    static_configs:
      - targets: ['localhost:5000']
    metrics_path: /metrics
    scrape_interval: 5s
```

#### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "QR Attendance System",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(flask_http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "flask_http_request_duration_seconds",
            "legendFormat": "{{quantile}}"
          }
        ]
      }
    ]
  }
}
```

### Testing Framework

#### Unit Tests
```python
# tests/test_app.py
import pytest
import json
from app import app, init_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DATABASE'] = ':memory:'
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client

def test_register_student(client):
    """Test student registration"""
    response = client.post('/register', 
        data=json.dumps({
            'roll_no': '12345',
            'name': 'John Doe'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'qr_code' in data

def test_duplicate_registration(client):
    """Test duplicate roll number registration"""
    # First registration
    client.post('/register', 
        data=json.dumps({
            'roll_no': '12345',
            'name': 'John Doe'
        }),
        content_type='application/json'
    )
    
    # Duplicate registration
    response = client.post('/register', 
        data=json.dumps({
            'roll_no': '12345',
            'name': 'Jane Doe'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 409
    data = json.loads(response.data)
    assert data['success'] == False
    assert 'already exists' in data['error']

def test_scan_qr(client):
    """Test QR code scanning"""
    # Register student first
    client.post('/register', 
        data=json.dumps({
            'roll_no': '12345',
            'name': 'John Doe'
        }),
        content_type='application/json'
    )
    
    # Scan QR code
    response = client.post('/scan', 
        data=json.dumps({
            'roll_no': '12345',
            'subject_id': 'DBMS'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['student']['roll_no'] == '12345'
```

#### Integration Tests
```python
# tests/test_integration.py
import requests
import pytest

class TestIntegration:
    base_url = "http://localhost:5000"
    
    def test_full_workflow(self):
        """Test complete registration and scanning workflow"""
        # Register student
        register_response = requests.post(
            f"{self.base_url}/register",
            json={
                'roll_no': 'INT001',
                'name': 'Integration Test Student'
            }
        )
        
        assert register_response.status_code == 200
        register_data = register_response.json()
        assert register_data['success'] == True
        
        # Scan QR code
        scan_response = requests.post(
            f"{self.base_url}/scan",
            json={
                'roll_no': 'INT001',
                'subject_id': 'DBMS'
            }
        )
        
        assert scan_response.status_code == 200
        scan_data = scan_response.json()
        assert scan_data['success'] == True
        assert scan_data['student']['name'] == 'Integration Test Student'
```

### Performance Testing

#### Load Testing with Locust
```python
# locustfile.py
from locust import HttpUser, task, between

class QRAttendanceUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Register a student for testing"""
        self.roll_no = f"LOAD{self.environment.runner.user_count}"
        self.client.post("/register", json={
            'roll_no': self.roll_no,
            'name': f'Load Test User {self.roll_no}'
        })
    
    @task(3)
    def scan_qr(self):
        """Simulate QR code scanning"""
        self.client.post("/scan", json={
            'roll_no': self.roll_no,
            'subject_id': 'DBMS'
        })
    
    @task(1)
    def register_student(self):
        """Simulate new student registration"""
        import random
        roll_no = f"NEW{random.randint(1000, 9999)}"
        self.client.post("/register", json={
            'roll_no': roll_no,
            'name': f'New Student {roll_no}'
        })
```

### Security Implementation

#### Security Headers
```python
# Security middleware
from flask import Flask
from flask_talisman import Talisman

app = Flask(__name__)

# Configure security headers
Talisman(app, {
    'force_https': True,
    'strict_transport_security': True,
    'content_security_policy': {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline'",
        'style-src': "'self' 'unsafe-inline'",
        'img-src': "'self' data:",
        'media-src': "'self'"
    }
})

@app.before_request
def security_headers():
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
```

#### Input Validation
```python
from flask_wtf import FlaskForm
from wtforms import StringField, validators
from wtforms.validators import DataRequired, Length, Regexp

class StudentRegistrationForm(FlaskForm):
    roll_no = StringField('Roll Number', [
        DataRequired(),
        Length(min=3, max=20),
        Regexp(r'^[A-Za-z0-9]+$', message="Roll number must contain only letters and numbers")
    ])
    
    name = StringField('Student Name', [
        DataRequired(),
        Length(min=2, max=100),
        Regexp(r'^[A-Za-z\s]+$', message="Name must contain only letters and spaces")
    ])

def validate_input(data):
    """Server-side input validation"""
    form = StudentRegistrationForm(data=data)
    if not form.validate():
        return False, form.errors
    return True, None
```

This comprehensive documentation covers all aspects of the Student QR Attendance System, from frontend implementation to production deployment, providing a complete technical reference for development, deployment, and maintenance.