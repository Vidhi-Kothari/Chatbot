import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import base64

# Set Google API key
os.environ['GOOGLE_API_KEY'] = "AIzaSyBfG8ys5p9GGEVSFXWsSIwx_4TbDe7s3qU"
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

# Create the Model
model = genai.GenerativeModel('gemini-pro')
vision_model = genai.GenerativeModel('gemini-pro-vision')

st.title("Chat - Gemini Bot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Ask me anything"
        }
    ]

# Function to generate audio and return HTML for player
def generate_audio(text):
    tts = gTTS(text)
    tts.save("response.mp3")
    audio_file = open("response.mp3", "rb")
    audio_bytes = audio_file.read()
    audio_b64 = base64.b64encode(audio_bytes).decode()
    audio_html = f"""
    <audio controls>
        <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
    </audio>
    """
    return audio_html

# Display chat messages from history on app rerun
def display_chat():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                st.markdown(generate_audio(message["content"]), unsafe_allow_html=True)

# Process and store Query and Response
def llm_function(query):
    # Combine previous messages as context
    context = "\n".join([msg["role"] + ": " + msg["content"] for msg in st.session_state.messages])
    prompt = f"{context}\nuser: {query}\nassistant:"

    response = model.generate_content(prompt)

    # Displaying the Assistant Message
    with st.chat_message("assistant"):
        st.markdown(response.text)
        st.markdown(generate_audio(response.text), unsafe_allow_html=True)

    # Storing the User Message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": query
        }
    )

    # Storing the Assistant Message
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response.text
        }
    )

# Function to handle image upload and processing
def process_image(image):
    st.image(image, caption='Uploaded Image.', use_column_width=True)
    response = vision_model.generate_content(["Explain the picture?", image])

    # Displaying the Assistant Message
    with st.chat_message("assistant"):
        st.markdown(response.text)
        st.markdown(generate_audio(response.text), unsafe_allow_html=True)

    # Storing the User Message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": "Uploaded an image"
        }
    )

    # Storing the Assistant Message
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response.text
        }
    )

# Accept user input (text)
query = st.chat_input("What is up?")

# Calling the Function when Input is Provided
if query:
    # Displaying the User Message
    with st.chat_message("user"):
        st.markdown(query)

    llm_function(query)

# Accept image upload
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    process_image(image)

# Sidebar for chat history
st.sidebar.title("Chat History")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Add current chat to history
if st.button("Save Current Chat"):
    st.session_state.chat_history.append(st.session_state.messages)
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Ask me anything"
        }
    ]

# Display chat history
for i, chat in enumerate(st.session_state.chat_history):
    if st.sidebar.button(f"Chat {i + 1}"):
        st.session_state.messages = chat
        display_chat()

# Display the current chat
display_chat()
