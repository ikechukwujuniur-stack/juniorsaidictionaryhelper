import streamlit as st
import hashlib
import json
import os
import requests

# -------------------------
# CONFIG
# -------------------------
USERS_FILE = "users.json"
API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/{}"

st.set_page_config(page_title="📖 Smart Dictionary AI", layout="centered")

# -------------------------
# SESSION STATE
# -------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "page" not in st.session_state:
    st.session_state.page = "Login"

# UI settings
if "theme" not in st.session_state:
    st.session_state.theme = "Light"
if "brightness" not in st.session_state:
    st.session_state.brightness = 1.0
if "font_size" not in st.session_state:
    st.session_state.font_size = 16
if "accent_color" not in st.session_state:
    st.session_state.accent_color = "#1f77b4"
if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#ffffff"
if "text_color" not in st.session_state:
    st.session_state.text_color = "#000000"

# -------------------------
# HELPERS
# -------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def register_user(username, password):
    if not username or not password:
        return False, "Username and password cannot be empty"
    users = load_users()
    if username in users:
        return False, "Username already exists. Please login."
    users[username] = hash_password(password)
    save_users(users)
    return True, "Registration successful! You can now login."

def verify_user(username, password):
    users = load_users()
    return username in users and users[username] == hash_password(password)

def change_password(username, new_password):
    users = load_users()
    users[username] = hash_password(new_password)
    save_users(users)

# -------------------------
# SIDEBAR NAVIGATION
# -------------------------
st.sidebar.header("📌 Navigation")
page = st.sidebar.selectbox(
    "Go to page:",
    ["Login", "Register", "Dictionary", "Settings"],
    index=["Login", "Register", "Dictionary", "Settings"].index(st.session_state.page)
)
st.session_state.page = page

if st.session_state.authenticated:
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.page = "Login"
        st.experimental_rerun()

# -------------------------
# APPLY GLOBAL STYLES
# -------------------------
st.markdown(
    f"""
    <style>
    html, body, [class*="st"] {{
        background-color: {st.session_state.bg_color} !important;
        color: {st.session_state.text_color} !important;
        font-size: {st.session_state.font_size}px !important;
        opacity: {st.session_state.brightness};
    }}
    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
    .stMarkdown strong, .stTitle, .stHeader, .stSubheader {{
        color: {st.session_state.accent_color} !important;
        font-weight: bold !important;
    }}
    div.stButton > button {{
        background-color: {st.session_state.accent_color} !important;
        color: #ffffff !important;
        border-radius: 8px;
        padding: 0.5em 1em;
    }}
    div.stButton > button:hover {{
        opacity: 0.85;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------
# LOGIN PAGE
# -------------------------
if page == "Login":
    st.title("🔑 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if verify_user(username.strip(), password.strip()):
            st.session_state.authenticated = True
            st.session_state.username = username.strip()
            st.session_state.page = "Dictionary"
            st.success(f"Welcome {username} 🎉")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password")
    st.info("New user? Go to Register in the sidebar.")

# -------------------------
# REGISTER PAGE
# -------------------------
elif page == "Register":
    st.title("📝 Register")
    if st.session_state.authenticated:
        st.warning("You are already logged in.")
        st.stop()
    username = st.text_input("Choose username")
    password = st.text_input("Choose password", type="password")
    if st.button("Register"):
        success, msg = register_user(username.strip(), password.strip())
        if success:
            st.success(msg)
            st.session_state.page = "Login"
            st.experimental_rerun()
        else:
            st.error(msg)

# -------------------------
# DICTIONARY PAGE
# -------------------------
elif page == "Dictionary":
    if not st.session_state.authenticated:
        st.warning("🔒 Please login first")
    else:
        st.title("📖 Smart Dictionary AI")
        st.caption(f"Logged in as {st.session_state.username}")

        # Dictionary settings inside sidebar
        show_phonetics = st.sidebar.checkbox("Show Phonetics", True)
        play_audio = st.sidebar.checkbox("Play Pronunciation Audio", True)
        show_synonyms = st.sidebar.checkbox("Show Synonyms", True)
        show_antonyms = st.sidebar.checkbox("Show Antonyms", True)
        show_examples = st.sidebar.checkbox("Show Examples", True)
        output_style = st.sidebar.radio("Choose display style:", ("Detailed", "Minimal"))
        layout_option = st.sidebar.radio("Choose layout:", ("Single Column", "Two Columns"))

        word = st.text_input("Enter a word").strip().lower()

        if word:
            try:
                response = requests.get(API_URL.format(word))
                data = response.json()

                if isinstance(data, dict) and data.get("title") == "No Definitions Found":
                    st.error("❌ No definitions found. Try another word.")
                else:
                    entry = data[0]

                    # Word + phonetics
                    st.subheader(f"🔍 {entry['word'].capitalize()}")
                    if show_phonetics and "phonetics" in entry and entry["phonetics"]:
                        for ph in entry["phonetics"]:
                            if "text" in ph:
                                st.markdown(
                                    f"<span style='color:{st.session_state.accent_color}; font-weight:bold;'>Phonetic: {ph['text']}</span>",
                                    unsafe_allow_html=True,
                                )
                            if play_audio and "audio" in ph and ph["audio"]:
                                st.markdown("🔊 Pronunciation:")
                                st.audio(ph["audio"], format="audio/mp3")

                    # Layout control
                    if layout_option == "Two Columns":
                        col1, col2 = st.columns(2)
                    else:
                        col1 = st
                        col2 = st

                    # Meanings, examples, synonyms, antonyms
                    col1.subheader("📚 Meanings:")
                    for meaning in entry.get("meanings", []):
                        part_of_speech = meaning.get("partOfSpeech", "")
                        for i, definition in enumerate(meaning.get("definitions", []), 1):
                            if output_style == "Detailed":
                                col1.markdown(
                                    f"<span style='color:{st.session_state.accent_color}; font-weight:bold;'>({part_of_speech}) {i}.</span> {definition['definition']}",
                                    unsafe_allow_html=True,
                                )
                            else:
                                col1.write(f"- {definition['definition']}")

                            if show_examples and "example" in definition:
                                col2.write("_Example:_ " + definition["example"])
                            if show_synonyms and "synonyms" in definition and definition["synonyms"]:
                                col2.write("🟢 Synonyms: " + ", ".join(definition["synonyms"][:10]))
                            if show_antonyms and "antonyms" in definition and definition["antonyms"]:
                                col2.write("🔴 Antonyms: " + ", ".join(definition["antonyms"][:10]))

            except Exception as e:
                st.error(f"Error fetching data: {e}")

# -------------------------
# SETTINGS PAGE
# -------------------------
elif page == "Settings":
    st.title("⚙️ Settings")
    if not st.session_state.authenticated:
        st.warning("Login required to access Settings")
        st.stop()

    # Display settings
    st.subheader("🎨 Display Settings")
    st.session_state.brightness = st.slider("Brightness", 0.5, 1.0, st.session_state.brightness)
    st.session_state.font_size = st.slider("Font Size", 12, 24, st.session_state.font_size)
    st.session_state.accent_color = st.color_picker("Accent / Highlight Color", st.session_state.accent_color)
    st.session_state.bg_color = st.color_picker("Background Color", st.session_state.bg_color)
    st.session_state.text_color = st.color_picker("Text Color", st.session_state.text_color)

    st.divider()
    st.subheader("🔐 Account Settings")
    new_pass = st.text_input("Change password", type="password")
    if st.button("Update Password"):
        if new_pass:
            change_password(st.session_state.username, new_pass)
            st.success("Password updated successfully")
        else:
            st.error("Password cannot be empty")
