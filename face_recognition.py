
import csv
from datetime import datetime
import cv2
import os
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "student_faces"
CSV_FILE = BASE_DIR / "students.csv"
ATTENDANCE_FILE = BASE_DIR / "attendance.csv"

# Load registered students
students = {}

if not CSV_FILE.exists():
    print("students.csv file kidaikkala!")
    raise SystemExit

with open(CSV_FILE, "r", newline="", encoding="utf-8") as file:
    for row in csv.DictReader(file):
        students[row["student_id"]] = row["student_name"]

if not students:
    print("Registered students yaarum illai!")
    raise SystemExit

# Prepare training images
training_images = []
training_labels = []
label_to_student = {}
label_number = 0

for student_id, student_name in students.items():
    folder = DATA_DIR / student_id

    if not folder.exists():
        continue

    student_images = []

    for image_path in folder.glob("*.jpg"):
        image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

        if image is not None:
            image = cv2.resize(image, (200, 200))
            student_images.append(image)

    if student_images:
        label_to_student[label_number] = (student_id, student_name)

        for image in student_images:
            training_images.append(image)
            training_labels.append(label_number)

        label_number += 1

if not training_images:
    print("Training images kidaikkala!")
    print("student_faces folder-ai check pannunga.")
    raise SystemExit

# Train face recognition model
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.train(
    training_images,
    np.array(training_labels, dtype="int32")
)

print("Face recognition model ready!")
print("Registered students:", len(label_to_student))

# Attendance marking function
def mark_attendance(student_id, student_name):
    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")

    # Check if attendance already exists for today
    if ATTENDANCE_FILE.exists():
        with open(
            ATTENDANCE_FILE, "r", newline="", encoding="utf-8"
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                if (
                    row.get("student_id") == student_id
                    and row.get("date") == today
                ):
                    return "Already Marked"

    # Save attendance
    file_exists = ATTENDANCE_FILE.exists()
    needs_header = (
        not file_exists or ATTENDANCE_FILE.stat().st_size == 0
    )

    with open(
        ATTENDANCE_FILE, "a", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)

        if needs_header:
            writer.writerow(
                ["student_id", "student_name", "date", "time", "status"]
            )

        writer.writerow(
            [student_id, student_name, today, current_time, "Present"]
        )

    print(f"Attendance marked: {student_name} ({student_id})")
    return "Present"


# Face detector
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades
    + "haarcascade_frontalface_default.xml"
)

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Webcam open aagala!")
    raise SystemExit

# Prevent attendance checking on every camera frame
last_seen = {}
attendance_status = {}

print("Camera open aagiduchu. Exit panna Q press pannunga.")

try:
    while True:
        success, frame = camera.read()

        if not success:
            print("Camera frame read panna mudiyala!")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(80, 80)
        )

        for (x, y, w, h) in faces:
            face_image = gray[y:y + h, x:x + w]
            face_image = cv2.resize(face_image, (200, 200))

            label, confidence = recognizer.predict(face_image)

            if label in label_to_student and confidence < 65:
                student_id, student_name = label_to_student[label]

                # Mark attendance once per student per day
                if student_id not in attendance_status:
                    status = mark_attendance(student_id, student_name)
                    attendance_status[student_id] = status

                status = attendance_status[student_id]
                message = f"{student_name} ({student_id})"
                color = (0, 255, 0)

                cv2.putText(
                    frame, status, (x, min(y + h + 25, frame.shape[0] - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2
                )
            else:
                message = "Unknown"
                color = (0, 0, 255)

            cv2.rectangle(
                frame, (x, y), (x + w, y + h), color, 2
            )

            cv2.putText(
                frame, message, (x, max(y - 10, 25)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2
            )

        cv2.imshow("Smart Attendance - Face Recognition", frame)

        if cv2.waitKey(10) & 0xFF == ord("q"):
            break

finally:
    camera.release()
    cv2.destroyAllWindows()

