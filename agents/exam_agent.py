import re
from database.database import find_failed_students

def handle_exam_query(question):
    subject = None

    known_subjects = [
        "mathematics", "math", "english", "science",
        "computer", "urdu", "islamiyat"
    ]

    q = question.lower()
    for item in known_subjects:
        if item in q:
            subject = item
            if item == "math":
                subject = "Mathematics"
            break

    data = find_failed_students(subject=subject, pass_percentage=50)

    if subject:
        message = f"I found **{len(data)} students** who scored below 50% in {subject.title()}."
    else:
        message = f"I found **{len(data)} students** who scored below 50%."

    return {
        "message": message,
        "data": data,
    }
