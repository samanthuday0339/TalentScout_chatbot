# TalentScout - AI Hiring Assistant Chatbot

## 1. Project Overview

TalentScout is an intelligent chatbot designed to assist with the initial screening of technology candidates. Built for the fictional "TalentScout" recruitment agency, this tool streamlines the hiring process by gathering essential candidate information and dynamically generating relevant technical questions based on the candidate's declared tech stack.

The chatbot maintains a professional, context-aware conversation, ensuring a seamless experience for the candidate while efficiently collecting key data points for recruiters.

### Key Features
* **Conversational Greeting:** Welcomes candidates and outlines the screening process.
* **Information Gathering:** Collects Full Name, Email, Phone, Years of Experience, Desired Position(s), Current Location, and Tech Stack.
* **Dynamic Question Generation:** Analyzes the candidate's tech stack and generates 3-5 tailored technical questions.
* **Context Handling:** Uses Streamlit's `session_state` to maintain a coherent, multi-turn conversation.
* **Fallback Mechanism:** Gracefully handles off-topic or unexpected inputs, guiding the user back to the screening process.
* **Graceful Exit:** Allows users to end the conversation at any time with keywords (e.g., "exit", "quit").

## 2. Technical Details

* **Programming Language:** Python 3.10+
* **Frontend Interface:** Streamlit
* **Large Language Model (LLM):** OpenAI (GPT-3.5-Turbo or GPT-4)
* **Core Libraries:** `streamlit`, `openai`

### Architecture
The application is a single-page Streamlit app. Its logic is built around a "state machine" managed by `st.session_state`.

1.  **`app.py`**: Contains all Streamlit UI components and the main application logic. It manages the conversation flow by tracking the `current_stage` in `st.session_state`.
2.  **`prompts.py`**: A modular file that stores all prompts for the LLM. This includes the system message (persona, rules) and the prompts for each stage of the conversation. This separation makes it easy to update the chatbot's dialogue without altering the core logic.
3.  **`st.session_state`**: This is the "memory" of the chatbot. We use it to store:
    * `messages`: The complete chat history.
    * `current_stage`: The candidate's current step in the flow (e.g., "gather_email").
    * `user_data`: A dictionary storing all collected information (name, email, etc.).
    * `flow`: A dictionary defining the entire conversation state machine.

## 3. Installation & Usage

### Prerequisites
* Python 3.8+
* An OpenAI API Key

### Local Setup
1.  **Clone the Repository:**
    ```bash
    git clone [YOUR_GIT_REPOSITORY_LINK]
    cd TalentScout_Chatbot
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up API Key:**
    Streamlit uses a `.streamlit/secrets.toml` file to manage secret keys.
    
    * Create a folder: `mkdir .streamlit`
    * Create the secrets file: `touch .streamlit/secrets.toml`
    * Add your API key to the `secrets.toml` file:
        ```toml
        OPENAI_API_KEY = "sk-YOUR_API_KEY_HERE"
        ```

5.  **Run the Application:**
    ```bash
    streamlit run app.py
    ```
    Open your browser and navigate to `http://localhost:8501`.

## 4. Prompt Design

Effective prompt engineering was critical to this project's success.

* **System Message (`SYSTEM_MESSAGE`):** This is the chatbot's constitution. It defines the persona ("TalentScout," professional, friendly) and, most importantly, sets **strict rules**. The "Fallback Response" and "Stay on Task" instructions prevent the LLM from deviating from its purpose, fulfilling a key requirement.

* **Stateful Prompts (`PROMPT_TEMPLATES`):** A dictionary (`PROMPT_TEMPLATES`) maps conversation stages to specific prompts. This allows for a clean, linear flow. Prompts for later stages (like `conclude`) use f-string formatting (e.g., `{name}`) to dynamically insert previously collected data, creating a personalized experience.

* **Question Generation (`generate_questions`):** This is the most complex prompt.
    * It explicitly instructs the LLM to generate "4 (four) relevant technical questions."
    * It provides the raw `{tech_stack}` as context.
    * It sets constraints: "Target a mid-level... proficiency," "Cover different aspects," and "Format the output as a clean, numbered list."
    * This "zero-shot" prompt (with a "one-shot" example in the instructions) is highly effective at getting the desired output format, which is then passed directly to the candidate.

## 5. Data Handling & Privacy

Data privacy is paramount in a hiring context.

* **Data Collection:** The chatbot only collects information explicitly defined in the requirements (Name, Email, etc.).
* **Data Storage (Simulated):** In this implementation, candidate data is stored *ephemerally* in `st.session_state`. **This data is lost when the browser tab is closed or refreshed.**
* **Simulated Backend:** After the conversation concludes, the `app.py` script prints the collected `user_data` and `questions` to the console. This simulates the action of sending this data to a secure, GDPR-compliant backend database (e.g., an internal HR system) for a recruiter to review.
* **Privacy Compliance:**
    * **Consent:** The chatbot's greeting clearly states its purpose, implying consent for data collection for that purpose.
    * **Data Minimization:** Only essential screening information is collected.
    * **Security:** Using Streamlit's `secrets.toml` prevents the API key from being hard-coded in the source code.

## 6. Challenges & Solutions

* **Challenge:** Maintaining conversation context in Streamlit, which re-runs the entire script on every interaction.
    * **Solution:** Extensive use of `st.session_state`. By storing the `current_stage`, `messages`, and `user_data` in the session, we create a persistent "memory" for the chatbot across re-runs.

* **Challenge:** Forcing the LLM to follow a strict, linear conversation and not get sidetracked by the user.
    * **Solution:** A strong `SYSTEM_MESSAGE`. By explicitly ordering the LLM to "Stay on Task" and providing a "Fallback Response" for off-topic inputs, we create guardrails that keep the conversation on track. The application logic (the state machine) also enforces this, as it only knows how to move to the *next* logical step.

* **Challenge:** Parsing the LLM's output for technical questions.
    * **Solution:** Instead of complex parsing (like regex or JSON), the prompt for `generate_questions` instructs the LLM to format its output as a "clean, numbered list" and to "NOT add any other text." This makes the LLM do the formatting work, and the clean string can be directly embedded in the final conclusion message.