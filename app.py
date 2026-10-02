import streamlit as st
from database.database import init_db, get_dashboard_stats, get_students, add_student, save_attendance, get_attendance_report, save_mark, get_results
from agents.orchestrator import ask_orchestrator

st.set_page_config(
    page_title="AI School Manager",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Theme ----------
st.markdown("""
<style>
    .main {background: #f7f9fc;}
    [data-testid="stSidebar"] {background: #102a43;}
    [data-testid="stSidebar"] * {color: white !important;}
    .card {
        background: white;
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #e7edf4;
        box-shadow: 0 2px 10px rgba(16,42,67,.05);
        margin-bottom: 15px;
    }
    .metric-title {font-size: 14px; color: #627d98;}
    .metric-value {font-size: 30px; font-weight: 700; color: #102a43;}
    .small-muted {color:#627d98; font-size:14px;}
    .ai-box {
        background: white;
        border: 1px solid #d9e2ec;
        border-radius: 14px;
        padding: 18px;
    }
</style>
""", unsafe_allow_html=True)

init_db()

# ---------- Session ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = "Principal"
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# ---------- Login ----------
def login_page():
    st.markdown("<br><br>", unsafe_allow_html=True)
    left, center, right = st.columns([1, 1.2, 1])
    with center:
        st.markdown(
            "<div style='text-align:center'><h1>🎓 AI School Manager</h1>"
            "<p class='small-muted'>Smart Management • Better Education</p></div>",
            unsafe_allow_html=True
        )
        with st.container(border=True):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            role = st.selectbox("Role", ["Principal", "Teacher", "Student", "Parent"])
            if st.button("Login", type="primary", use_container_width=True):
                # Simple demo authentication for V1.
                if username == "admin" and password == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.role = role
                    st.rerun()
                else:
                    st.error("Demo login: username = admin, password = admin123")

if not st.session_state.logged_in:
    login_page()
    st.stop()

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🎓 AI School Manager")
    st.caption(f"Logged in as: {st.session_state.role}")
    st.divider()

    pages = ["Dashboard", "Students", "Attendance", "Exams & Marks", "AI Assistant", "Reports"]
    for page in pages:
        icon = {
            "Dashboard":"🏠", "Students":"👨‍🎓", "Attendance":"📅",
            "Exams & Marks":"📝", "AI Assistant":"🤖", "Reports":"📊"
        }[page]
        if st.button(f"{icon}  {page}", use_container_width=True):
            st.session_state.page = page
            st.rerun()

    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ---------- Helpers ----------
def metric_card(title, value, icon):
    st.markdown(
        f"""<div class="card">
        <div class="metric-title">{icon} {title}</div>
        <div class="metric-value">{value}</div>
        </div>""",
        unsafe_allow_html=True
    )

# ---------- Dashboard ----------
def dashboard():
    st.title("Good Morning! 👋")
    st.caption("Welcome to your AI-powered school management dashboard.")

    stats = get_dashboard_stats()
    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Students", stats["students"], "👨‍🎓")
    with c2: metric_card("Teachers", stats["teachers"], "👩‍🏫")
    with c3: metric_card("Attendance", f'{stats["attendance"]}%', "📅")
    with c4: metric_card("Subjects", stats["subjects"], "📚")

    st.subheader("Quick Actions")
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        if st.button("➕ Add Student", use_container_width=True):
            st.session_state.page = "Students"
            st.rerun()
    with q2:
        if st.button("📅 Mark Attendance", use_container_width=True):
            st.session_state.page = "Attendance"
            st.rerun()
    with q3:
        if st.button("📝 Enter Marks", use_container_width=True):
            st.session_state.page = "Exams & Marks"
            st.rerun()
    with q4:
        if st.button("🤖 Ask AI", use_container_width=True):
            st.session_state.page = "AI Assistant"
            st.rerun()

    st.subheader("What this V1 can do")
    a, b, c = st.columns(3)
    with a:
        st.markdown('<div class="card"><h3>👨‍🎓 Students</h3><p>Add, search and view student records.</p></div>', unsafe_allow_html=True)
    with b:
        st.markdown('<div class="card"><h3>📅 Attendance</h3><p>Mark attendance and find low-attendance students.</p></div>', unsafe_allow_html=True)
    with c:
        st.markdown('<div class="card"><h3>🤖 AI Assistant</h3><p>Ask school-data questions using the multi-agent system.</p></div>', unsafe_allow_html=True)

# ---------- Students ----------
def students_page():
    st.title("👨‍🎓 Students")
    st.caption("Manage basic student information.")

    with st.expander("➕ Add New Student", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Student Name")
            roll_no = st.text_input("Roll Number")
            father_name = st.text_input("Father Name")
        with c2:
            class_name = st.text_input("Class", placeholder="e.g. 8")
            section = st.text_input("Section", placeholder="e.g. A")
            phone = st.text_input("Phone")
        if st.button("Save Student", type="primary"):
            if not name or not roll_no or not class_name or not section:
                st.warning("Please fill Name, Roll Number, Class and Section.")
            else:
                try:
                    add_student(roll_no, name, father_name, class_name, section, phone)
                    st.success("Student added successfully.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not add student: {e}")

    search = st.text_input("🔍 Search by name or roll number")
    students = get_students(search)

    if students:
        st.dataframe(
            students,
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": None,
                "roll_no": "Roll No",
                "name": "Name",
                "class_name": "Class",
                "section": "Section",
                "father_name": "Father Name",
                "phone": "Phone",
            },
        )
    else:
        st.info("No students found.")

# ---------- Attendance ----------
def attendance_page():
    st.title("📅 Attendance")
    st.caption("Mark today's attendance.")

    students = get_students("")
    if not students:
        st.info("Add students first.")
        return

    class_options = sorted(set(str(s["class_name"]) for s in students))
    class_name = st.selectbox("Class", class_options)
    section_options = sorted(set(str(s["section"]) for s in students if str(s["class_name"]) == class_name))
    section = st.selectbox("Section", section_options)
    date = st.date_input("Date")

    selected = [s for s in students if str(s["class_name"]) == class_name and str(s["section"]) == section]

    if selected:
        st.write(f"**{len(selected)} students**")
        statuses = {}
        for s in selected:
            statuses[s["id"]] = st.radio(
                f'{s["roll_no"]} — {s["name"]}',
                ["Present", "Absent"],
                horizontal=True,
                key=f'att_{s["id"]}_{date}'
            )

        if st.button("💾 Save Attendance", type="primary"):
            for student_id, status in statuses.items():
                save_attendance(student_id, str(date), status)
            st.success("Attendance saved successfully.")

# ---------- Exams ----------
def exams_page():
    st.title("📝 Exams & Marks")
    st.caption("Enter student marks.")

    students = get_students("")
    if not students:
        st.info("Add students first.")
        return

    with st.form("marks_form"):
        student_map = {f'{s["roll_no"]} — {s["name"]}': s["id"] for s in students}
        selected_student = st.selectbox("Student", list(student_map.keys()))
        subject = st.text_input("Subject", placeholder="Mathematics")
        exam = st.text_input("Exam", value="Mid Term")
        c1, c2 = st.columns(2)
        with c1:
            obtained = st.number_input("Obtained Marks", min_value=0.0, step=1.0)
        with c2:
            total = st.number_input("Total Marks", min_value=1.0, value=100.0, step=1.0)

        submitted = st.form_submit_button("💾 Save Marks", type="primary")
        if submitted:
            if not subject:
                st.warning("Enter a subject.")
            elif obtained > total:
                st.warning("Obtained marks cannot be greater than total marks.")
            else:
                save_mark(student_map[selected_student], subject, exam, obtained, total)
                st.success("Marks saved successfully.")

    st.subheader("Recent Results")
    results = get_results()
    if results:
        st.dataframe(results, use_container_width=True, hide_index=True)
    else:
        st.info("No marks entered yet.")

# ---------- AI Assistant ----------
def ai_page():
    st.title("🤖 AI School Assistant")
    st.caption("Ask questions about students, attendance and marks.")

    st.markdown('<div class="ai-box">', unsafe_allow_html=True)
    st.write("### Try one of these")
    examples = [
        "Show students with attendance below 75%",
        "Who failed Mathematics?",
        "Show Ali Khan's result",
        "Which students have low attendance and low marks?",
    ]
    for example in examples:
        if st.button(example, use_container_width=True):
            st.session_state.ai_question = example
    st.markdown("</div>", unsafe_allow_html=True)

    question = st.text_input(
        "Ask your question",
        value=st.session_state.get("ai_question", ""),
        placeholder="e.g. Show students with attendance below 75%"
    )

    if st.button("🚀 Ask AI", type="primary"):
        if not question.strip():
            st.warning("Please enter a question.")
            return
        with st.spinner("AI agents are working..."):
            result = ask_orchestrator(question)
        if result["success"]:
            st.success(f'Agents used: {", ".join(result["agents"])}')
            st.markdown(result["answer"])
            if result.get("data"):
                st.dataframe(result["data"], use_container_width=True, hide_index=True)
        else:
            st.error(result["message"])

# ---------- Reports ----------
def reports_page():
    st.title("📊 Reports")
    stats = get_dashboard_stats()

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Total Students", stats["students"])
        report = get_attendance_report()
        if report:
            st.subheader("Attendance Summary")
            st.dataframe(report, use_container_width=True, hide_index=True)
    with c2:
        st.metric("Average Attendance", f'{stats["attendance"]}%')
        results = get_results()
        if results:
            st.subheader("Results")
            st.dataframe(results, use_container_width=True, hide_index=True)

# ---------- Router ----------
if st.session_state.page == "Dashboard":
    dashboard()
elif st.session_state.page == "Students":
    students_page()
elif st.session_state.page == "Attendance":
    attendance_page()
elif st.session_state.page == "Exams & Marks":
    exams_page()
elif st.session_state.page == "AI Assistant":
    ai_page()
elif st.session_state.page == "Reports":
    reports_page()
