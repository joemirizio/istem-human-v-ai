from typing import Iterable, Iterator

import ollama
import streamlit as st


async def _ollama_stream(chat_output):
    for message in chat_output:
        yield message["message"]["content"]


def chat(
    client, messages: Iterable[str], model="gemma3:1b"
) -> Iterator[ollama.ChatResponse]:
    return client.chat(
        model=model,
        messages=[
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ],
        stream=True,
    )


client = ollama.Client()


def render_assistant(round_started: bool, note: str, question: str):
    st.write("### :material/robot_2: AI Assistant")
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if not round_started:
        st.session_state.chat_input = ""

    if prompt := st.chat_input(
        "Ask a question about the current notes",
        disabled=not round_started,
        key="chat_input",
    ):
        note = note.replace("\n", " ")
        prompt = f"""Given the medical note "{note}", return a succinct answer to the following question: "{prompt}"."""
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                stream = chat(client, st.session_state.messages)
                response = st.write_stream(_ollama_stream(stream))
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
                st.rerun()
            except Exception:
                st.error(
                    "Failed to communicate with chat assistant",
                    icon=":material/signal_disconnected:",
                )
