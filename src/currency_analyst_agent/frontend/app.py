import os
import streamlit as st
import requests
import time
import random

# configure the streamlit page.
st.set_page_config(page_title="💱 Currency Analyst AI", page_icon="💹", layout="centered")

# backend analyze endpoint (override in Docker / Compose via CURRENCY_API_URL).
api_url = os.getenv(
    "CURRENCY_API_URL",
    "http://localhost:8000/currency/analyze",
)

# initialize session state page.
if "page" not in st.session_state:
    st.session_state.page = "home"

# initialize session state messages.
if "messages" not in st.session_state:
    st.session_state.messages = []


# define a function to simulate streaming responses.
def stream_response(text: str):
    """Simulate a streaming effect for AI responses."""

    for word in text.split():
        yield word + " "

        time.sleep(0.05) 


# define function to render the home page.
def home_page():
    st.title("💹 Currency Analyst AI")

    st.markdown(
        """
        ### About the Project
        **Currency Analyst AI Agent** is a financial intelligence system built using **CrewAI**.  
        It fetches *real-time exchange rate data* and provides **insightful analysis** about currency relationships. 
        It does **not rely on historical data** - everything is based on the current market snapshot.

        #### 🔍 Key Features
        - Fetches live foreign exchange data  
        - Performs smart analysis with AI agents  
        - Provides tailored responses to your currency-related questions  
        - Built with **CrewAI**, **FastAPI**, and **Streamlit** for modular design  

        #### ⚙️ Architecture Overview
        - **CrewAI** manages the AI agents  
        - **FastAPI** hosts backend endpoints  
        - **Streamlit** powers this interactive chat interface  

        ---
        """,
        unsafe_allow_html=True,
    )

    st.success("Ready to chat with the AI? Click the button below to start 👇")

    # button to navigate to chat page.
    if st.button("🚀 Use the App"):
        st.session_state.page = "chat"
        st.rerun()


# define function to render the chat page.
def chat_page():
    st.title("💬 Chat with Currency Analyst AI")

    # display past chat messages from session state.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # accept user prompt (or input).
    if user_prompt := st.chat_input("Ask about currencies, trends, or forex insights..."):

        # display user message immediately.
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # save the user message to session state for display.
        st.session_state.messages.append({"role": "user", "content": user_prompt})

        # fetch ai agent response by sending a request to the backend (api url).
        with st.chat_message("assistant"):
            try:
                http_response = requests.post(
                    api_url,
                    json={"query": user_prompt},
                    headers={"Content-Type": "application/json"},
                    timeout=120,
                )
                http_response.raise_for_status()

                payload = http_response.json()
                ai_text = payload.get("response")
                if not ai_text:
                    ai_text = (
                        "⚠️ The AI agent didn't return any analysis. Please try again."
                    )

            except requests.HTTPError as e:
                detail = None
                try:
                    detail = e.response.json().get("detail")
                except Exception:
                    detail = e.response.text if e.response is not None else None
                status = e.response.status_code if e.response is not None else "unknown"
                ai_text = f"⚠️ API Error ({status}): {detail or str(e)}"

            except requests.RequestException as e:
                fallback_responses = [
                    "I'm analyzing the latest forex data...",
                    "Let's check recent currency trends together!",
                    "Gathering exchange rate insights right now...",
                ]
                ai_text = random.choice(fallback_responses) + f"\n\n(Backend error: {e})"

            # simulated streaming output.
            response_text = st.write_stream(stream_response(ai_text))

        # save the ai agent response..
        st.session_state.messages.append({"role": "assistant", "content": response_text})

    # button to navigate back to the home page.
    if st.button("🏠 Back to Home"):
        st.session_state.page = "home"

        # rerun the web app to reflect changes.
        st.rerun()



# render the appropriate page based on session state.
if st.session_state.page == "home":
    home_page()

else:
    chat_page()