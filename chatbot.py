import streamlit as st
import sqlite3
from config import Config
from helpers.llm_helper import chat, stream_parser

# Database Setup
def init_db():
    conn = sqlite3.connect("chat_app.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_message(username, role, content):
    conn = sqlite3.connect("chat_app.db")
    c = conn.cursor()
    c.execute("INSERT INTO chats (username, role, content) VALUES (?, ?, ?)", (username, role, content))
    conn.commit()
    conn.close()

def fetch_messages(username):
    conn = sqlite3.connect("chat_app.db")
    c = conn.cursor()
    c.execute("SELECT role, content FROM chats WHERE username = ?", (username,))
    messages = c.fetchall()
    conn.close()
    return messages

def delete_account(username):
    conn = sqlite3.connect("chat_app.db")
    c = conn.cursor()
    c.execute("DELETE FROM chats WHERE username = ?", (username,))
    c.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def clear_chat_data(username):
    conn = sqlite3.connect("chat_app.db")
    c = conn.cursor()
    c.execute("DELETE FROM chats WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def download_chat_as_txt(username):
    messages = fetch_messages(username)
    chat_content = "\n".join([f"{role}: {content}" for role, content in messages])
    return chat_content

def register_user(username, password):
    conn = sqlite3.connect("chat_app.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect("chat_app.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

# Initialize database
init_db()

# Set page config and logo
st.set_page_config(page_title="Chat Application", layout="wide")
st.sidebar.image("img2.png", use_container_width=True)
st.sidebar.image("img.png", use_container_width=True)

# Authentication State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

if not st.session_state.logged_in:
    # Login and Signup  
    st.title("Welcome to SafeSpace")
    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        st.header("Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            if authenticate_user(login_username, login_password):
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")

    with tab2:
        st.header("Signup")
        signup_username = st.text_input("New Username", key="signup_username")
        signup_password = st.text_input("New Password", type="password", key="signup_password")

        if st.button("Signup"):
            if register_user(signup_username, signup_password):
                st.success("Signup successful! You can now login.")
            else:
                st.error("Username already exists. Try a different one.")

else:
    # Chat Page
    st.title("Chat Application")
    st.sidebar.markdown("### Options")
    
    # Logout
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()
    
    # Clear Chat Data
    if st.sidebar.button("Clear Chat Data"):
        clear_chat_data(st.session_state.username)
        st.session_state.messages = []
        st.success("Chat data cleared!")

    # Delete Account
    if st.sidebar.button("Delete Account"):
        delete_account(st.session_state.username)
        st.session_state.logged_in = False
        st.session_state.username = None
        st.success("Account deleted successfully!")
        st.rerun()

    # Download Chat
    if st.sidebar.button("Download Chat"):
        chat_data = download_chat_as_txt(st.session_state.username)
        st.download_button(
            label="Download Chat as .txt",
            data=chat_data,
            file_name=f"{st.session_state.username}_chat.txt",
            mime="text/plain",
        )

    st.sidebar.markdown("---")

    st.sidebar.markdown("# Chat Options")
    model = st.sidebar.selectbox('What model would you like to use?', Config.OLLAMA_MODELS)

    if "messages" not in st.session_state:
        st.session_state.messages = fetch_messages(st.session_state.username)

    MAX_CHAT_HISTORY = 20

    # Display chat history
    for message in st.session_state.messages[-MAX_CHAT_HISTORY:]:
        with st.chat_message(message[0]):
            st.markdown(message[1])

    # Collect conversation history
    conversation_history = [{"role": role, "content": content} for role, content in st.session_state.messages]
    if user_prompt := st.chat_input("How can I help you"):
        if not user_prompt.strip():  # Check for empty input
            st.warning("Please enter a valid question related to medical or mental health topics.")
        else:
            # Display user input
            with st.chat_message("user"):
                st.markdown(user_prompt)
                save_message(st.session_state.username, "user", user_prompt)

            st.session_state.messages.append(("user", user_prompt))

            with st.spinner('Generating response...'):
                # Get the chatbot's response
                llm_stream = chat(user_prompt, model=model, conversation_history=conversation_history)
                stream_output = stream_parser(llm_stream)  # Parse the stream

                # Display the chatbot's response
                with st.chat_message("assistant"):
                    st.markdown(stream_output)

                # Save the response
                st.session_state.messages.append(("assistant", stream_output))
                save_message(st.session_state.username, "assistant", stream_output)
