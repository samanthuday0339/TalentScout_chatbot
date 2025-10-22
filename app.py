import streamlit as st
import re
from textblob import TextBlob
from prompts import QUESTIONS, FALLBACK, THANK_YOU, generate_tech_questions

# --- Page Configuration ---
st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="💼", layout="centered")

# --- Custom CSS ---
st.markdown("""
<style>
body, .main { background-color: #000000; color: white; font-family: 'Arial', sans-serif; }
.assistant { background-color: #1e1e1e; padding: 15px; border-radius: 12px; color: #ffffff; font-weight: bold; margin-bottom: 10px; box-shadow: 0px 4px 10px rgba(255,255,255,0.1); }
.user { background-color: #2c2c2c; padding: 15px; border-radius: 12px; color: #bfbfbf; text-align: right; margin-bottom: 10px; box-shadow: 0px 4px 10px rgba(255,255,255,0.1); }
div.stButton > button { background-color: #333; color: white; border-radius: 10px; font-weight: bold; border: 1px solid #555; padding: 10px 20px; transition: background-color 0.3s ease, transform 0.2s ease; }
div.stButton > button:hover { background-color: #444; transform: scale(1.05); }
.stChatInput { background-color: #000 !important; border-radius: 12px; border: 1px solid #333 !important; padding: 8px; }
.stChatInput textarea { background-color: #121212 !important; color: #d3d3d3 !important; border-radius: 12px; border: 1px solid #333 !important; font-size: 16px; padding: 12px; transition: background-color 0.3s ease, border-color 0.3s ease; }
.stChatInput textarea:focus { background-color: #1c1c1c !important; border: 1px solid #555 !important; color: #d3d3d3 !important; outline: none !important; }
footer {visibility: hidden;}
.invalid-message, .sentiment-message { color: #ff5555; font-size: 14px; text-align: center; margin-top: 5px; }
.sentiment-message.positive { color: #55ff55; }
</style>
""", unsafe_allow_html=True)

# --- Initialize session state ---
for key in ["messages", "step", "candidate_data", "tech_questions", "tech_step", "finished", "invalid_message", "sentiment", "language"]:
    if key not in st.session_state:
        st.session_state[key] = {} if key == "candidate_data" else [] if key in ["messages", "tech_questions"] else False if key == "finished" else "" if key in ["invalid_message", "sentiment", "language"] else 0

# --- Auto-start greeting ---
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "text": "👋 Welcome to TalentScout's AI Hiring Assistant! I'm here to screen candidates for tech roles. "
                "Let's start with your full name. (Type 'exit' at any time to end the conversation.)"
    })

# --- Display chat history ---
for msg in st.session_state.messages:
    css_class = 'assistant' if msg["role"] == "assistant" else 'user'
    st.markdown(f"<div class='{css_class}'>{msg['text']}</div>", unsafe_allow_html=True)

# --- Input Validation ---
def validate_input(step, user_input):
    user_input = user_input.strip()
    if step == 0: return bool(user_input and user_input.replace(" ", "").isalpha())
    if step == 1: return bool(user_input and re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', user_input))
    if step == 2: return bool(user_input and re.match(r'^\+?1?\d{10,15}$', user_input.replace(" ", "").replace("-", "")))
    if step == 3: return bool(user_input.isdigit() and int(user_input) >= 0)
    if step in [4,5,6]: return bool(user_input and len(user_input) > 2)
    return True

# --- Sentiment Analysis ---
def analyze_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1: return "positive", "Your response sounds confident! Keep it up!"
    if polarity < -0.1: return "negative", "It seems you're unsure. Feel free to provide more details!"
    return "neutral", ""

# --- User Input ---
user_input = st.chat_input("Enter your response...")

# --- Handle Input ---
if user_input:
    user_input = user_input.strip()
    st.session_state.messages.append({"role": "user", "text": user_input})

    # Exit
    if user_input.lower() == "exit":
        name = st.session_state.candidate_data.get("name", "Candidate")
        st.session_state.messages.append({"role": "assistant", "text": f"Thank you, {name}! Goodbye!"})
        st.session_state.finished = True

    else:
        # Sentiment
        sentiment, sentiment_msg = analyze_sentiment(user_input)
        st.session_state.sentiment = sentiment_msg

        # Multilingual support
        if "language" in user_input.lower():
            lang_msg = "Please specify a supported language or continue in English."
            if "spanish" in user_input.lower():
                st.session_state.language = "Spanish"
                lang_msg = "¡Entendido! Continuaremos en español. Por favor, responde a la pregunta anterior."
            elif "french" in user_input.lower():
                st.session_state.language = "French"
                lang_msg = "Compris ! Nous continuerons en français. Veuillez répondre à la question précédente."
            st.session_state.messages.append({"role": "assistant", "text": lang_msg})

        current_step = st.session_state.step
        tech_step = st.session_state.tech_step
        candidate_data = st.session_state.candidate_data

        # --- Validation ---
        if current_step < len(QUESTIONS) and not validate_input(current_step, user_input):
            st.session_state.invalid_message = "Invalid input, please re-enter."
            st.session_state.messages.append({"role": "assistant", "text": QUESTIONS[current_step]["text"].format(**candidate_data)})
        else:
            st.session_state.invalid_message = ""
            # --- Personal Info Q&A ---
            if current_step < len(QUESTIONS):
                key = QUESTIONS[current_step]["key"]
                candidate_data[key] = user_input
                st.session_state.candidate_data = candidate_data
                st.session_state.step += 1

                if st.session_state.step < len(QUESTIONS):
                    st.session_state.messages.append({"role": "assistant", "text": QUESTIONS[st.session_state.step]["text"].format(**candidate_data)})
                else:
                    st.session_state.tech_questions = generate_tech_questions(candidate_data.get("techstack", ""))
                    if st.session_state.tech_questions:
                        st.session_state.messages.append({"role": "assistant", "text": "Perfect! Here are some technical questions:"})
                        st.session_state.messages.append({"role": "assistant", "text": st.session_state.tech_questions[0]})

            # --- Technical Questions ---
            elif tech_step < len(st.session_state.tech_questions):
                st.session_state.tech_step += 1
                if st.session_state.tech_step < len(st.session_state.tech_questions):
                    st.session_state.messages.append({"role": "assistant", "text": st.session_state.tech_questions[st.session_state.tech_step]})
                else:
                    name = candidate_data.get("name", "Candidate")
                    st.session_state.messages.append({"role": "assistant", "text": THANK_YOU.format(name=name)})
                    st.session_state.finished = True
            else:
                st.session_state.messages.append({"role": "assistant", "text": FALLBACK})

# --- Display Invalid Message and Sentiment ---
if st.session_state.invalid_message:
    st.markdown(f"<div class='invalid-message'>{st.session_state.invalid_message}</div>", unsafe_allow_html=True)
if st.session_state.sentiment:
    sentiment_class = "sentiment-message positive" if "confident" in st.session_state.sentiment else "sentiment-message"
    st.markdown(f"<div class='{sentiment_class}'>{st.session_state.sentiment}</div>", unsafe_allow_html=True)

# --- Restart Button ---
if st.session_state.finished:
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("🔁 Restart", on_click=lambda: st.session_state.clear())
