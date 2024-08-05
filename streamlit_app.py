"""
Streamlit app for our chatbot
"""
import os
import streamlit as st
import tempfile
from rag import init, ingest_pdf, query

init()

st.title("Sansar's retrieval augnmented AI assistant")

uploaded_file = st.file_uploader("Upload your pdf", type="pdf", label_visibility="visible")
if uploaded_file is not None:
    temp_dir = tempfile.mkdtemp()
    path = os.path.join(temp_dir, uploaded_file.name)
    with open(path, "wb") as f:
        f.write(uploaded_file.getvalue())
    ingest_pdf(path)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Enter your query for the AI assistant"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = query(prompt)
        response = st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
