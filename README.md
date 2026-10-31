
# AI-Powered Smart Attendance Management System Using Face Recognition

## 📌 Project Overview

The AI-Powered Smart Attendance Management System is a Python-based desktop application that automates student attendance using face recognition technology.

The system captures student face images during registration, recognizes registered students through a webcam, and automatically records their attendance.

It provides a simple graphical user interface (GUI) to manage student registration, attendance tracking, daily reports, and attendance percentage calculation.

## 🎯 Objectives

- Automate the traditional manual attendance process.
- Identify registered students using face recognition.
- Reduce duplicate attendance entries.
- Maintain student and attendance records.
- Generate daily attendance reports.
- Calculate student attendance percentages.

## ✨ Features

### 1. Student Registration
- Register students using Student ID and Student Name.
- Capture five face images through a webcam.
- Store captured face images in individual student folders.
- Save student details in a CSV file.
- Display a registration success confirmation.

### 2. Face Recognition
- Detect faces using OpenCV Haar Cascade.
- Recognize registered students using the LBPH face recognition algorithm.
- Display recognized student details.
- Identify unknown faces.

### 3. Automatic Attendance
- Automatically mark attendance when a registered student is recognized.
- Store attendance date and time.
- Prevent duplicate attendance entries on the same day.

### 4. Daily Attendance Report
- Display the daily attendance records.
- Show Student ID, Student Name, Date, Time, and Attendance Status.

### 5. Attendance Percentage
- Calculate the number of present days.
- Calculate the number of absent days based on the entered working days.
- Display the attendance percentage for each student.

### 6. GUI Dashboard
- Single-window desktop application.
- Easy navigation between all modules.
- User-friendly interface using Tkinter.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| OpenCV | Image processing and face detection |
| Haar Cascade | Face detection |
| LBPH | Face recognition |
| Tkinter | Graphical User Interface |
| NumPy | Image and numerical processing |
| Pillow | Displaying webcam images in GUI |
| CSV | Storing student and attendance records |

## 📂 Project Structure

SmartAttendanceAI/
│
├── dashboard.py
├── face_detection.py
├── face_recognition.py
├── student_registration.py
├── attendance_report.py
├── attendance_percentage.py
├── students.csv
├── attendance.csv
│
├── student_faces/
│   ├── student_id_1/
│   │   ├── face_1.jpg
│   │   ├── face_2.jpg
│   │   └── ...
│   │
│   └── student_id_2/
│
├── requirements.txt
└── README.md

## ⚙️ Installation and Setup

### Step 1: Clone the Repository

git clone YOUR_GITHUB_REPOSITORY_URL

### Step 2: Open the Project Folder

cd SmartAttendanceAI

### Step 3: Create a Virtual Environment

python -m venv .venv

### Step 4: Activate Virtual Environment

Windows:

.venv\Scripts\activate

### Step 5: Install Dependencies

python -m pip install opencv-contrib-python numpy pillow

### Step 6: Run the Application

python dashboard.py

## 💻 System Requirements

- Operating System: Windows 10 / Windows 11
- Programming Language: Python 3
- Webcam: Required
- RAM: 4 GB or above recommended
- Code Editor: Visual Studio Code

## 🔄 System Workflow

1. Launch the application.
2. Register a student using Student ID and Name.
3. Capture five face images using the webcam.
4. Store student information and face images.
5. Start face recognition.
6. Recognize registered students through the webcam.
7. Automatically record attendance.
8. View daily attendance reports.
9. Calculate attendance percentages.

## 📊 Attendance Calculation

Attendance Percentage =

(Present Days / Total Working Days) × 100

## 🔮 Future Enhancements

- MySQL or SQLite database integration.
- Secure administrator login.
- Excel and PDF report generation.
- Monthly attendance analytics.
- Low attendance notifications.
- Face liveness detection to reduce photo-based impersonation.

## 👩‍💻 Developer

**Kiruthiga R**

MCA Student

GitHub: https://github.com/Kiruthigakiruthiga18

## 📌 Project Status

Completed - Working Prototype

This project was developed as a practical implementation of Python programming, computer vision, face recognition, and desktop application development.
