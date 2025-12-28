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
        return False, "❌ Username and password cannot be empty"
    users = load_users()
    if username in users:
        return False, "⚠️ Username already exists. Please login instead."
    users[username] = hash_password(password)
    save_users(users)
    return True, "✅ Registration successful! Please login next."

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
st.sidebar.caption("⬇️ Use this menu to move between pages")

page = st.sidebar.selectbox(
    "Go to page:",
    ["Login", "Register", "Dictionary", "Settings"],
    index=["Login", "Register", "Dictionary", "Settings"].index(st.session_state.page)
)
st.session_state.page = page

if st.session_state.authenticated:
    st.sidebar.success(f"Logged in as {st.session_state.username}")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.page = "Login"
        st.rerun()

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
    h1, h2, h3, h4, h5, h6 {{
        color: {st.session_state.accent_color} !important;
    }}
    div.stButton > button {{
        background-color: {st.session_state.accent_color} !important;
        color: #ffffff !important;
        border-radius: 8px;
        padding: 0.5em 1em;
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

    st.info(
        "👉 **Already registered?** Enter your username & password and press **Login**.\n\n"
        "👉 **New here?** Go to **Register** using the sidebar on the left."
    )

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if verify_user(username.strip(), password.strip()):
            st.session_state.authenticated = True
            st.session_state.username = username.strip()
            st.session_state.page = "Dictionary"
            st.success(f"🎉 Welcome {username}!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

    if st.button("➡️ Go to Register"):
        st.session_state.page = "Register"
        st.rerun()

# -------------------------
# REGISTER PAGE
# -------------------------
elif page == "Register":
    st.title("📝 Register")

    st.info(
        "🆕 **Create a new account here**\n\n"
        "After registering, you will be taken back to **Login** to sign in."
    )

    if st.session_state.authenticated:
        st.warning("You are already logged in.")
        st.stop()

    username = st.text_input("Choose a username")
    password = st.text_input("Choose a password", type="password")

    if st.button("Register"):
        success, msg = register_user(username.strip(), password.strip())
        if success:
            st.success(msg)
            st.session_state.page = "Login"
            st.rerun()
        else:
            st.error(msg)

    if st.button("⬅️ Back to Login"):
        st.session_state.page = "Login"
        st.rerun()

# -------------------------
# DICTIONARY PAGE
# -------------------------
elif page == "Dictionary":
    if not st.session_state.authenticated:
        st.warning("🔒 Please login first (use the sidebar)")
    else:
        st.title("📖 Smart Dictionary AI")
        st.caption(f"👤 Logged in as {st.session_state.username}")

        st.info("✏️ Type a word below and press **Enter** to get its meaning.")

        show_phonetics = st.sidebar.checkbox("Show Phonetics", True)
        play_audio = st.sidebar.checkbox("Play Pronunciation Audio", True)
        show_examples = st.sidebar.checkbox("Show Examples", True)

        word = st.text_input("Enter a word").strip().lower()

        if word:
            try:
                response = requests.get(API_URL.format(word))
                data = response.json()

                if isinstance(data, dict):
                    st.error("❌ No definitions found.")
                else:
                    entry = data[0]
                    st.subheader(entry["word"].capitalize())

                    for meaning in entry.get("meanings", []):
                        for definition in meaning.get("definitions", []):
                            st.write("•", definition["definition"])
                            if show_examples and "example" in definition:
                                st.caption("Example: " + definition["example"])

            except Exception as e:
                st.error(f"Error fetching data: {e}")

# -------------------------
# SETTINGS PAGE
# -------------------------
elif page == "Settings":
    st.title("⚙️ Settings")

    if not st.session_state.authenticated:
        st.warning("🔒 Login required to access settings")
        st.stop()

    st.subheader("🎨 Display Settings")
    st.session_state.brightness = st.slider("Brightness", 0.5, 1.0, st.session_state.brightness)
    st.session_state.font_size = st.slider("Font Size", 12, 24, st.session_state.font_size)
    st.session_state.accent_color = st.color_picker("Accent Color", st.session_state.accent_color)
    st.session_state.bg_color = st.color_picker("Background Color", st.session_state.bg_color)
    st.session_state.text_color = st.color_picker("Text Color", st.session_state.text_color)

    st.divider()
    st.subheader("🔐 Account Settings")
    new_pass = st.text_input("Change password", type="password")
    if st.button("Update Password"):
        if new_pass:
            change_password(st.session_state.username, new_pass)
            st.success("✅ Password updated successfully")
        else:
            st.error("Password cannot be empty")
