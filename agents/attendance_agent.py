import re
from database.database import find_low_attendance

def handle_attendance_query(question):
    threshold = 75

    match = re.search(r'(\d{1,3})\s*%', question)
    if match:
        threshold = int(match.group(1))

    data = find_low_attendance(threshold)

    if data:
        return {
            "message": f"I found **{len(data)} students** with attendance below {threshold}%.",
            "data": data,
        }

    return {
        "message": f"No students were found below {threshold}% attendance.",
        "data": [],
    }
