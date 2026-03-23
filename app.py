import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Set the page configuration
st.set_page_config(
    page_title="Hire an AI Assistant for Free",
    page_icon=":robot_face:",
    layout="wide",
    initial_sidebar_state="expanded",
    )

# Define the model
MODEL = "gpt-5.2"

# Main content
st.title("Hire an AI Assistant for Free 🤖")
st.write("Learn NotebookLM to save 10 hours a week on your work. 📚")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vector_store_id" not in st.session_state:
    st.session_state.vector_store_id = None
if "previous_response" not in st.session_state:
    st.session_state.previous_response = None
if "previous_response_id" not in st.session_state:
    st.session_state.previous_response_id = None

# Function to load the vector store
def load_vector_store():
    """Load the vector store id from the .env file. Then fallback to streamlit secrets."""
    
    try:
        vector_store_id = os.getenv("VECTOR_STORE_ID")

        if not vector_store_id:
            try:
                vector_store_id = st.secrets["VECTOR_STORE_ID"]
            except Exception:
                pass

        if not vector_store_id:
            st.error("No vector store id found. Please set the VECTOR_STORE_ID environment variable or Streamlit secrets. 🔑")
            return None
    
        return vector_store_id
    except Exception as e:
        st.error(f"Error loading vector store: {e} ⚠️")
        return None

# Define the initial message
INITIAL_MESSAGE = """
You are a helpful assistant that can answer questions and help with tasks.
"""

# Define the instructions
INSTRUCTIONS = """
# SYSTEM_PROMPT: The Manuscript Mentor

You are The Manuscript Mentor, a precision-focused Book Editor for the manuscript stored in the Vector Store. Your goal is to help the author refine, audit, and navigate their work with professional clarity. 

Be concise, direct, and practical. Use active voice. No fluff.

### Primary Objective
* Analyze and edit the manuscript using only the provided Vector Store (chapters, drafts, outlines, and style guides).
* Prioritize retrieved text over general literary knowledge. If the files don't contain a specific scene or character detail, state that clearly.
* Focus on narrative consistency, structural integrity, pacing, and character development.

### Retrieval & Citations
* Always use File Search first to locate specific passages or plot points.
* Ground every editorial critique in retrieved snippets from the manuscript.
* Gap Identification: If a requested detail (e.g., a character's eye color or a sub-plot resolution) isn't found, say: "I don't see this in the current manuscript." Then suggest where that detail might be missing in the narrative arc.
* Clean Output: Never include source citations or reference labels in the final answer text.

### Editorial Style
* Scannable Feedback: Use short paragraphs, bulleted critiques, and "Before/After" examples for prose refinement.
* Structural Logic: When suggesting a developmental change, outline the impact across the Arc → Beat → Scene → Sentence levels before providing specific edits.
* Tone: Stay professional, encouraging, and focused on the craft. You are a partner in the creative process.

### Boundaries
* No Hallucinations: Don't invent characters, plot twists, or backstory elements not present in the files.
* Scope: If asked about publishing contracts or marketing (unless those notes are in the store), acknowledge the gap and redirect the focus back to the manuscript’s content.
* Stability: Never invent chapter numbers or titles. Use the names exactly as they appear in the corpus.

### Context: Editorial Focus
* Developmental Editing: Pacing, stakes, and thematic resonance.
* Copy Editing: Identifying repetitive syntax, passive voice, and tonal inconsistencies.
* Continuity: Tracking character movements, timelines, and world-building rules.

Close each reply with a friendly follow-up question the author might ask next.
"""

# Build the ask bot function
def ask_bot(user_prompt:str):
    """Send questions to OpenAI and get responses."""
    common_kwargs = {
        "model": MODEL,
        "tools": [
        {
            "type": "file_search",
            "vector_store_ids": [st.session_state.vector_store_id],
            "max_num_results": 20
        }
    ],
        "text": {"verbosity": "low"},
        "instructions": INSTRUCTIONS
    }


    if st.session_state.previous_response_id:
        resp = client.responses.create(
            previous_response_id=st.session_state.previous_response_id,
            input = [{"role": "user", "content": user_prompt}],
            **common_kwargs
        )
    else:
        resp = client.responses.create(
            input = [
                {"role": "system", "content": INITIAL_MESSAGE.strip()},
                {"role": "user", "content": user_prompt}],
            **common_kwargs
        )

    st.session_state.previous_response_id = resp.id
    return resp.output_text

# Build function to reset the conversation
def reset_conversation():
    """Reset the conversation state."""
    st.session_state.messages = [{
        "role": "assistant",
        "content": INITIAL_MESSAGE.strip()
    }]
    st.session_state.previous_response_id = None
    st.rerun()

def main():
    # Sidebar for configuration
    with st.sidebar:
        st.header("Settings ⚙️")
        if st.button("Reset conversation 🔄"):
            reset_conversation()

    # Load the vector store
    if not st.session_state.vector_store_id:
        st.session_state.vector_store_id = load_vector_store()

    # Initialize the messages
    if not st.session_state.messages:
        st.session_state.messages = [{
            "role": "assistant",
            "content": INITIAL_MESSAGE.strip()
        }]


    # Display the chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    
    # Chat input
    prompt = st.chat_input("Ask me about the book ✍️")
    if prompt:
        st.session_state.messages.append(
            {"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)


        # Process user input
        with st.chat_message("assistant"):
            with st.spinner("Thinking... 💭"):
                response = ask_bot(prompt)
            st.markdown(response)
        st.session_state.messages.append(
            {"role": "assistant", "content": response})

if __name__ == "__main__":
    main()

