from datetime import datetime

from sqlalchemy.sql import text
from streamlit.runtime.scriptrunner import get_script_run_ctx


def init_db(conn):
    with conn.session as s:
        s.execute(text("drop table if exists results"))
        s.execute(
            text(
                "create table results (rowid int auto_increment primary key, session_id text, question_id int, start_time timestamp, end_time timestamp, guesses int, ai int)"
            )
        )
        s.commit()


def get_results(conn):
    return conn.query("select * from results", ttl=1).set_index("rowid")


def add_result(
    conn,
    question_id: int,
    start_time: datetime,
    end_time: datetime,
    guesses: int,
    ai: bool,
):
    with conn.session as s:
        ctx = get_script_run_ctx()
        if not ctx:
            raise Exception("Failed to write results: Invalid session")
        session_id = ctx.session_id

        s.execute(
            text(
                "insert into results (session_id, question_id, start_time, end_time, guesses, ai) values (:session_id, :question_id, :start_time, :end_time, :guesses, :ai)"
            ),
            {
                "session_id": session_id,
                "question_id": question_id,
                "start_time": start_time,
                "end_time": end_time,
                "guesses": guesses,
                "ai": int(ai),
            },
        )
        s.commit()
