import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

# --- Firebase Init (only once) ---
def get_db():
    if not firebase_admin._apps:
        key_dict = dict(st.secrets["firebase"])
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(cred)
    return firestore.client()

# --- Schedule ---
def create_tables():
    pass  # Firestore is schemaless, nothing to create

def load_schedule():
    db = get_db()
    doc = db.collection("schedule").document("current").get()
    if doc.exists:
        return doc.to_dict().get("trains", [])
    return []

def save_schedule(schedule):
    db = get_db()
    db.collection("schedule").document("current").set({"trains": schedule})

# --- Presets ---
def create_presets_table():
    pass

def list_presets():
    db = get_db()
    doc = db.collection("presets").document("all").get()
    if doc.exists:
        return list(doc.to_dict().get("presets", {}).keys())
    return []

def load_preset(name):
    db = get_db()
    doc = db.collection("presets").document("all").get()
    if doc.exists:
        return doc.to_dict().get("presets", {}).get(name)
    return None

def save_preset(name, data):
    db = get_db()
    doc_ref = db.collection("presets").document("all")
    doc = doc_ref.get()
    presets = doc.to_dict().get("presets", {}) if doc.exists else {}
    presets[name] = data
    doc_ref.set({"presets": presets})

def delete_preset(name):
    db = get_db()
    doc_ref = db.collection("presets").document("all")
    doc = doc_ref.get()
    if doc.exists:
        presets = doc.to_dict().get("presets", {})
        presets.pop(name, None)
        doc_ref.set({"presets": presets})

# --- Notes ---
def create_notes_table():
    pass  # No schema needed

def load_notes():
    db = get_db()
    doc = db.collection("notes").document("current").get()
    if doc.exists:
        return doc.to_dict().get("notes", "")
    return ""

def save_notes(notes):
    db = get_db()
    db.collection("notes").document("current").set({"notes": notes})

# --- Diggers Count ---
def load_diggers_count():
    db = get_db()
    doc = db.collection("diggers").document("today").get()
    if doc.exists:
        return doc.to_dict().get("count", 0)
    return 0

def save_diggers_count(count):
    db = get_db()
    db.collection("diggers").document("today").set({"count": count})
