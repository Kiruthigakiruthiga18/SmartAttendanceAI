
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import datetime, date
import csv
import cv2
import numpy as np
from PIL import Image, ImageTk

# ---------------- CONFIGURATION ----------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "student_faces"
STUDENTS_FILE = BASE_DIR / "students.csv"
ATTENDANCE_FILE = BASE_DIR / "attendance.csv"

DATA_DIR.mkdir(exist_ok=True)

BG = "#eef2f7"
BLUE = "#1f3a5f"
ACCENT = "#2874a6"

CASCADE_FILE = (
    cv2.data.haarcascades
    + "haarcascade_frontalface_default.xml"
)
face_cascade = cv2.CascadeClassifier(CASCADE_FILE)

camera = None
camera_job = None
current_page = None

# ---------------- CSV HELPERS ----------------

def load_students():
    students = {}

    if STUDENTS_FILE.exists():
        with open(STUDENTS_FILE, "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            for row in reader:
                sid = row.get("student_id", "").strip()
                name = row.get("student_name", "").strip()

                if sid and name:
                    students[sid] = name

    return students


def load_attendance():
    records = []

    if ATTENDANCE_FILE.exists():
        with open(ATTENDANCE_FILE, "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            records = list(reader)

    return records


def ensure_csv_files():
    if not STUDENTS_FILE.exists() or STUDENTS_FILE.stat().st_size == 0:
        with open(STUDENTS_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["student_id", "student_name"])

    if not ATTENDANCE_FILE.exists() or ATTENDANCE_FILE.stat().st_size == 0:
        with open(ATTENDANCE_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["student_id", "student_name", "date", "time", "status"])


ensure_csv_files()


# ---------------- WINDOW SETUP ----------------

root = tk.Tk()
root.title("AI Smart Attendance Management System")
root.geometry("1000x700")
root.minsize(850, 600)
root.configure(bg=BG)

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", rowheight=28, font=("Arial", 10))
style.configure("Treeview.Heading", font=("Arial", 10, "bold"))


def stop_camera():
    global camera, camera_job

    if camera_job is not None:
        try:
            root.after_cancel(camera_job)
        except tk.TclError:
            pass
        camera_job = None

    if camera is not None:
        camera.release()
        camera = None


def clear_page():
    global current_page

    stop_camera()

    if current_page is not None:
        current_page.destroy()

    current_page = tk.Frame(root, bg=BG)
    current_page.pack(fill="both", expand=True)


def make_header(title):
    header = tk.Frame(current_page, bg=BLUE, height=70)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(
        header,
        text=title,
        font=("Arial", 20, "bold"),
        fg="white",
        bg=BLUE
    ).pack(pady=18)


def back_button():
    tk.Button(
        current_page,
        text="← Back to Dashboard",
        command=show_dashboard,
        bg="#d9e2ec",
        fg=BLUE,
        font=("Arial", 10, "bold"),
        padx=12,
        pady=7,
        relief="flat"
    ).pack(pady=10)


# ---------------- DASHBOARD ----------------

def show_dashboard():
    clear_page()
    make_header("AI-Powered Smart Attendance System")

    tk.Label(
        current_page,
        text="Face Recognition Attendance Management",
        font=("Arial", 14),
        bg=BG,
        fg=BLUE
    ).pack(pady=15)

    menu = tk.Frame(current_page, bg=BG)
    menu.pack(pady=20)

    options = [
        ("Register Student", show_registration),
        ("Mark Attendance", show_recognition),
        ("Daily Attendance Report", show_report),
        ("Attendance Percentage", show_percentage),
    ]

    for text, command in options:
        tk.Button(
            menu,
            text=text,
            command=command,
            width=28,
            height=2,
            bg=ACCENT,
            fg="white",
            activebackground=BLUE,
            activeforeground="white",
            font=("Arial", 12, "bold"),
            relief="flat",
            cursor="hand2"
        ).pack(pady=10)

    students = load_students()

    tk.Label(
        current_page,
        text=f"Registered Students: {len(students)}",
        font=("Arial", 12, "bold"),
        bg=BG,
        fg=BLUE
    ).pack(pady=10)

    tk.Label(
        current_page,
        text="Project: AI-Powered Smart Attendance Management System",
        font=("Arial", 9),
        bg=BG,
        fg="gray"
    ).pack(side="bottom", pady=12)


# ---------------- STUDENT REGISTRATION ----------------

def show_registration():
    global camera, camera_job

    clear_page()
    make_header("Student Registration")

    form = tk.Frame(current_page, bg=BG)
    form.pack(pady=10)

    tk.Label(
        form, text="Student ID:", bg=BG,
        font=("Arial", 11, "bold")
    ).grid(row=0, column=0, padx=8, pady=8, sticky="e")

    id_entry = tk.Entry(form, font=("Arial", 11), width=25)
    id_entry.grid(row=0, column=1, padx=8, pady=8)

    tk.Label(
        form, text="Student Name:", bg=BG,
        font=("Arial", 11, "bold")
    ).grid(row=1, column=0, padx=8, pady=8, sticky="e")

    name_entry = tk.Entry(form, font=("Arial", 11), width=25)
    name_entry.grid(row=1, column=1, padx=8, pady=8)

    video_label = tk.Label(
        current_page,
        text="Camera preview will appear here",
        bg="#d9e2ec",
        width=60,
        height=12
    )
    video_label.pack(pady=10)

    status_label = tk.Label(
        current_page,
        text="Enter student details and start registration.",
        bg=BG,
        fg=BLUE,
        font=("Arial", 11)
    )
    status_label.pack(pady=5)

    count_label = tk.Label(
        current_page,
        text="Face images captured: 0/5",
        bg=BG,
        font=("Arial", 10, "bold")
    )
    count_label.pack(pady=5)

    capture_state = {
        "student_id": "",
        "student_name": "",
        "folder": None,
        "count": 0,
        "last_capture": 0.0,
        "finished": False
    }

    start_button = tk.Button(
        current_page,
        text="Start Registration",
        bg=ACCENT,
        fg="white",
        font=("Arial", 11, "bold"),
        padx=18,
        pady=8,
        relief="flat"
    )
    start_button.pack(pady=8)

    def finish_registration():
        global camera, camera_job

        if capture_state["finished"]:
            return

        capture_state["finished"] = True
        stop_camera()

        try:
            with open(
                STUDENTS_FILE, "a",
                newline="", encoding="utf-8"
            ) as file:
                writer = csv.writer(file)
                writer.writerow([
                    capture_state["student_id"],
                    capture_state["student_name"]
                ])

            status_label.config(
                text="Registration completed successfully!",
                fg="green"
            )

            messagebox.showinfo(
                "Registration Successful!",
                "Registration Successful!\n\n"
                f"Student ID: {capture_state['student_id']}\n"
                f"Student Name: {capture_state['student_name']}\n"
                f"Face Images: {capture_state['count']} saved successfully!"
            )

            show_dashboard()

        except Exception as error:
            messagebox.showerror(
                "Registration Error",
                f"Unable to save student details.\n{error}"
            )

    def update_registration_camera():
        global camera_job

        if capture_state["finished"] or camera is None:
            return

        success, frame = camera.read()

        if not success:
            status_label.config(
                text="Cannot read camera. Please check webcam.",
                fg="red"
            )
            camera_job = root.after(100, update_registration_camera)
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(80, 80)
        )

        # Draw rectangle around detected faces.
        largest_face = None

        for (x, y, w, h) in faces:
            cv2.rectangle(
                frame, (x, y), (x + w, y + h),
                (0, 255, 0), 2
            )

            if largest_face is None or w * h > largest_face[2] * largest_face[3]:
                largest_face = (x, y, w, h)

        # Capture one image every 1.5 seconds using the SAME frame.
        if largest_face is not None and capture_state["count"] < 5:
            now = datetime.now().timestamp()

            if now - capture_state["last_capture"] >= 1.5:
                x, y, w, h = largest_face
                face_img = gray[y:y+h, x:x+w]
                face_img = cv2.resize(face_img, (200, 200))

                next_number = capture_state["count"] + 1
                image_path = (
                    capture_state["folder"]
                    / f"face_{next_number}.jpg"
                )

                if cv2.imwrite(str(image_path), face_img):
                    capture_state["count"] = next_number
                    capture_state["last_capture"] = now

                    count_label.config(
                        text=(
                            "Face images captured: "
                            f"{capture_state['count']}/5"
                        )
                    )

                    status_label.config(
                        text="Face detected. Capturing images...",
                        fg=BLUE
                    )

                    if capture_state["count"] == 5:
                        finish_registration()
                        return
        elif largest_face is None:
            status_label.config(
                text="Face not detected. Look at the camera.",
                fg="red"
            )

        # Display camera preview.
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb_frame)
        image.thumbnail((600, 350))

        photo = ImageTk.PhotoImage(image=image)
        video_label.configure(image=photo, text="")
        video_label.image = photo

        camera_job = root.after(30, update_registration_camera)

    def start_registration():
        global camera

        student_id = id_entry.get().strip()
        student_name = name_entry.get().strip()

        if not student_id or not student_name:
            messagebox.showwarning(
                "Missing Details",
                "Please enter both Student ID and Student Name."
            )
            return

        if any(char in student_id for char in r'\/:*?"<>|'):
            messagebox.showwarning(
                "Invalid Student ID",
                "Student ID contains invalid characters."
            )
            return

        if student_id in load_students():
            messagebox.showwarning(
                "Duplicate Student ID",
                "This Student ID is already registered."
            )
            return

        folder = DATA_DIR / student_id

        if folder.exists() and any(folder.iterdir()):
            messagebox.showwarning(
                "Existing Face Images",
                "A folder with face images already exists for this ID.\n"
                "Use another Student ID or check the existing folder."
            )
            return

        folder.mkdir(parents=True, exist_ok=True)

        camera = cv2.VideoCapture(0)

        if not camera.isOpened():
            camera.release()
            camera = None

            messagebox.showerror(
                "Camera Error",
                "Unable to open webcam.\n"
                "Close other camera apps and try again."
            )
            return

        capture_state["student_id"] = student_id
        capture_state["student_name"] = student_name
        capture_state["folder"] = folder
        capture_state["count"] = 0
        capture_state["last_capture"] = 0.0
        capture_state["finished"] = False

        id_entry.config(state="disabled")
        name_entry.config(state="disabled")
        start_button.config(state="disabled")

        status_label.config(
            text="Camera started. Look straight at the camera.",
            fg=BLUE
        )

        update_registration_camera()

    start_button.config(command=start_registration)
    back_button()


# ---------------- FACE RECOGNITION ----------------

def prepare_recognizer():
    if not hasattr(cv2, "face"):
        messagebox.showerror(
            "OpenCV Error",
            "LBPH recognizer is unavailable.\n"
            "Install opencv-contrib-python in your virtual environment."
        )
        return None

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces_list = []
    labels_list = []
    label_to_student = {}
    label_number = 0

    for student_id, student_name in load_students().items():
        folder = DATA_DIR / student_id

        if not folder.exists():
            continue

        student_images = []

        for image_path in folder.glob("*.jpg"):
            image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

            if image is not None:
                student_images.append(image)

        if student_images:
            label_to_student[label_number] = (
                student_id, student_name
            )

            for image in student_images:
                faces_list.append(image)
                labels_list.append(label_number)

            label_number += 1

    if not faces_list:
        messagebox.showwarning(
            "No Face Data",
            "Please register at least one student first."
        )
        return None

    recognizer.train(
        faces_list,
        np.array(labels_list, dtype=np.int32)
    )

    return recognizer, label_to_student


def mark_attendance(student_id, student_name):
    today = date.today().isoformat()
    records = load_attendance()

    for row in records:
        if (
            row.get("student_id") == student_id
            and row.get("date") == today
        ):
            return False

    with open(
        ATTENDANCE_FILE, "a",
        newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow([
            student_id,
            student_name,
            today,
            datetime.now().strftime("%H:%M:%S"),
            "Present"
        ])

    return True


def show_recognition():
    global camera, camera_job

    clear_page()
    make_header("Face Recognition Attendance")

    video_label = tk.Label(
        current_page, bg="#d9e2ec",
        text="Camera preview"
    )
    video_label.pack(pady=15)

    status_label = tk.Label(
        current_page,
        text="Preparing face recognition...",
        bg=BG, fg=BLUE,
        font=("Arial", 12, "bold")
    )
    status_label.pack(pady=8)

    model = prepare_recognizer()

    if model is None:
        back_button()
        return

    recognizer, label_to_student = model

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        camera.release()
        camera = None

        messagebox.showerror(
            "Camera Error",
            "Unable to open webcam."
        )
        back_button()
        return

    status_label.config(
        text="Look at the camera to mark attendance."
    )

    recognized_today = set()

    def update_recognition_camera():
        global camera_job

        if camera is None:
            return

        success, frame = camera.read()

        if not success:
            camera_job = root.after(
                100, update_recognition_camera
            )
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(
            gray, 1.2, 5, minSize=(80, 80)
        )

        for (x, y, w, h) in faces:
            face_img = cv2.resize(
                gray[y:y+h, x:x+w], (200, 200)
            )

            label, confidence = recognizer.predict(face_img)

            if label in label_to_student and confidence < 75:
                student_id, student_name = label_to_student[label]

                cv2.putText(
                    frame,
                    student_name,
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (0, 255, 0), 2
                )

                cv2.rectangle(
                    frame, (x, y), (x+w, y+h),
                    (0, 255, 0), 2
                )

                if student_id not in recognized_today:
                    marked = mark_attendance(
                        student_id, student_name
                    )
                    recognized_today.add(student_id)

                    if marked:
                        status_label.config(
                            text=f"Attendance marked: {student_name}",
                            fg="green"
                        )
                    else:
                        status_label.config(
                            text=f"{student_name}: Already marked today",
                            fg=BLUE
                        )
            else:
                cv2.rectangle(
                    frame, (x, y), (x+w, y+h),
                    (0, 0, 255), 2
                )
                cv2.putText(
                    frame, "Unknown",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (0, 0, 255), 2
                )

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb)
        image.thumbnail((700, 420))
        photo = ImageTk.PhotoImage(image=image)

        video_label.configure(image=photo, text="")
        video_label.image = photo

        camera_job = root.after(
            30, update_recognition_camera
        )

    update_recognition_camera()
    back_button()


# ---------------- DAILY REPORT ----------------

def show_report():
    clear_page()
    make_header("Daily Attendance Report")

    today = date.today().isoformat()
    records = [
        row for row in load_attendance()
        if row.get("date") == today
    ]

    columns = ("student_id", "student_name", "date", "time", "status")

    table = ttk.Treeview(
        current_page, columns=columns, show="headings"
    )

    for col in columns:
        table.heading(col, text=col.replace("_", " ").title())
        table.column(col, width=160, anchor="center")

    table.pack(fill="both", expand=True, padx=20, pady=20)

    for row in records:
        table.insert(
            "", "end",
            values=tuple(row.get(col, "") for col in columns)
        )

    tk.Label(
        current_page,
        text=f"Date: {today} | Present: {len(records)}",
        bg=BG, fg=BLUE,
        font=("Arial", 12, "bold")
    ).pack(pady=5)

    back_button()


# ---------------- ATTENDANCE PERCENTAGE ----------------

def show_percentage():
    clear_page()
    make_header("Attendance Percentage")

    students = load_students()
    records = load_attendance()

    input_frame = tk.Frame(current_page, bg=BG)
    input_frame.pack(pady=15)

    tk.Label(
        input_frame,
        text="Total Working Days:",
        bg=BG,
        font=("Arial", 11, "bold")
    ).grid(row=0, column=0, padx=8, pady=8)

    days_entry = tk.Entry(input_frame, width=12, font=("Arial", 11))
    days_entry.grid(row=0, column=1, padx=8, pady=8)

    columns = (
        "student_id", "student_name",
        "present_days", "absent_days", "percentage"
    )

    table = ttk.Treeview(
        current_page, columns=columns, show="headings"
    )

    headings = {
        "student_id": "Student ID",
        "student_name": "Student Name",
        "present_days": "Present Days",
        "absent_days": "Absent Days",
        "percentage": "Attendance %"
    }

    for col in columns:
        table.heading(col, text=headings[col])
        table.column(col, width=170, anchor="center")

    table.pack(fill="both", expand=True, padx=20, pady=15)

    def calculate():
        try:
            working_days = int(days_entry.get())

            if working_days <= 0:
                raise ValueError

        except ValueError:
            messagebox.showwarning(
                "Invalid Input",
                "Enter total working days as a positive whole number."
            )
            return

        table.delete(*table.get_children())

        for student_id, student_name in students.items():
            present_days = len({
                row.get("date")
                for row in records
                if row.get("student_id") == student_id
                and row.get("status", "").lower() == "present"
            })

            present_days = min(present_days, working_days)
            absent_days = working_days - present_days
            percentage = present_days / working_days * 100

            table.insert(
                "", "end",
                values=(
                    student_id,
                    student_name,
                    present_days,
                    absent_days,
                    f"{percentage:.2f}%"
                )
            )

    tk.Button(
        input_frame,
        text="Calculate",
        command=calculate,
        bg=ACCENT,
        fg="white",
        font=("Arial", 10, "bold"),
        relief="flat",
        padx=12, pady=5
    ).grid(row=0, column=2, padx=8)

    back_button()


# ---------------- START APPLICATION ----------------

show_dashboard()


def close_application():
    stop_camera()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", close_application)
root.mainloop()
