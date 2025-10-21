import streamlit as st
from datetime import date
import psycopg2
import os

conn = psycopg2.connect(st.secrets["SUPABASE_URL"])
cursor = conn.cursor()

def load_notes_from_db(date_obj, keys):
    date_str = date_obj.isoformat()
    format_strings = ','.join(['%s'] * len(keys))
    query = f"SELECT key, value FROM daily_notes WHERE date = %s AND key IN ({format_strings});"
    cursor.execute(query, (date_str, *keys))
    rows = cursor.fetchall()
    return {key: value for key, value in rows}


def save_notes_to_db(date_obj, notes_dict):
    date_str = date_obj.isoformat()
    # Delete existing notes for that date
    cursor.execute("DELETE FROM daily_notes WHERE date = %s;", (date_str,))
    # Insert new notes
    insert_query = "INSERT INTO daily_notes (date, key, value) VALUES (%s, %s, %s);"
    for k, v in notes_dict.items():
        cursor.execute(insert_query, (date_str, k, v))
    conn.commit()


def delete_old_notes():
    today_str = date.today().isoformat()
    cursor.execute("DELETE FROM daily_notes WHERE date < %s;", (today_str,))
    conn.commit()


def load_custom_questions():
    cursor.execute("SELECT key, text FROM custom_questions;")
    rows = cursor.fetchall()
    return {key: text for key, text in rows}


def save_custom_question(key, text):
    cursor.execute("INSERT INTO custom_questions (key, text) VALUES (%s, %s) ON CONFLICT (key) DO NOTHING;", (key, text))
    conn.commit()


def delete_custom_question(key):
    cursor.execute("DELETE FROM custom_questions WHERE key = %s;", (key,))
    conn.commit()

def information_page():
    # Auto-delete outdated notes
    delete_old_notes()

    st.title("🗓️ Information & Planning Page")

    # Load all questions from DB (initial default ones + user-added)
    default_questions = {
        "in_charge": "In charge:",
        "first_aider": "First Aider:",
        "diggers_1_2": "Diggers 1pm-2pm:",
        "train_lunch": "What time is the train driver having lunch and who is covering:",
        "clean_toilet": "Clean top toilet before 11:00am:",
        "quads_gokarts": "Quads & gokarts before 11:00am:",
        "leaf_blow": "Leaf blow Molly the Cow concrete, Panning for gold, train station etc.:",
        "general_rubbish": "General rubbish walk:",
        "party_trains": "Times of party trains today:",
        "school_trains": "Schools and the time of their trains today:",
    }

    # Load all questions from DB
    if "all_questions" not in st.session_state:
        db_questions = load_custom_questions()
        if not db_questions:
            # If empty, save defaults to DB
            for key, text in default_questions.items():
                save_custom_question(key, text)
            db_questions = default_questions
        st.session_state["all_questions"] = db_questions

    questions = st.session_state["all_questions"]
    today_key = date.today().isoformat()

    # --- Show today's notes (read-only) ---
    st.markdown("### 📅 Today's Notes")
    today_notes = load_notes_from_db(date.today(), list(questions.keys()))

    with st.expander(f"📅 Notes for Today ({today_key})", expanded=True):
        has_any = False
        for key, question_text in questions.items():
            val = today_notes.get(key, "").strip()
            if val:
                has_any = True
                st.markdown(f"**{question_text}**")
                st.markdown(val)
                st.markdown("")
        if not has_any:
            st.info("No notes saved for today yet.")

    st.markdown("---")

    # --- Edit notes for selected date ---
    st.header("📅 Plan for Another Date")

    selected_date = st.date_input("Select a date to plan for", value=date.today())
    date_key = selected_date.isoformat()
    notes_for_date = load_notes_from_db(selected_date, list(questions.keys()))

    for key, question_text in questions.items():
        notes_for_date[key] = st.text_input(question_text, value=notes_for_date.get(key, ""), key=f"{date_key}_{key}")

    if st.button(f"💾 Save Notes for {date_key}"):
        save_notes_to_db(selected_date, notes_for_date)
        st.success(f"Notes saved for {date_key}!")
        st.rerun()

    st.markdown("---")
    st.subheader("➕ Add a New Question")

    new_question_text = st.text_input("Enter your new question here:")
    if st.button("Add Question"):
        if not new_question_text.strip():
            st.error("Please enter a non-empty question.")
        else:
            new_key = f"user_q_{len(st.session_state['all_questions']) + 1}"
            st.session_state["all_questions"][new_key] = new_question_text.strip()
            save_custom_question(new_key, new_question_text.strip())
            st.success(f"Added new question: {new_question_text}")
            st.rerun()

    st.markdown("---")
    st.subheader("➖ Remove a Question")

    if questions:
        question_to_remove = st.selectbox(
            "Select a question to remove:",
            options=list(questions.keys()),
            format_func=lambda k: questions[k]
        )
        if st.button("Remove Selected Question"):
            removed_text = questions.pop(question_to_remove)
            delete_custom_question(question_to_remove)
            st.success(f"Removed question: {removed_text}")
            st.rerun()
    else:
        st.info("No questions to remove.")

if __name__ == "__main__":
    information_page()
