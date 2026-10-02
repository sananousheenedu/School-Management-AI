# 🎓 AI School Manager V1

Beginner-friendly AI-powered school management system built with:

- Streamlit
- Python
- SQLite
- Groq API
- Simple multi-agent architecture

## V1 Features

- Dashboard
- Student management
- Attendance
- Exams and marks
- Reports
- AI Assistant
- Student Agent
- Attendance Agent
- Exam Agent
- Orchestrator Agent

## Demo Login

Username:
`admin`

Password:
`admin123`

## Groq API

For Streamlit Cloud, add this under:

**App Settings → Secrets**

```toml
GROQ_API_KEY = "your-groq-api-key"
```

The V1 keyword-based agents work without calling Groq for database queries. Groq is included as the AI service foundation for the next upgrade.
