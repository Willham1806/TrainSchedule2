import streamlit as st
from datetime import date
from Code.Database import get_db

def load_notes_from_db(date_obj, keys):
    db = get_db()
    date_str = date_obj.isoformat()
    doc = db.collection("daily_notes").document(date_str).get()
    if doc.exists:
        data = doc.to_dict()
        return {k: data.get(k, "") for k in keys}
    return {k: "" for k in keys}

def save_notes_to_db(date_obj, notes_dict):
    db = get_db()
    date_str = date_obj.isoformat()
    db.collection("daily_notes").document(date_str).set(notes_dict)

def delete_old_notes():
    db = get_db()
    today_str = date.today().isoformat()
    docs = db.collection("daily_notes").stream()
    for doc in docs:
        if doc.id < today_str:
            doc.reference.delete()

def load_custom_questions():
    db = get_db()
    doc = db.collection("custom_questions").document("all").get()
    if doc.exists:
        return doc.to_dict()
    return {}

def save_custom_question(key, text):
    db = get_db()
    doc_ref = db.collection("custom_questions").document("all")
    doc = doc_ref.get()
    data = doc.to_dict() if doc.exists else {}
    data[key] = text
    doc_ref.set(data)

def delete_custom_question(key):
    db = get_db()
    doc_ref = db.collection("custom_questions").document("all")
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        data.pop(key, None)
        doc_ref.set(data)

def information_page():
    delete_old_notes()

    st.title("🗓️ Information & Planning Page")

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

    if "all_questions" not in st.session_state:
        db_questions = load_custom_questions()
        if not db_questions:
            for key, text in default_questions.items():
                save_custom_question(key, text)
            db_questions = default_questions
        st.session_state["all_questions"] = db_questions

    questions = st.session_state["all_questions"]
    today_key = date.today().isoformat()

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
