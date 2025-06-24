import streamlit as st
import os
from mecca_dialogue_prototype_calls import call_openai, call_anthropic, call_google, call_perplexity, enhanced_dialogue_handler
from mecca_dialogue_prototype_prompts import get_editorial_prompt, get_eic_synthesis_prompt_v3
from ui.styles import load_custom_styles
from ui.forms import render_user_context_form, render_article_input
from core.session_manager import initialize_session_state, reset_analysis_state

# Configure page
st.set_page_config(
    page_title="MECCA Interactive Prototype - AI Editorial Assistant",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
initialize_session_state()

# Load custom styles
st.markdown(load_custom_styles(), unsafe_allow_html=True)

# Main header
st.markdown('<div class="main-header">📝 MECCA Interactive Prototype</div>', unsafe_allow_html=True)

# About section with inline Learn More button
st.markdown("""
<div class="about-section">
The <strong>Multiple Edit and Cross-Check Assistant</strong> aims to <strong>HELP</strong> writers and editors, not <strong>REPLACE</strong> them. This interactive prototype adds dialogue capability - you can ask the Editor-in-Chief questions about their feedback to better understand the reasoning behind suggestions.
</div>
""", unsafe_allow_html=True)

# Inline Learn More expandable section
with st.expander("📖 Learn More About MECCA Interactive"):
    st.markdown("""
    **How MECCA Interactive Works:**
    
    MECCA uses a **hybrid specialization approach** with added dialogue capability:
    
    • **GPT-4 (Comprehensive Analysis)**: Primary focus on organization, structure, and comprehensive review
    • **Gemini (Copy Editing & Style)**: Primary focus on grammar, style, tone, and language clarity
    • **Perplexity (Fact-Checking)**: Web search capabilities for real-time verification (with reliability monitoring)
    • **Claude (Editor-in-Chief)**: Synthesizes all feedback + **answers your questions with complete transparency**
    
    **Enhanced Features:**
    
    • **Honest AI Assessment**: Shows you exactly what each AI found (including their mistakes)
    • **Educational Dialogue**: Learn why AI systems fail and how to verify their work
    • **Transparency Requirements**: EiC must quote specialists exactly, including their errors
    • **"Not an Oracle" Approach**: Teaches appropriate skepticism about AI outputs
    
    **Best Practices:**
    
    • Use dialogue to understand both AI strengths AND limitations
    • Always verify AI fact-checking independently
    • Learn from AI failures as teaching moments
    • Maintain editorial control over all decisions
    """)

# Render user context form
form_data = render_user_context_form()

# Render article input form
headline, article_text, analyze_button = render_article_input()

# Analysis results
if analyze_button and article_text.strip():
    # Reset dialogue history and analysis state for new analysis
    reset_analysis_state()
    
    with st.spinner("🤖 Your enhanced editorial team is reviewing your article..."):
        
        # Get API keys
        openai_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        anthropic_key = st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY") 
        google_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
        perplexity_key = st.secrets.get("PERPLEXITY_API_KEY") or os.getenv("PERPLEXITY_API_KEY")
        
        # Prepare context for models
        context = {
            "content_type": form_data["content_type"],
            "target_audience": form_data["target_audience"],
            "process_stage": form_data["process_stage"],
            "category_emphasis": "Comprehensive",  # Default since we removed the option
            "style_guide": form_data["style_guide"],
            "target_length": form_data["target_length"],
            "custom_context": form_data["custom_context"],
            "headline": headline,
            "writer_role": form_data["writer_role"],
            "editorial_role": form_data["editorial_role"]
        }
        
        # Store in session state for dialogue
        st.session_state.context = context
        st.session_state.original_article = f"HEADLINE: {headline}\n\n{article_text}"
        
        # Map writer role to expected format
        role_mapping = {
            "Student journalist": "student",
            "Professional journalist": "professional", 
            "Academic writer": "other",
            "Content creator": "other",
            "Other writer": "other"
        }
        mapped_role = role_mapping.get(form_data["writer_role"], "other")
        
        # Call individual models with enhanced prompts
        gpt_response = call_openai(get_editorial_prompt("gpt-4o", article_text, mapped_role, context), openai_key) if openai_key else "OpenAI API key not configured"
        gemini_response = call_google(get_editorial_prompt("gemini", article_text, mapped_role, context), google_key) if google_key else "Google API key not configured"
        perplexity_response = call_perplexity(get_editorial_prompt("perplexity", article_text, mapped_role, context), perplexity_key) if perplexity_key else "Perplexity API key not configured"
        
        # Store editor responses in session state
        st.session_state.editor_responses = {
            "gpt": gpt_response,
            "gemini": gemini_response,
            "perplexity": perplexity_response
        }
        
        # Prepare combined responses for EiC
        combined_analysis = f"""
GPT-4 Editor Response:
{gpt_response}

Gemini Editor Response:
{gemini_response}

Perplexity Fact-Checker Response:
{perplexity_response}
        """
        
        # Call Claude as Editor-in-Chief with enhanced synthesis
        claude_eic_prompt = get_eic_synthesis_prompt_v3(gpt_response, gemini_response, "", perplexity_response, mapped_role, context)
        claude_response = call_anthropic(claude_eic_prompt, combined_analysis, anthropic_key) if anthropic_key else "Anthropic API key not configured"
        
        # Store EiC response for dialogue
        st.session_state.eic_summary = claude_response
        st.session_state.has_analysis = True

elif analyze_button:
    st.warning("⚠️ Please enter some article text to analyze.")

# Display results with tabbed interface
if st.session_state.has_analysis:
    # Enhanced AI Disclaimer
    st.markdown("""
    <div class="ai-disclaimer">
    <strong>⚠️ IMPORTANT: MECCA's fact-checking is experimental and often unreliable -- as is the case currently with all AI fact-checking programs. Treat all factual claims as suggestions requiring independent verification. We strive to uncover those errors and show them to you as illustrations of AI limitations in real-time as part of our educational mission.</strong><br>
    This AI-generated feedback is advisory only and includes validation monitoring. The writer maintains full responsibility for fact-checking, editorial decisions, and final content. MECCA shows you exactly what each AI found (including their mistakes) to teach appropriate skepticism about AI verification.
    </div>
    """, unsafe_allow_html=True)

    # Step 3 header
    st.markdown('<div class="section-header">📋 Step 3: Your Editorial Feedback</div>', unsafe_allow_html=True)
    
    # Initialize tab state if not exists
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0
    
    # Create tabs for organized feedback display
    tab1, tab2, tab3 = st.tabs([
        "📋 Editor-in-Chief Overview", 
        "📝 Full Individual Responses", 
        "💬 Ask the Editor"
    ])
    
    with tab1:
        st.markdown("## 📋 Editor-in-Chief Summary")
        st.markdown("*Synthesis of all editorial feedback using the 'embarrassment test' for prioritization*")
        
        # Display EiC content directly (no parsing needed)
        st.markdown(st.session_state.eic_summary)
        
        # Navigation hints
        st.markdown("---")
        st.markdown("""
        **💡 Next Steps:**
        - Check **Full Individual Responses** tab for detailed specialist feedback
        - Use **Ask the Editor** tab to understand the reasoning behind suggestions
        - Remember: This is advisory feedback - you maintain full editorial control
        """)
    
    with tab2:
        st.markdown("## Full Individual Responses")
        st.markdown("*Compare all specialist feedback side by side - transparency is key to learning AI limitations.*")
        
        # Search bar for responses (future enhancement)
        search_query = st.text_input("🔍 Search within responses:", placeholder="Search for specific terms across all responses...", key="response_search")
        
        # Three-column layout for specialist responses
        editor_responses = st.session_state.editor_responses
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📝 GPT-4 (Comprehensive Analysis)")
            st.markdown("**Focus:** Organization, structure, comprehensive review")
            
            gpt_content = editor_responses.get("gpt", "Response not available")
            if search_query and search_query.lower() in gpt_content.lower():
                # Simple highlight effect (could be enhanced)
                st.markdown(f"🔍 *Contains: '{search_query}'*")
            st.markdown(gpt_content)
        
        with col2:
            st.markdown("#### ✏️ Gemini (Copy Editing & Style)")
            st.markdown("**Focus:** Grammar, style, language clarity")
            
            gemini_content = editor_responses.get("gemini", "Response not available")
            if search_query and search_query.lower() in gemini_content.lower():
                st.markdown(f"🔍 *Contains: '{search_query}'*")
            st.markdown(gemini_content)
        
        with col3:
            st.markdown("#### 🔍 Perplexity (Fact-Checking)")
            st.markdown("**Focus:** Web search fact-checking")
            
            perplexity_content = editor_responses.get("perplexity", "Response not available")
            if search_query and search_query.lower() in perplexity_content.lower():
                st.markdown(f"🔍 *Contains: '{search_query}'*")
            st.markdown(perplexity_content)
            st.markdown("⚠️ **Fact-checking results below can often be wrong. Notices of mistakes are not the result of a bug - it's a feature designed to teach appropriate AI skepticism.**")
    
    with tab3:
        # Set active tab when this tab is accessed
        if st.session_state.get('form_submitted', False):
            st.session_state.active_tab = 2
            st.session_state.form_submitted = False
            
        st.markdown("## 💬 Ask the Editor-in-Chief")
        st.markdown("*Ask questions about the feedback with complete transparency. The EiC will show you exactly what each specialist found, including their mistakes.*")
        
        # Display dialogue history
        for i, exchange in enumerate(st.session_state.dialogue_history):
            st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {exchange["question"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-message eic-message"><strong>Editor-in-Chief:</strong> {exchange["answer"]}</div>', unsafe_allow_html=True)
        
        # Question input form
        with st.form("dialogue_form"):
            user_question = st.text_input(
                "Ask a question about the feedback:",
                placeholder="e.g., 'Show me exactly what your fact-checker said about Mario Cuomo' or 'Which specialists missed the State Senator error?'",
                key="dialogue_question_input"
            )
            
            submitted = st.form_submit_button("Ask Question", type="primary")
            
            if submitted and user_question.strip():
                anthropic_key = st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
                if anthropic_key:
                    with st.spinner("🤔 Editor-in-Chief is thinking (with transparency validation)..."):
                        # Set flag to stay on this tab after rerun
                        st.session_state.form_submitted = True
                        
                        # Use enhanced dialogue handler with validation
                        eic_answer = enhanced_dialogue_handler(user_question, st.session_state, anthropic_key)
                        
                        # Store in dialogue history
                        st.session_state.dialogue_history.append({
                            "question": user_question,
                            "answer": eic_answer
                        })
                        
                        # Rerun to update display
                        st.rerun()
                else:
                    st.error("Anthropic API key not configured for dialogue feature.")
        
        # Educational note
        st.markdown("---")
        st.markdown("""
        **🎓 Educational Note:** The Editor-in-Chief can reference what each specialist 
        found and explain the reasoning behind editorial decisions. This dialogue helps 
        you understand not just *what* to change, but *why* changes are needed.
        """)

# Footer with enhanced messaging
st.markdown("---")
st.markdown(
    "Built with ❤️ for writers, journalists, and students. "
    "MECCA Interactive teaches both AI capabilities AND limitations through transparent feedback and honest dialogue. **Not an Oracle - but a learning tool.**"
)
