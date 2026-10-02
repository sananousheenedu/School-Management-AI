from database.database import get_students, find_student_result

def handle_student_query(question):
    q = question.lower()

    # Very simple name extraction for V1.
    if "result" in q:
        # Try to extract a name after "result"
        name = question.lower().split("result", 1)[-1].strip()
        name = name.replace("of", "").replace("for", "").strip()
        if name:
            data = find_student_result(name)
            if data:
                return {
                    "message": f"Here is the result information I found for **{name}**.",
                    "data": data,
                }

    data = get_students("")
    if data:
        return {
            "message": f"I found **{len(data)} students** in the school database.",
            "data": data,
        }

    return {
        "message": "There are no students in the database yet. Add a student first.",
        "data": [],
    }
