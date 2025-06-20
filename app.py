import streamlit as st
import re
import random
import pandas as pd
from pathlib import Path
import io
from utils.pdf_loader import extract_text_from_pdf, chunk_text
from utils.embed_store import upsert_chunks, query_chunks
from utils.clue_generator import generate_clue

st.set_page_config(page_title="📘 AI Wordl from PDF", layout="wide")
st.title("📘 AI Wordl from PDF")

SCORES_FILE = "scores.csv"
PRELOADED_PDFS = {
    "🧀 Fast Food Trivia": "trivia_pdfs/fastfood_trivia.pdf",
    "🌍 General Knowledge Trivia": "trivia_pdfs/general_knowledge_trivia.pdf",
}

# Session state defaults
for key in [
    "target_word", "clue", "chunks", "attempts", "max_attempts", "game_over",
    "show_hint", "hint_level", "show_answer", "score_submitted"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "attempts" else 0 if key == "hint_level" else False if isinstance(st.session_state.get(key), bool) else ""

st.session_state.max_attempts = 6

def load_scores():
    if Path(SCORES_FILE).exists():
        try:
            return pd.read_csv(SCORES_FILE)
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=["name", "score", "word", "result"])
    return pd.DataFrame(columns=["name", "score", "word", "result"])

def save_score(name, score, word, result):
    df = load_scores()
    new_entry = pd.DataFrame([{
        "name": name,
        "score": score,
        "word": word,
        "result": result
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(SCORES_FILE, index=False)

st.sidebar.title("📚 Choose Trivia Game")
use_uploaded = st.sidebar.checkbox("Upload your own PDF")
selected_file = None

if use_uploaded:
    uploaded_file = st.sidebar.file_uploader("📄 Upload a PDF to start", type=["pdf"])
    if uploaded_file and st.sidebar.button("▶ Start Game"):
        selected_file = uploaded_file
else:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧀 Fast Food Trivia"):
            with open(PRELOADED_PDFS["🧀 Fast Food Trivia"], "rb") as f:
                selected_file = io.BytesIO(f.read())
    with col2:
        if st.button("🌍 General Knowledge Trivia"):
            with open(PRELOADED_PDFS["🌍 General Knowledge Trivia"], "rb") as f:
                selected_file = io.BytesIO(f.read())

if selected_file:
    with st.spinner("Processing PDF..."):
        full_text = extract_text_from_pdf(selected_file)
        chunks = chunk_text(full_text)
        chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
        st.session_state.chunks = chunks

        if not chunks:
            st.error("❌ No valid content found in PDF.")
            st.stop()

        upsert_chunks(chunks)

        answers = re.findall(r"A:\s*([a-zA-Z]{5})\b", full_text)
        words = [ans.upper() for ans in answers if ans.isalpha()]

        if not words:
            st.error("❌ No valid 5-letter answers found in the PDF.")
            st.stop()

        st.session_state.target_word = random.choice(words)
        context_chunks = query_chunks(st.session_state.target_word)
        st.session_state.clue = generate_clue(st.session_state.target_word, context_chunks)
        st.success("🎯 Game Ready!")

COLORS = {"🟩": "#4CAF50", "🟨": "#FFC107", "⬜": "#9E9E9E"}

def render_feedback(guess, feedback):
    blocks = "".join(
        f"<span style='display:inline-block;width:35px;height:35px;margin:2px;background-color:{COLORS[c]};text-align:center;line-height:35px;color:white;font-weight:bold;border-radius:4px;'>{g}</span>"
        for g, c in zip(guess, feedback)
    )
    st.markdown(blocks, unsafe_allow_html=True)

if st.session_state.clue and not st.session_state.game_over:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🧠 Clue")
        st.info(st.session_state.clue)

        guess = st.text_input("🔡 Enter your guess (5 letters):").upper()
        submit_col1, submit_col2 = st.columns([1, 1])
        with submit_col1:
            if st.button("✅ Submit") and guess:
                target = st.session_state.target_word
                feedback = []
                for i in range(len(target)):
                    if i < len(guess):
                        if guess[i] == target[i]:
                            feedback.append("🟩")
                        elif guess[i] in target:
                            feedback.append("🟨")
                        else:
                            feedback.append("⬜")
                    else:
                        feedback.append("⬜")
                st.session_state.attempts.append((guess, feedback))
                if guess == target:
                    st.success("🎉 Correct!")
                    st.session_state.game_over = True
                elif len(st.session_state.attempts) >= st.session_state.max_attempts:
                    st.error(f"❌ Game Over. Word was: {target}")
                    st.session_state.game_over = True

        with submit_col2:
            if st.button("❌ Give Up"):
                st.session_state.show_answer = True
                st.session_state.game_over = True

        if st.session_state.show_answer:
            st.warning(f"The word was: **{st.session_state.target_word}**")

        if st.session_state.attempts:
            st.markdown("### 🔁 Attempts")
            for g, f in st.session_state.attempts:
                render_feedback(g, f)

    with col2:
        st.subheader("💡 Hints")
        if st.button("🔍 Reveal Hint") and st.session_state.hint_level < 4:
            st.session_state.hint_level += 1
        if st.session_state.hint_level >= 1:
            st.markdown(f"🔠 First Letter: **{st.session_state.target_word[0]}**")
        if st.session_state.hint_level >= 2:
            st.markdown(f"📏 Word Length: **{len(st.session_state.target_word)}**")
        if st.session_state.hint_level >= 3:
            pos = random.randint(1, len(st.session_state.target_word)-1)
            st.markdown(f"🧩 Letter {pos+1}: **{st.session_state.target_word[pos]}**")
        if st.session_state.hint_level == 4:
            extra_hint = generate_clue(
                st.session_state.target_word,
                query_chunks(st.session_state.target_word)
            )
            st.markdown(f"🧠 Bonus Hint: *{extra_hint}*")

if st.session_state.game_over and not st.session_state.score_submitted:
    st.subheader("🏁 Submit Your Score")
    name = st.text_input("Name:")
    if st.button("💾 Save Score"):
        if name:
            score = st.session_state.max_attempts - len(st.session_state.attempts)
            result = "Win" if not st.session_state.show_answer else "Pass"
            save_score(name, score, st.session_state.target_word, result)
            st.session_state.score_submitted = True
            st.success("✅ Score saved!")
        else:
            st.warning("Please enter your name to save score.")

st.markdown("### 🏆 Leaderboard")
scores = load_scores()
if not scores.empty:
    scores = scores.sort_values(by="score", ascending=False)
    st.dataframe(scores.head(10), use_container_width=True)
else:
    st.info("No scores yet. Upload a PDF and start playing!")

if st.session_state.game_over:
    play_col1, play_col2 = st.columns(2)
    with play_col1:
        if st.button("🔁 Play Again"):
            for key in ["target_word", "clue", "attempts", "game_over", "hint_level", "show_hint", "show_answer", "score_submitted"]:
                st.session_state[key] = [] if key == "attempts" else 0 if key == "hint_level" else False if isinstance(st.session_state.get(key), bool) else ""
            st.rerun()
    with play_col2:
        if st.button("📄 Upload New PDF"):
            st.session_state.clear()
            st.rerun()
