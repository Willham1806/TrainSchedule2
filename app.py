import streamlit as st
from streamlit_option_menu import option_menu
from Booking import booking_page
from Overview import booking_overview_page
from Cancel import train_cancel_page
from RemoveGroup import remove_group_page
from Manual import manual_group_assignment_page
from Party import party_train_page
from Presets import preset_schedule_page
from School import school_train_page
from Information import information_page

import psycopg2
import os

# --- Supabase Setup ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]

conn = psycopg2.connect(SUPABASE_URL)
cursor = conn.cursor()

DIGGERS_ID = "today"  # You can adjust this to use a date key if needed


def load_diggers_count():
    cursor.execute("SELECT count FROM diggers_count WHERE id = %s;", (DIGGERS_ID,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        cursor.execute("INSERT INTO diggers_count (id, count) VALUES (%s, %s);", (DIGGERS_ID, 0))
        conn.commit()
        return 0


def save_diggers_count(new_count):
    cursor.execute("""
        INSERT INTO diggers_count (id, count)
        VALUES (%s, %s)
        ON CONFLICT (id)
        DO UPDATE SET count = EXCLUDED.count;
    """, (DIGGERS_ID, new_count))
    conn.commit()

# --- Main App ---
def main():
    if "diggers_sold" not in st.session_state:
        st.session_state.diggers_sold = load_diggers_count()

    with st.sidebar:
        selected_page = option_menu(
            menu_title="Main Menu",
            options=[
                "Booking", "Overview", "Information","Manual Booking", "Remove Groups",
                "Remove Train Times", "Party Train", "School Train", "Schedule Presets"
            ],
            icons=["book", "list-task", "info-circle", "person", "trash", "x-circle", "gift", "building", "gear"],
            menu_icon="cast",
            default_index=0,
            orientation="vertical",
        )

        st.markdown("### Diggers Sold:")

        cols = st.columns([1, 1, 1])
        with cols[0]:
            if st.button("➖"):
                if st.session_state.diggers_sold > 0:
                    st.session_state.diggers_sold -= 1
                    save_diggers_count(st.session_state.diggers_sold)
                    st.rerun()
        with cols[1]:
            st.markdown(f"<h3 style='text-align:center;'>{st.session_state.diggers_sold}</h3>", unsafe_allow_html=True)
        with cols[2]:
            if st.button("➕"):
                st.session_state.diggers_sold += 1
                save_diggers_count(st.session_state.diggers_sold)
                st.rerun()

    if "last_page" not in st.session_state:
        st.session_state.last_page = selected_page
    elif st.session_state.last_page != selected_page:
        st.session_state.last_page = selected_page
        st.rerun()

    # Page routing
    if selected_page == "Booking":
        booking_page()
    elif selected_page == "Overview":
        booking_overview_page()
    elif selected_page == "Information":
        information_page()
    elif selected_page == "Remove Train Times":
        train_cancel_page()
    elif selected_page == "Remove Groups":
        remove_group_page()
    elif selected_page == "Manual Booking":
        manual_group_assignment_page()
    elif selected_page == "Party Train":
        party_train_page()
    elif selected_page == "Schedule Presets":
        preset_schedule_page()
    elif selected_page == "School Train":
        school_train_page()

if __name__ == "__main__":
    main()
