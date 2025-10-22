import streamlit as st
import re
from textblob import TextBlob
from prompts import QUESTIONS, FALLBACK, THANK_YOU, generate_tech_questions

# --- Page Configuration ---
st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="💼", layout="centered")

# --- Custom CSS (Enhanced Dark Theme + Polished UI) ---
st.markdown("""
    <style>
        body, .main {
            background-color: #000000;
            color: white;
            font-family: 'Arial', sans-serif;
        }
        .assistant {
            background-color: #1e1e1e;
            padding: 15px;
            border-radius: 12px;
            color: #ffffff;
            font-weight: bold;
            margin-bottom: 10px;
            box-shadow: 0px 4px 10px rgba(255, 255, 255, 0.1);
        }
        .user {
            background-color: #2c2c2c;
            padding: 15px;
            border-radius: 12px;
            color: #bfbfbf;
            text-align: right;
            margin-bottom: 10px;
            box-shadow: 0px 4px 10px rgba(255, 255, 255, 0.1);
        }
        div.stButton > button {
            background-color: #333333;
            color: white;
            border-radius: 10px;
            font-weight: bold;
            border: 1px solid #555;
            padding: 10px 20px;
            transition: background-color 0.3s ease, transform 0.2s ease;
        }
        div.stButton > button:hover {
            background-color: #444444;
            transform: scale(1.05);
        }
        .stChatInput {
            background-color: #000000 !important;
            border-radius: 12px;
            border: 1px solid #333 !important;
            padding: 8px;
        }
        .stChatInput textarea {
            background-color: #121212 !important;
            color: #d3d3d3 !important; /* Changed from white to light gray */
            border-radius: 12px;
            border: 1px solid #333 !important;
            font-size: 16px;
            padding: 12px;
            transition: background-color 0.3s ease, border-color 0.3s ease;
        }
        .stChatInput textarea:focus {
            background-color: #1c1c1c !important;
            border: 1px solid #555 !important;
            color: #d3d3d3 !important; /* Ensure focus state also uses light gray */
            outline: none !important;
        }
        footer {visibility: hidden;}
        h1, p, hr {
            color: white;
            text-align: center;
        }
        .invalid-message, .sentiment-message {
            color: #ff5555;
            font-size: 14px;
            text-align: center;
            margin-top: 5px;
        }
        .sentiment-message.positive {
            color: #55ff55;
        }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("<h1 style='text-align:center; color:black;'>TalentScout Hiring Assistant 💼</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:17px;'>AI-powered partner for tech talent screening</p><hr>", unsafe_allow_html=True)

# --- Session State Setup ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "step" not in st.session_state:
    st.session_state.step = 0
if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = {}
if "tech_questions" not in st.session_state:
    st.session_state.tech_questions = []
if "tech_step" not in st.session_state:
    st.session_state.tech_step = 0
if "finished" not in st.session_state:
    st.session_state.finished = False
if "invalid_message" not in st.session_state:
    st.session_state.invalid_message = ""
if "sentiment" not in st.session_state:
    st.session_state.sentiment = ""
if "language" not in st.session_state:
    st.session_state.language = "English"

# --- Auto-start with Greeting ---
if not st.session_state.messages:
    greeting = (
        "👋 Welcome to TalentScout's AI Hiring Assistant! I'm here to screen candidates for tech roles. "
        "I'll ask for some basic information and then pose technical questions based on your tech stack. "
        "Let's get started with your full name. (Type 'exit' at any time to end the conversation.)"
    )
    st.session_state.messages.append({"role": "assistant", "text": greeting})

# --- Display Chat History ---
for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        st.markdown(f"<div class='assistant'>{msg['text']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='user'>{msg['text']}</div>", unsafe_allow_html=True)

# --- Input Validation Functions ---
def validate_input(step, user_input):
    user_input = user_input.strip()
    if step == 0:  # Name
        return bool(user_input and user_input.replace(" ", "").isalpha())
    elif step == 1:  # Email
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return bool(user_input and re.match(email_regex, user_input))
    elif step == 2:  # Phone
        phone_regex = r'^\+?1?\d{10,15}$'
        return bool(user_input and re.match(phone_regex, user_input.replace(" ", "").replace("-", "")))
    elif step == 3:  # Experience
        return bool(user_input.isdigit() and int(user_input) >= 0)
    elif step == 4:  # Position
        return bool(user_input and len(user_input) > 2)
    elif step == 5:  # Location
        return bool(user_input and len(user_input) > 2)
    elif step == 6:  # Tech stack
        return bool(user_input and len(user_input) > 2)
    return True  # Allow tech questions to pass without strict validation

# --- Sentiment Analysis ---
def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0.1:
        return "positive", "Your response sounds confident! Keep it up!"
    elif polarity < -0.1:
        return "negative", "It seems you're unsure. Feel free to provide more details!"
    else:
        return "neutral", ""

# --- Input Box ---
user_input = st.chat_input("Enter your response...")

# --- Handle Input ---
if user_input:
    user_input = user_input.strip()
    st.session_state.messages.append({"role": "user", "text": user_input})

    # --- Check for Exit Keyword ---
    if user_input.lower() == "exit":
        name = st.session_state.candidate_data.get("name", "Candidate")
        st.session_state.messages.append({"role": "assistant", "text": f"Thank you, {name}, for your time! Best of luck! 😊"})
        st.session_state.finished = True
        st.rerun()  # <--- CORRECTION 1

    # --- Sentiment Analysis ---
    sentiment, sentiment_message = analyze_sentiment(user_input)
    st.session_state.sentiment = sentiment_message

    # --- Multilingual Support (Basic Detection) ---
    if "language" in user_input.lower():
        if "spanish" in user_input.lower():
            st.session_state.language = "Spanish"
            st.session_state.messages.append({"role": "assistant", "text": "¡Entendido! Continuaremos en español. Por favor, responde a la pregunta anterior."})
        elif "french" in user_input.lower():
            st.session_state.language = "French"
            st.session_state.messages.append({"role": "assistant", "text": "Compris ! Nous continuerons en français. Veuillez répondre à la question précédente."})
        else:
            st.session_state.messages.append({"role": "assistant", "text": "Please specify a supported language (e.g., Spanish, French) or continue in English."})
        st.rerun()  # <--- CORRECTION 2

    current_step = st.session_state.step
    candidate_data = st.session_state.candidate_data

    # --- Validate Input ---
    if current_step < len(QUESTIONS) and not validate_input(current_step, user_input):
        st.session_state.invalid_message = "Invalid input, please re-enter."
        st.session_state.messages.append({"role": "assistant", "text": QUESTIONS[current_step]["text"].format(**candidate_data)})
    else:
        st.session_state.invalid_message = ""
        # --- Sequential Q&A ---
        if current_step < len(QUESTIONS):
            key = QUESTIONS[current_step]["key"]
            candidate_data[key] = user_input
            st.session_state.candidate_data = candidate_data

            st.session_state.step += 1
            if st.session_state.step < len(QUESTIONS):
                next_q = QUESTIONS[st.session_state.step]["text"].format(**candidate_data)
                st.session_state.messages.append({"role": "assistant", "text": next_q})
            else:
                st.session_state.tech_questions = generate_tech_questions(candidate_data.get("techstack", ""))
                st.session_state.messages.append({"role": "assistant", "text": "Perfect! Based on your tech stack, here are some tailored technical questions:"})
                st.session_state.messages.append({"role": "assistant", "text": st.session_state.tech_questions[0]})
        # --- Technical Questions Phase ---
        elif st.session_state.tech_step < len(st.session_state.tech_questions):
            st.session_state.tech_step += 1
            if st.session_state.tech_step < len(st.session_state.tech_questions):
                st.session_state.messages.append({"role": "assistant", "text": st.session_state.tech_questions[st.session_state.tech_step]})
            else:
                name = candidate_data.get("name", "Candidate")
                st.session_state.messages.append({"role": "assistant", "text": THANK_YOU.format(name=name)})
                st.session_state.finished = True
        else:
            st.session_state.messages.append({"role": "assistant", "text": FALLBACK})

    st.rerun()  # <--- CORRECTION 3

# --- Display Invalid Message and Sentiment Feedback ---
if st.session_state.invalid_message:
    st.markdown(f"<div class='invalid-message'>{st.session_state.invalid_message}</div>", unsafe_allow_html=True)
if st.session_state.sentiment:
    sentiment_class = "sentiment-message positive" if "confident" in st.session_state.sentiment else "sentiment-message"
    st.markdown(f"<div class='{sentiment_class}'>{st.session_state.sentiment}</div>", unsafe_allow_html=True)

# --- Restart Button ---
if st.session_state.finished:
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("🔁 Restart", on_click=lambda: st.session_state.clear())
