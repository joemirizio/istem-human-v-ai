from pathlib import Path

import streamlit as st


def navigate(ai: bool):
    st.session_state.ai = ai


st.set_page_config(
    "Humans vs. Machines", page_icon=":material/smart_toy:", layout="centered"
)
st.html(Path("static/style.css"))

st.markdown("# :material/face: Humans vs. Machines :material/smart_toy:")
st.image("static/hero.png")
st.markdown("""
In this experiment, we will test the speed of answering a question about (fictitious) medical notes with and without the assistance of AI. 
A series of ten questions will be presented to the user, all of which do not require medical knowledge to answer. 
"Human" users must read the notes to answer the question, while "Human + AI" users have access to an AI large-language model (LLM) assistant pre-programmed with the note's content.
""")
instructions = st.expander("Instructions", icon=":material/format_list_numbered:")
instructions.markdown("""
1. Choose "Human" or "Human & AI" as instructed
1. Based on your role, do the following:
    1. As "Human"
        1. Read the question
        1. Click "Show notes"
        1. Read the note and determine the answer
        1. Type or copy/paste the answer into the response form
        1. Click submit
    1. As "Human + AI"
        1. Click "Show notes"
        1. In the sidebar, send the question to the assistant
        1. Wait for the response
        1. Type or copy/paste the answer into the response form
        1. Click submit
1. Click "Next" and repeat the process until all questions have been answered
""")
st.markdown("## :material/play_circle: Start Experiment")
columns = st.columns(2)
b1 = columns[0].button(
    "Human",
    key="start_human",
    on_click=lambda: navigate(False),
    use_container_width=True,
    icon=":material/face:",
    type="primary",
)
b2 = columns[1].button(
    "Human + AI",
    key="start_ai",
    on_click=lambda: navigate(True),
    use_container_width=True,
    icon=":material/smart_toy:",
    type="primary",
)
if b1 or b2:
    st.switch_page("pages/survey.py")

if st.button(
    "Results",
    icon=":material/bar_chart:",
    use_container_width=True,
):
    st.switch_page("pages/results.py")
