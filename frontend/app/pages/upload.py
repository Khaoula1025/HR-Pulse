import streamlit as st

st.title("Upload Job CSV")
uploaded = st.file_uploader("Choose a CSV file", type="csv")
if uploaded:
    st.success(f"Uploaded: {uploaded.name}")
    st.info("Ingestion pipeline integration coming soon.")
