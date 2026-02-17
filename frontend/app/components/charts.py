import streamlit as st


def skills_bar_chart(skill_counts: dict):
    st.bar_chart(skill_counts)
