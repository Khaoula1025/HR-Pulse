import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("Salary Predictor")

job_title = st.text_input("Job Title")
skills_input = st.text_input("Skills (comma-separated)")

if st.button("Predict"):
    skills = [s.strip() for s in skills_input.split(",") if s.strip()]
    resp = requests.post(
        f"{BACKEND_URL}/predict/",
        json={"job_title": job_title, "skills": skills},
    )
    if resp.ok:
        salary = resp.json()["estimated_salary"]
        st.success(f"Estimated Salary: ${salary:,.0f}K/year")
    else:
        st.error("Prediction failed.")
