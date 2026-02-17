import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("Job Listings")

skill_filter = st.text_input("Search by skill")

if skill_filter:
    resp = requests.get(f"{BACKEND_URL}/jobs/search", params={"skill": skill_filter})
else:
    resp = requests.get(f"{BACKEND_URL}/jobs/")

if resp.ok:
    jobs = resp.json()
    for job in jobs:
        st.write(f"**{job['job_title']}** — Skills: {', '.join(job['skills_extracted'] or [])}")
else:
    st.error("Failed to fetch jobs.")
