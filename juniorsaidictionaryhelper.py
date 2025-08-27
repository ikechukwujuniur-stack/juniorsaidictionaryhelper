import streamlit as st
import requests

API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/{}"

st.set_page_config(page_title="📖junior dictionary AI", layout="centered")
st.title("📖 junior dictionary AI")
st.write("Type an English word and get its **meaning, synonyms, antonyms, phonetics** online. No API key needed.")

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
            if "phonetics" in entry and entry["phonetics"]:
                for ph in entry["phonetics"]:
                    if "text" in ph:
                        st.write(f"**Phonetic:** {ph['text']}")
                    if "audio" in ph and ph["audio"]:
                        st.audio(ph["audio"])

            # Meanings
            st.subheader("📚 Meanings:")
            for meaning in entry["meanings"]:
                part_of_speech = meaning["partOfSpeech"]
                for i, definition in enumerate(meaning["definitions"], 1):
                    st.markdown(f"**({part_of_speech}) {i}.** {definition['definition']}")
                    if "example" in definition:
                        st.write("_Example:_", definition["example"])
                    if "synonyms" in definition and definition["synonyms"]:
                        st.write("🟢 Synonyms:", ", ".join(definition["synonyms"][:10]))
                    if "antonyms" in definition and definition["antonyms"]:
                        st.write("🔴 Antonyms:", ", ".join(definition["antonyms"][:10]))

    except Exception as e:

        st.error(f"Error fetching data: {e}")

