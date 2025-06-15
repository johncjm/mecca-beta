# mmqt.py - Multi-Model Query Tool
# For sending queries to all four AI models simultaneously for comparison and collaboration

import streamlit as st
import os
from datetime import datetime
from mecca_natural_calls import call_openai_gpt4, call_anthropic_claude, call_google_gemini, call_perplexity

# Page configuration
st.set_page_config(
    page_title="MMQT - Multi-Model Query Tool",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E86AB;
        margin-bottom: 1rem;
    }
    .model-response {
        background-color: #F8F9FA;
        border: 1px solid #DEE2E6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .comparison-view {
        background-color: #FFF9E6;
        border-left: 4px solid #FFA500;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 MMQT</h1>', unsafe_allow_html=True)
    st.markdown("### Multi-Model Query Tool")
    st.markdown("*Send queries to all four AI models for comparison and collaboration*")
    
    # Query input
    st.markdown("## 📝 Your Query")
    query_text = st.text_area(
        "Enter your question, code, prompt, or request:",
        height=150,
        placeholder="Example: How can we improve the Editor-in-Chief synthesis prompt for MECCA?",
        help="This will be sent to GPT-4, Gemini, Claude, and Perplexity simultaneously"
    )
    
    # Model selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Model Selection")
        models_to_query = st.multiselect(
            "Select models to query:",
            ["GPT-4", "Gemini", "Claude", "Perplexity"],
            default=["GPT-4", "Gemini", "Claude", "Perplexity"]
        )
    
    with col2:
        st.markdown("### Display Options")
        display_mode = st.radio(
            "Response format:",
            ["Side by Side", "Sequential", "Comparison View"]
        )
        
        include_timestamp = st.checkbox("Include timestamps", value=True)
        save_responses = st.checkbox("Save to file", value=False)
    
    # Submit button
    if st.button("Query All Models", type="primary", disabled=not (query_text.strip() and models_to_query)):
        if not query_text.strip():
            st.error("Please enter a query.")
            return
        
        if not models_to_query:
            st.error("Please select at least one model.")
            return
        
        # Show progress
        with st.spinner(f"Querying {len(models_to_query)} models..."):
            responses = {}
            
            # Query each selected model
            for model in models_to_query:
                try:
                    if model == "GPT-4":
                        responses["GPT-4"] = call_openai_gpt4(query_text)
                    elif model == "Gemini":
                        responses["Gemini"] = call_google_gemini(query_text)
                    elif model == "Claude":
                        responses["Claude"] = call_anthropic_claude(query_text)
                    elif model == "Perplexity":
                        responses["Perplexity"] = call_perplexity(query_text)
                except Exception as e:
                    responses[model] = f"Error: {str(e)}"
            
            # Display results
            st.success(f"Received responses from {len(responses)} models!")
            
            # Add timestamp if requested
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if include_timestamp else None
            
            if display_mode == "Side by Side":
                display_side_by_side(responses, timestamp)
            elif display_mode == "Sequential":
                display_sequential(responses, timestamp)
            else:  # Comparison View
                display_comparison_view(responses, query_text, timestamp)
            
            # Save responses if requested
            if save_responses:
                save_to_file(query_text, responses, timestamp)
                st.success("Responses saved to mmqt_responses.txt")

def display_side_by_side(responses, timestamp=None):
    """Display responses in columns side by side"""
    st.markdown("## 🔄 Model Responses")
    
    if timestamp:
        st.markdown(f"*Query timestamp: {timestamp}*")
    
    # Create columns based on number of models
    num_models = len(responses)
    if num_models <= 2:
        cols = st.columns(num_models)
    else:
        # For 3+ models, use 2 columns and stack
        cols = st.columns(2)
    
    for i, (model, response) in enumerate(responses.items()):
        col_index = i % len(cols)
        with cols[col_index]:
            st.markdown(f"### 🤖 {model}")
            st.markdown('<div class="model-response">', unsafe_allow_html=True)
            st.markdown(response)
            st.markdown('</div>', unsafe_allow_html=True)

def display_sequential(responses, timestamp=None):
    """Display responses one after another"""
    st.markdown("## 📋 Model Responses")
    
    if timestamp:
        st.markdown(f"*Query timestamp: {timestamp}*")
    
    for model, response in responses.items():
        with st.expander(f"🤖 {model} Response", expanded=True):
            st.markdown(response)

def display_comparison_view(responses, query, timestamp=None):
    """Display responses in a comparison-focused format"""
    st.markdown("## 🔍 Comparison Analysis")
    
    if timestamp:
        st.markdown(f"*Query timestamp: {timestamp}*")
    
    # Show query for context
    st.markdown('<div class="comparison-view">', unsafe_allow_html=True)
    st.markdown("**Query:**")
    st.markdown(f"*{query}*")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display each response with analysis prompts
    for model, response in responses.items():
        st.markdown(f"### 🤖 {model}")
        st.markdown(response)
        
        # Add quick analysis buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(f"Summarize {model}", key=f"sum_{model}"):
                st.info(f"Quick summary of {model}'s key points would go here")
        with col2:
            if st.button(f"Compare to Others", key=f"comp_{model}"):
                st.info(f"Comparison analysis of {model} vs other responses would go here")
        with col3:
            if st.button(f"Rate Response", key=f"rate_{model}"):
                st.info(f"Response rating interface for {model} would go here")
        
        st.markdown("---")

def save_to_file(query, responses, timestamp=None):
    """Save query and responses to a text file"""
    filename = "mmqt_responses.txt"
    
    with open(filename, "a", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        if timestamp:
            f.write(f"TIMESTAMP: {timestamp}\n")
        f.write(f"QUERY: {query}\n")
        f.write("=" * 80 + "\n\n")
        
        for model, response in responses.items():
            f.write(f"{model.upper()} RESPONSE:\n")
            f.write("-" * 40 + "\n")
            f.write(f"{response}\n\n")
        
        f.write("\n" + "=" * 80 + "\n\n")

# Sidebar with suggested queries
def show_suggested_queries():
    st.sidebar.markdown("## 💡 Suggested Queries")
    
    suggestions = [
        "How can we improve the Editor-in-Chief synthesis prompt for MECCA?",
        "What are the strengths and weaknesses of using multiple AI models for editorial feedback?",
        "How should we structure paragraph-by-paragraph feedback for writers?",
        "What would make AI editorial feedback more useful for journalism students?",
        "Review this code: [paste code here]",
        "What features should we prioritize for the MECCA beta release?",
        "How can we improve fact-checking accuracy in AI editorial tools?",
        "What are the ethical considerations for AI-assisted journalism?"
    ]
    
    for suggestion in suggestions:
        if st.sidebar.button(suggestion, key=f"suggest_{hash(suggestion)}"):
            st.session_state.suggested_query = suggestion
    
    # Auto-fill suggested query
    if hasattr(st.session_state, 'suggested_query'):
        st.sidebar.success(f"Query suggested! Paste into main area.")

if __name__ == "__main__":
    show_suggested_queries()
    main()
