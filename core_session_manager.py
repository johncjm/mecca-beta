import streamlit as st

def initialize_session_state():
    """Initialize all session state variables for MECCA"""
    
    # Initialize dialogue history
    if 'dialogue_history' not in st.session_state:
        st.session_state.dialogue_history = []
    
    # Initialize article storage
    if 'original_article' not in st.session_state:
        st.session_state.original_article = ""
    
    # Initialize EiC summary
    if 'eic_summary' not in st.session_state:
        st.session_state.eic_summary = ""
    
    # Initialize context
    if 'context' not in st.session_state:
        st.session_state.context = {}
    
    # Track if we have analysis results to display
    if 'has_analysis' not in st.session_state:
        st.session_state.has_analysis = False
    
    # Store individual editor responses
    if 'editor_responses' not in st.session_state:
        st.session_state.editor_responses = {}
    
    # Store validation history
    if 'validation_history' not in st.session_state:
        st.session_state.validation_history = []
    
    # EiC view mode for toggle (keeping for backward compatibility)
    if 'eic_view_mode' not in st.session_state:
        st.session_state.eic_view_mode = 'full'

def reset_analysis_state():
    """Reset session state for new analysis"""
    st.session_state.dialogue_history = []
    st.session_state.has_analysis = False
    st.session_state.editor_responses = {}
    st.session_state.validation_history = []