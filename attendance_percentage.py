
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STUDENTS_FILE = BASE_DIR / "students.csv"
ATTENDANCE_FILE = BASE_DIR / "attendance.csv"


def calculate_attendance():
    if not STUDENTS_FILE.exists():
        print("students.csv file kidaikkala!")
        return

    if not ATTENDANCE_FILE.exists():
        print("attendance.csv file kidaikkala!")
        return

    # Read registered students
    students = {}

    with open(
        STUDENTS_FILE, "r", newline="", encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            student_id = row["student_id"]
            student_name = row["student_name"]
            students[student_id] = student_name

    if not students:
        print("Students register pannala!")
        return

    # Get working days
    try:
        working_days = int(
            input("Total working days enter pannunga: ")
        )

        if working_days <= 0:
            print("Working days 1 or adhukku mela irukkanum!")
            return

    except ValueError:
        print("Correct number enter pannunga!")
        return

    # Read attendance records
    present_days = {student_id: set() for student_id in students}

    with open(
        ATTENDANCE_FILE, "r", newline="", encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            student_id = row.get("student_id", "")
            date = row.get("date", "")
            status = row.get("status", "").strip().lower()

            if (
                student_id in present_days
                and status == "present"
                and date
            ):
                present_days[student_id].add(date)

    # Display report
    print("\n========== ATTENDANCE PERCENTAGE REPORT ==========")
    print(f"{'Student ID':<15}{'Name':<20}{'Present':<10}"
          f"{'Absent':<10}{'Percentage':<12}")
    print("-" * 67)

    for student_id, student_name in students.items():
        present = len(present_days[student_id])
        absent = max(working_days - present, 0)
        percentage = (present / working_days) * 100

        print(
            f"{student_id:<15}"
            f"{student_name:<20}"
            f"{present:<10}"
            f"{absent:<10}"
            f"{percentage:.2f}%"
        )

    print("-" * 67)
    print("Report completed!")


calculate_attendance()
