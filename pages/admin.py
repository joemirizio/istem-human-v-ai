import streamlit as st

import db

conn = st.connection("game", type="sql")
st.set_page_config(page_title="Admin", page_icon="📈")

st.write("# Admin")
init = st.button(":material/database: Initialize database", width="stretch")
if init:
    db.init_db(conn)
    st.rerun()

st.write("## Results")
results = db.get_results(conn)
st.dataframe(results)
