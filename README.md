
# 📘 PDF Wordl Game (AI-Powered)

This is an interactive Wordle-style game powered by AI. Instead of guessing random words, the game extracts 5-letter answers from trivia-style PDFs and gives you context-based clues using GPT. Play with preloaded trivia or upload your own.

## ✨ Features

- Upload your own trivia-style PDFs or choose from preloaded ones  
- Extracts valid 5-letter answers based on the pattern `A: XXXXX`  
- AI-generated clues based on PDF context using GPT-4  
- Hint system with up to 4 progressive clues  
- Give Up button reveals the answer  
- Leaderboard to save and view top scores  
- Clean, bordered UI with structured layout  
- Play Again and Upload New PDF options after each game  

## 🗂️ Project Structure

- `app.py` — Main Streamlit app file  
- `utils/` — Contains helper scripts:
  - `pdf_loader.py` — Extracts and chunks PDF text  
  - `embed_store.py` — Handles Pinecone embeddings and query  
  - `clue_generator.py` — Uses OpenAI API to generate hints  
- `trivia_pdfs/` — Folder with preloaded PDFs:
  - `fastfood_trivia.pdf`  
  - `general_knowledge_trivia.pdf`  
- `scores.csv` — Stores user scores for leaderboard  
- `requirements.txt` — Python dependencies  

## 🚀 How to Run

1. Clone the repository  
2. Set up and activate a Python virtual environment  
3. Install dependencies from `requirements.txt`  
4. Set your OpenAI API key as an environment variable  
5. Run the app using Streamlit

## 🧠 How It Works

- Extracts all 5-letter answers matching the pattern `A: XXXXX` from the PDF  
- Sends the selected answer and surrounding context to GPT to generate a clue  
- Tracks guesses, provides color-coded feedback (green, yellow, gray)  
- Allows optional hints including letter reveals and bonus clue  
- Saves the score to `scores.csv` along with player name and outcome  

## 📚 Sample PDFs Included

- 🧀 Fast Food Trivia  
- 🌍 General Knowledge Trivia  

You can add more trivia PDFs to the `trivia_pdfs/` folder and link them in the app.

## 🏁 Game Flow

1. Upload a PDF or select a preloaded trivia  
2. Game extracts possible words and selects one randomly  
3. You get a GPT-generated clue to begin guessing  
4. Use hints if needed (up to 4 allowed)  
5. Guess the word within 6 attempts  
6. Submit your name to save score and view leaderboard  

---

Feel free to customize the UI and add more trivia content.  
Happy guessing! 🎯✨
