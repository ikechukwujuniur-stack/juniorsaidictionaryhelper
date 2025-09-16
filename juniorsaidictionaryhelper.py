import streamlit as st
import requests

API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/{}"

st.set_page_config(page_title="📖 smart Dictionary AI", layout="centered")
st.title("📖 smart Dictionary AI")
st.write("Type an English word and get its **meaning, synonyms, antonyms, phonetics and voices** online. No API key needed.")

# Sidebar settings
st.sidebar.header("⚙️ Settings")

# 🎨 Gradient box for color settings
st.sidebar.markdown(
    """
    <div style="
        padding:15px; 
        border-radius:12px; 
        background: linear-gradient(135deg, #ff9a9e, #fad0c4); 
        border:2px solid #d35400;
        margin-bottom:15px;
    ">
        <h4 style="margin:0; text-align:center; color:#2d3436;">🎨 Color Settings</h4>
    </div>
    """,
    unsafe_allow_html=True
)

# Color settings
theme_color = st.sidebar.color_picker("Highlight Color", "#1f77b4")
bg_color = st.sidebar.color_picker("Background Color", "#ffffff")
text_color = st.sidebar.color_picker("Text Color", "#000000")

# Apply background + text color globally
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {bg_color} !important;
            color: {text_color} !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Display options
show_phonetics = st.sidebar.checkbox("Show Phonetics", True)
play_audio = st.sidebar.checkbox("Play Pronunciation Audio", True)
show_synonyms = st.sidebar.checkbox("Show Synonyms", True)
show_antonyms = st.sidebar.checkbox("Show Antonyms", True)
show_examples = st.sidebar.checkbox("Show Examples", True)

# Output style
output_style = st.sidebar.radio("Choose display style:", ("Detailed", "Minimal"))

# Layout
layout_option = st.sidebar.radio("Choose layout:", ("Single Column", "Two Columns"))

# Voice speed option
voice_speed = st.sidebar.slider("Voice Speed (for pronunciation)", 0.5, 2.0, 1.0, 0.1)

# Input word
word = st.text_input("Enter a word:", value=" ").strip().lower()

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
                            f"<span style='color:{theme_color}; font-weight:bold;'>Phonetic: {ph['text']}</span>",
                            unsafe_allow_html=True,
                        )
                    if play_audio and "audio" in ph and ph["audio"]:
                        st.audio(ph["audio"])

            # Layout control
            if layout_option == "Two Columns":
                col1, col2 = st.columns(2)
            else:
                col1, col2 = st, st

            # Meanings
            col1.subheader("📚 Meanings:")
            for meaning in entry["meanings"]:
                part_of_speech = meaning["partOfSpeech"]
                for i, definition in enumerate(meaning["definitions"], 1):
                    if output_style == "Detailed":
                        col1.markdown(
                            f"<span style='color:{theme_color}; font-weight:bold;'>({part_of_speech}) {i}.</span> {definition['definition']}",
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


