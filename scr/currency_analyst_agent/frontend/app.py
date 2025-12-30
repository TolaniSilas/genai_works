import streamlit as st
import requests
import time
import random

# configure the streamlit page
st.set_page_config(page_title="💱 Currency Analyst AI", page_icon="💹", layout="centered")
API_URL = "http://localhost:8000/currency/analyze"  # change when you deploy


# initialize session state.
if "page" not in st.session_state:
    st.session_state.page = "home"
if "messages" not in st.session_state:
    st.session_state.messages = []


# define a function to simulate streaming responses.
def stream_response(text: str):
    """Simulate a streaming effect for AI responses."""
    for word in text.split():
        yield word + " "
        time.sleep(0.05)  # Adjust speed if desired


# define function to render the home page.
def home_page():
    st.title("💹 Currency Analyst AI")

    st.markdown(
        """
        ## 🧠 About the Project
        **Currency Analyst AI Agent** is a financial intelligence system built using **CrewAI**.  
        It fetches *real-time exchange rate data* and provides **insightful analysis** about currency relationships. 
        It does **not rely on historical data** - everything is based on the current market snapshot.

        ### 🔍 Key Features
        - Fetches live foreign exchange data  
        - Performs smart analysis with AI agents  
        - Provides tailored responses to your currency-related questions  
        - Built with **CrewAI**, **FastAPI**, and **Streamlit** for modular design  

        ### ⚙️ Architecture Overview
        - **CrewAI** manages the AI agents  
        - **FastAPI** hosts backend endpoints  
        - **Streamlit** powers this interactive chat interface  

        ---
        """,
        unsafe_allow_html=True,
    )

    st.success("Ready to chat with the AI? Click below to start 👇")

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

    # accept user input.
    if user_prompt := st.chat_input("Ask about currencies, trends, or forex insights..."):

        # display user message immediately.
        with st.chat_message("user"):
            st.markdown(user_prompt)
        st.session_state.messages.append({"role": "user", "content": user_prompt})

        # generate or fetch ai agent response.
        with st.chat_message("assistant"):
            try:
                # Example backend call (you can later parse query → base & target)
                response = requests.get(API_URL, params={"base": "USD", "target": "EUR"})
                if response.status_code == 200:
                    ai_text = response.json().get(
                        "analysis",
                        "⚠️ The AI agent didn't return any analysis. Please try again.",
                    )

                else:
                    ai_text = f"⚠️ API Error: {response.status_code}"

            except Exception as e:
                # Fallback: use simple responses to simulate backend
                fallback_responses = [
                    "I'm analyzing the latest forex data...",
                    "Let’s check recent currency trends together!",
                    "Gathering exchange rate insights right now...",
                ]
                ai_text = random.choice(fallback_responses) + f"\n\n(Backend error: {e})"

            # simulated streaming output.
            response_text = st.write_stream(stream_response(ai_text))

        # save assistant reply.
        st.session_state.messages.append({"role": "assistant", "content": response_text})

    if st.button("🏠 Back to Home"):
        st.session_state.page = "home"
        st.rerun()



# render the appropriate page based on session state.
if st.session_state.page == "home":
    home_page()

else:
    chat_page()
