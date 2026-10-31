
import cv2
import csv
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "student_faces"
CSV_FILE = BASE_DIR / "students.csv"

student_id = input("Enter Student ID: ").strip()
student_name = input("Enter Student Name: ").strip()

if not student_id or not student_name:
    print("Student ID and Name required!")
    raise SystemExit

# Allow only safe characters in folder name
if not all(c.isalnum() or c in "_-" for c in student_id):
    print("Student ID-la letters, numbers, _ or - mattum use pannunga.")
    raise SystemExit

if CSV_FILE.exists():
    with open(CSV_FILE, "r", newline="", encoding="utf-8") as file:
        for student in csv.DictReader(file):
            if student["student_id"].lower() == student_id.lower():
                print("Student ID already registered! Use a new ID.")
                raise SystemExit

student_folder = DATA_DIR / student_id

if student_folder.exists():
    print("Indha ID-ku folder already irukku. Pudhu ID use pannunga.")
    raise SystemExit

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

if face_cascade.empty():
    print("Face detection model load aagala!")
    raise SystemExit

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Webcam open aagala!")
    raise SystemExit

student_folder.mkdir(parents=True, exist_ok=True)

saved_count = 0
total_images = 2
last_save_time = 0

print("Face Registration Started!")
print("Camera-va paarunga. Face detect aana images automatic-ah save aagum.")
print("Exit panna Q press pannunga.")

try:
    while saved_count < total_images:
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

        largest_face = None

        if len(faces) > 0:
            largest_face = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = largest_face

            cv2.rectangle(
                frame, (x, y), (x + w, y + h), (0, 255, 0), 2
            )
            cv2.putText(
                frame, "Face Detected", (x, max(y - 10, 25)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
            )

            # Save one image every 2 seconds
            if time.time() - last_save_time >= 2:
                face_image = gray[y:y + h, x:x + w]
                next_number = saved_count + 1
                image_path = student_folder / f"face_{next_number}.jpg"

                if cv2.imwrite(str(image_path), face_image):
                    saved_count += 1
                    last_save_time = time.time()
                    print(f"Saved image {saved_count}/{total_images}")
                else:
                    print("Image save aagala!")

        cv2.putText(
            frame, f"Images: {saved_count}/{total_images}",
            (10, 35), cv2.FONT_HERSHEY_SIMPLEX,
            0.9, (255, 255, 0), 2
        )

        cv2.imshow("Student Face Registration", frame)

        # waitKey is still used for Q to exit
        key = cv2.waitKey(10) & 0xFF
        if key == ord("q"):
            break

finally:
    camera.release()
    cv2.destroyAllWindows()

if saved_count == total_images:
    file_exists = CSV_FILE.exists()

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file, fieldnames=["student_id", "student_name"]
        )
        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "student_id": student_id,
            "student_name": student_name
        })

    print("Registration Successful!")
    print("Student ID:", student_id)
    print("Student Name:", student_name)
    print("Images folder:", student_folder)
else:
    print(f"Registration incomplete: {saved_count}/{total_images}")
    print("Student details CSV-la save pannappadala.")
