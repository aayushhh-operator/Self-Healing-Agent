import streamlit as st
import json
import time
import sys
import os
from dotenv import load_dotenv

# Add src to sys.path so the package is discoverable
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from self_verifying_agent.graph import stream_self_verifying_agent

load_dotenv()

st.set_page_config(page_title="Self-Healing Agent", layout="wide")

# Custom CSS for ChatGPT-like appearance
st.markdown("""
    <style>
    .stChatMessage {
        max-width: 80%;
        color: black !important;
    }
    .stChatMessage p {
        color: black !important;
    }
    .stChatMessage:nth-child(even) {
        align-self: flex-start;
    }
    .stChatMessage:nth-child(odd) {
        align-self: flex-end;
        background-color: #f0f2f6;
        border-radius: 10px;
    }
    .report-container {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin-top: 20px;
    }
    /* Style the chat input box and text */
    [data-testid="stChatInput"] textarea {
        background-color: black !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 AutoMend AI")
st.caption("Self-Healing Code Agent")

# Initialize session state for chat history and agent state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent_results" not in st.session_state:
    st.session_state.agent_results = {}

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    max_iters = st.slider("Max Self-Repair Iterations", 1, 10, 3)
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.agent_results = {}
        st.rerun()

# Chat input
if prompt := st.chat_input("What would you like me to build?"):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Agent response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = "I'm working on it! I'll parse your specification, generate code, and verify it with tests."
        message_placeholder.markdown(f"<span style='color:black'>{full_response}▌</span>", unsafe_allow_html=True)
        
        # Progress bar and status
        status_text = st.empty()
        progress_bar = st.progress(0)
        
        # Container for live updates below the chat
        results_container = st.container()

        # Run the agent
        results = {
            "parsed_spec": None,
            "code": None,
            "tests": None,
            "error_analysis": None,
            "iteration": 0
        }

        # Track steps for progress bar
        steps = ["spec_parser", "code_generator", "test_generator", "test_runner", "failure_analyzer", "code_fixer"]
        total_steps = len(steps)
        current_step_idx = 0

        try:
            for node_name, state_update in stream_self_verifying_agent(prompt, max_iterations=max_iters):
                results.update(state_update)
                
                # Update status and progress
                status_text.markdown(f"<span style='color:black'>Current Phase: {node_name.replace('_', ' ').title()}...</span>", unsafe_allow_html=True)
                if node_name in steps:
                    current_step_idx = steps.index(node_name)
                    progress_bar.progress((current_step_idx + 1) / total_steps)

                # Live preview in the results container
                with results_container:
                    cols = st.columns(2)
                    with cols[0]:
                        if results.get("code"):
                            st.markdown("<h3 style='color:black'>Implementation</h3>", unsafe_allow_html=True)
                            st.code(results["code"], language="python")
                    with cols[1]:
                        if results.get("tests"):
                            st.markdown("<h3 style='color:black'>Unit Tests</h3>", unsafe_allow_html=True)
                            st.code(results["tests"], language="python")

                    if results.get("error_analysis"):
                        st.markdown("<h3 style='color:black'>Analysis / Logs</h3>", unsafe_allow_html=True)
                        st.json(results["error_analysis"])

                time.sleep(0.1) # Small delay for visual effect

            full_response = "Done! I've generated the code and verified it. You can see the details below."
            message_placeholder.markdown(f"<span style='color:black'>{full_response}</span>", unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.session_state.agent_results = results
            
            status_text.markdown("<span style='color:black'>Task Complete!</span>", unsafe_allow_html=True)
            progress_bar.progress(1.0)

        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Final Results Section (always visible if results exist)
if st.session_state.agent_results:
    res = st.session_state.agent_results
    st.divider()
    st.header("Final Output")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Code", "Tests", "Analysis", "Spec"])
    
    with tab1:
        if res.get("code"):
            st.code(res["code"], language="python")
        else:
            st.info("No code generated yet.")
            
    with tab2:
        if res.get("tests"):
            st.code(res["tests"], language="python")
        else:
            st.info("No tests generated yet.")
            
    with tab3:
        if res.get("error_analysis"):
            st.json(res["error_analysis"])
        else:
            st.info("No analysis available.")

    with tab4:
        if res.get("parsed_spec"):
            st.json(res["parsed_spec"])
        else:
            st.info("No specification parsed yet.")
