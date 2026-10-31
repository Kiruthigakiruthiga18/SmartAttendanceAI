
import csv
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
ATTENDANCE_FILE = BASE_DIR / "attendance.csv"


def view_attendance_report():
    if not ATTENDANCE_FILE.exists():
        print("Attendance file innum create aagala!")
        return

    with open(
        ATTENDANCE_FILE, "r", newline="", encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)
        records = list(reader)

    if not records:
        print("Attendance records edhuvum illai!")
        return

    print("\n===== SMART ATTENDANCE REPORT =====")

    report_date = input(
        "Date enter pannunga (YYYY-MM-DD), "
        "illaina Enter press pannunga for today: "
    ).strip()

    if not report_date:
        report_date = datetime.now().strftime("%Y-%m-%d")

    daily_records = [
        row for row in records
        if row.get("date") == report_date
    ]

    print("\nDate:", report_date)
    print("-" * 75)
    print(
        f"{'Student ID':<15}"
        f"{'Student Name':<20}"
        f"{'Time':<15}"
        f"{'Status':<12}"
    )
    print("-" * 75)

    if not daily_records:
        print("Indha date-ku attendance records kidaikkala.")
        return

    for row in daily_records:
        print(
            f"{row.get('student_id', ''):<15}"
            f"{row.get('student_name', ''):<20}"
            f"{row.get('time', ''):<15}"
            f"{row.get('status', ''):<12}"
        )

    present_count = sum(
        1 for row in daily_records
        if row.get("status", "").lower() == "present"
    )

    print("-" * 75)
    print("Total attendance records:", len(daily_records))
    print("Students Present:", present_count)
    print("===== REPORT COMPLETED =====")


view_attendance_report()
