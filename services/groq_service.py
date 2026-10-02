import streamlit as st
from groq import Groq

def get_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured in Streamlit Secrets.")
    return Groq(api_key=api_key)

def ask_groq(prompt, model="llama-3.1-8b-instant"):
    client = get_groq_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful school management AI assistant. Give concise, clear answers."
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content
