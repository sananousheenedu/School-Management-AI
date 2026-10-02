import re
from agents.student_agent import handle_student_query
from agents.attendance_agent import handle_attendance_query
from agents.exam_agent import handle_exam_query

def ask_orchestrator(question):
    """
    Simple beginner-friendly orchestrator.
    It uses keywords to choose one or more specialist agents.
    Later, Groq can make this routing smarter.
    """
    q = question.lower()

    agents = []
    data = []
    answers = []

    # Multi-agent request
    attendance_words = ["attendance", "absent", "present", "low attendance"]
    exam_words = ["marks", "mark", "exam", "failed", "fail", "result", "score", "mathematics"]

    needs_attendance = any(word in q for word in attendance_words)
    needs_exam = any(word in q for word in exam_words)

    if needs_attendance and needs_exam:
        a = handle_attendance_query(question)
        e = handle_exam_query(question)
        agents = ["Attendance Agent", "Exam Agent"]
        answers.append(a["message"])
        answers.append(e["message"])
        data = a.get("data", [])
        if e.get("data"):
            if data:
                # Keep V1 simple: show both result tables separately.
                data = {"attendance": data, "exam": e["data"]}
            else:
                data = e["data"]

        return {
            "success": True,
            "agents": agents,
            "answer": "I used the Attendance Agent and Exam Agent to answer your request.",
            "data": data,
            "message": "",
        }

    if needs_attendance:
        result = handle_attendance_query(question)
        return {
            "success": True,
            "agents": ["Attendance Agent"],
            "answer": result["message"],
            "data": result.get("data", []),
            "message": "",
        }

    if needs_exam:
        result = handle_exam_query(question)
        return {
            "success": True,
            "agents": ["Exam Agent"],
            "answer": result["message"],
            "data": result.get("data", []),
            "message": "",
        }

    # Student/general request
    result = handle_student_query(question)
    return {
        "success": True,
        "agents": ["Student Agent"],
        "answer": result["message"],
        "data": result.get("data", []),
        "message": "",
    }
