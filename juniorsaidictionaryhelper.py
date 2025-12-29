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

# UI defaults
defaults = {
    "brightness": 1.0,
    "font_size": 16,
    "accent_color": "#1f77b4",
    "bg_color": "#ffffff",
    "text_color": "#000000",
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# -------------------------
# HELPERS
# -------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)
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
    return True, "Registration successful! Please login."

def verify_user(username, password):
    users = load_users()
    return username in users and users[username] == hash_password(password)

def change_password(username, new_password):
    users = load_users()
    users[username] = hash_password(new_password)
    save_users(users)

def change_username(old_username, new_username):
    users = load_users()
    if not new_username:
        return False, "Username cannot be empty."
    if new_username in users:
        return False, "Username already taken."
    users[new_username] = users.pop(old_username)
    save_users(users)
    st.session_state.username = new_username
    return True, "Username updated successfully."

# -------------------------
# SIDEBAR NAVIGATION
# -------------------------
st.sidebar.header("📌 Navigation")

if "nav_page" not in st.session_state:
    st.session_state.nav_page = st.session_state.page

nav_choice = st.sidebar.selectbox(
    "Go to page:",
    ["Login", "Register", "Dictionary", "Settings"],
    index=["Login", "Register", "Dictionary", "Settings"].index(st.session_state.page),
    key="nav_page"
)

# Update page only if user manually changes it
if nav_choice != st.session_state.page:
    st.session_state.page = nav_choice

if st.session_state.authenticated:
    st.sidebar.success(f"Logged in as {st.session_state.username}")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.page = "Login"
        st.session_state.nav_page = "Login"
        st.rerun()

# -------------------------
# GLOBAL STYLES
# -------------------------
st.markdown(
    f"""
    <style>
    html, body, [class*="st"] {{
        background-color: {st.session_state.bg_color};
        color: {st.session_state.text_color};
        font-size: {st.session_state.font_size}px;
        opacity: {st.session_state.brightness};
    }}
    h1, h2, h3 {{
        color: {st.session_state.accent_color};
    }}
    div.stButton > button {{
        background-color: {st.session_state.accent_color};
        color: #ffffff;
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
if st.session_state.page == "Login":
    st.title("🔑 Login")

    st.info(
        "ℹ️ Accounts are stored locally.\n\n"
        "If you reinstalled the app, please **Register again**."
    )

    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login"):
        if verify_user(username.strip(), password.strip()):
            st.session_state.authenticated = True
            st.session_state.username = username.strip()
            st.session_state.page = "Dictionary"  # Auto-redirect to Dictionary
            st.session_state.nav_page = "Dictionary"
            st.success("Login successful! Redirecting to Dictionary...")
            st.rerun()
        else:
            st.error(
                "❌ Login failed.\n\n"
                "• Check username/password\n"
                "• Or register again if app was reinstalled"
            )

    if st.button("➡️ Go to Register"):
        st.session_state.page = "Register"
        st.session_state.nav_page = "Register"
        st.rerun()

# -------------------------
# REGISTER PAGE
# -------------------------
elif st.session_state.page == "Register":
    st.title("📝 Register")

    st.info("Create a new account, then login.")

    username = st.text_input("Choose username", key="reg_user")
    password = st.text_input("Choose password", type="password", key="reg_pass")

    if st.button("Register"):
        success, msg = register_user(username.strip(), password.strip())
        if success:
            st.success(msg)
            st.session_state.page = "Login"
            st.session_state.nav_page = "Login"
            st.rerun()
        else:
            st.error(msg)

    if st.button("⬅️ Back to Login"):
        st.session_state.page = "Login"
        st.session_state.nav_page = "Login"
        st.rerun()

# -------------------------
# DICTIONARY PAGE
# -------------------------
elif st.session_state.page == "Dictionary":
    if not st.session_state.authenticated:
        st.warning("Please login first")
        st.stop()

    st.title("📖 Smart Dictionary AI")

    show_phonetics = st.sidebar.checkbox("Show Phonetics", True, key="show_phonetics")
    play_audio = st.sidebar.checkbox("Play Pronunciation Audio", True, key="play_audio")
    show_synonyms = st.sidebar.checkbox("Show Synonyms", True, key="show_synonyms")
    show_antonyms = st.sidebar.checkbox("Show Antonyms", True, key="show_antonyms")
    show_examples = st.sidebar.checkbox("Show Examples", True, key="show_examples")

    output_style = st.sidebar.radio("Display Style", ("Detailed", "Minimal"), key="output_style")
    layout_option = st.sidebar.radio("Layout", ("Single Column", "Two Columns"), key="layout_option")

    word = st.text_input("Enter a word").strip().lower()

    if word:
        try:
            response = requests.get(API_URL.format(word))
            data = response.json()

            if isinstance(data, dict):
                st.error("No definitions found.")
            else:
                entry = data[0]
                st.subheader(entry["word"].capitalize())

                col1, col2 = st.columns(2) if layout_option == "Two Columns" else (st, st)

                for meaning in entry.get("meanings", []):
                    pos = meaning.get("partOfSpeech", "")
                    for d in meaning.get("definitions", []):
                        if output_style == "Detailed":
                            col1.markdown(f"**({pos})** {d['definition']}")
                        else:
                            col1.write(f"- {d['definition']}")

                        if show_examples and "example" in d:
                            col2.caption("Example: " + d["example"])
                        if show_synonyms and d.get("synonyms"):
                            col2.write("🟢 Synonyms: " + ", ".join(d["synonyms"][:10]))
                        if show_antonyms and d.get("antonyms"):
                            col2.write("🔴 Antonyms: " + ", ".join(d["antonyms"][:10]))
                        if show_phonetics and "phonetics" in entry:
                            for ph in entry["phonetics"]:
                                if "text" in ph:
                                    col2.markdown(f"Phonetic: {ph['text']}")
                                if play_audio and "audio" in ph and ph["audio"]:
                                    col2.audio(ph["audio"], format="audio/mp3")
        except Exception as e:
            st.error(f"Error fetching data: {e}")

# -------------------------
# SETTINGS PAGE
# -------------------------
elif st.session_state.page == "Settings":
    if not st.session_state.authenticated:
        st.warning("Login required")
        st.stop()

    st.title("⚙️ Settings")

    st.subheader("🎨 Display Settings")
    st.session_state.brightness = st.slider("Brightness", 0.5, 1.0, st.session_state.brightness)
    st.session_state.font_size = st.slider("Font Size", 12, 24, st.session_state.font_size)
    st.session_state.accent_color = st.color_picker("Accent Color", st.session_state.accent_color)
    st.session_state.bg_color = st.color_picker("Background Color", st.session_state.bg_color)
    st.session_state.text_color = st.color_picker("Text Color", st.session_state.text_color)

    st.divider()
    st.subheader("🔐 Account Settings")

    new_username = st.text_input("Change Username", key="new_username")
    if st.button("Update Username"):
        if new_username.strip():
            success, msg = change_username(st.session_state.username, new_username.strip())
            if success:
                st.success(msg)
            else:
                st.error(msg)
        else:
            st.error("Username cannot be empty.")

    new_pass = st.text_input("Change Password", type="password")
    if st.button("Update Password"):
        if new_pass:
            change_password(st.session_state.username, new_pass)
            st.success("Password updated successfully")
        else:
            st.error("Password cannot be empty")
