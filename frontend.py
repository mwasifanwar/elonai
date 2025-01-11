import requests
import streamlit as st
from PIL import Image

# Streamlit Frontend Configuration
st.set_page_config(page_title="Chat with Elon Musk", layout="wide")

# Title and Description
st.markdown(
    """
    <div style="text-align: center;">
        <h1>🤖 Chat with Elon Musk (AI)</h1>
        <p style="color: gray;">Have a conversation with an AI impersonating Elon Musk! Ask your questions below.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Load Elon Musk's profile picture
elon_dp = "https://upload.wikimedia.org/wikipedia/commons/e/ed/Elon_Musk_Royal_Society_%28crop2%29.jpg"

# Store chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Create a chat input box
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    """
    <style>
        .chat-bubble {
            padding: 10px;
            border-radius: 15px;
            margin-bottom: 10px;
            max-width: 75%;
            font-size: 16px;
            line-height: 1.5;
        }
        .chat-bubble-user {
            background-color: #000000;
            margin-left: auto;
            margin-right: 0;
            text-align: left;
        }
        .chat-bubble-elon {
            background-color: #000000;
            margin-left: 0;
            margin-right: auto;
            text-align: left;
        }
        .chat-container {
            display: flex;
            align-items: flex-start;
            margin-bottom: 10px;
        }
        .chat-container-elon img {
            border-radius: 50%;
            width: 40px;
            height: 40px;
            margin-right: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Input box for user questions
with st.container():
    user_input = st.text_input("Ask Elon a question:", "")

# Submit Button
if st.button("Submit") and user_input.strip():
    with st.spinner("Elon is thinking..."):
        # Send user input to the Flask backend
        response = requests.post("https://elonai.onrender.com/chat", json={"question": user_input})


        if response.status_code == 200:
            data = response.json()
            text_response = data["text_response"]
            audio_response = f"http://127.0.0.1:5000{data['audio_response']}"

            # Append user input and AI response to the chat history
            st.session_state.chat_history.append(
                {"type": "user", "message": user_input}
            )
            st.session_state.chat_history.append(
                {"type": "elon", "message": text_response, "audio": audio_response}
            )
        else:
            st.error("Error communicating with the backend. Please try again.")

# Display the chat history
st.markdown("<hr>", unsafe_allow_html=True)
for chat in st.session_state.chat_history:
    if chat["type"] == "user":
        # User chat bubble
        st.markdown(
            f"""
            <div class="chat-container">
                <div class="chat-bubble chat-bubble-user">
                    {chat['message']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif chat["type"] == "elon":
        # Elon Musk's chat bubble with profile picture
        st.markdown(
            f"""
            <div class="chat-container chat-container-elon">
                <img src="{elon_dp}" alt="Elon Musk">
                <div class="chat-bubble chat-bubble-elon">
                    {chat['message']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # Audio response
        st.audio(chat["audio"])
