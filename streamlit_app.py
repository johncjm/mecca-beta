import streamlit as st
import os
from mecca_dialogue_prototype_calls import call_openai, call_anthropic, call_google, call_perplexity, enhanced_dialogue_handler
from mecca_dialogue_prototype_prompts import get_editorial_prompt, get_eic_synthesis_prompt_v2

# Configure page
st.set_page_config(
    page_title="MECCA Interactive Prototype - AI Editorial Assistant",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state for dialogue
if 'dialogue_history' not in st.session_state:
    st.session_state.dialogue_history = []
if 'original_article' not in st.session_state:
    st.session_state.original_article = ""
if 'eic_summary' not in st.session_state:
    st.session_state.eic_summary = ""
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
# EiC view mode for toggle
if 'eic_view_mode' not in st.session_state:
    st.session_state.eic_view_mode = 'full'

# Enhanced CSS for better styling and layout + Toggle Feature
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .about-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #1f77b4;
    }
    .learn-more-inline {
        display: inline-block;
        margin-left: 10px;
        vertical-align: top;
    }
    .section-header {
        font-size: 1.3rem;
        font-weight: bold;
        color: #333;
        margin-bottom: 0.5rem;
        margin-top: 1rem;
    }
    .radio-group {
        font-size: 0.9rem;
        color: #666;
    }
    .custom-context-container {
        margin-top: 1rem;
    }
    .fact-check-warning {
        font-style: italic;
        color: #d63384;
        font-size: 0.85rem;
        margin-top: 0.3rem;
    }
    .word-limit-notice {
        background-color: #e7f3ff;
        padding: 0.8rem;
        border-radius: 6px;
        border-left: 3px solid #1f77b4;
        margin-bottom: 1rem;
        font-size: 0.9rem;
    }
    .eic-summary {
        background-color: #fff3cd;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin-bottom: 1rem;
    }
    .dialogue-section {
        background-color: #e8f5e8;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin-bottom: 1rem;
    }
    .ai-disclaimer {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin-bottom: 1rem;
        font-size: 0.9rem;
    }
    .chat-message {
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .user-message {
        background-color: #e3f2fd;
        text-align: right;
    }
    .eic-message {
        background-color: #f1f8e9;
    }
    .specialist-columns {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 20px;
        max-height: 600px;
    }
    .specialist-column {
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        overflow-y: auto;
        background-color: #ffffff;
    }
    .specialist-column h4 {
        margin-top: 0;
        color: #1f77b4;
        border-bottom: 2px solid #e9ecef;
        padding-bottom: 0.5rem;
    }
    .search-bar {
        width: 100%;
        padding: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid #ced4da;
        border-radius: 4px;
    }
    /* Improve tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0px 0px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        border-bottom: 3px solid #1f77b4;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1rem;
    }
    
    /* EiC Toggle Styles */
    .eic-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e9ecef;
    }
    
    .eic-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #333;
        margin: 0;
    }
    
    .eic-toggle {
        display: flex;
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 4px;
        border: 1px solid #dee2e6;
    }
    
    .eic-toggle-btn {
        padding: 8px 16px;
        border: none;
        background: transparent;
        border-radius: 6px;
        font-size: 0.9rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        color: #6c757d;
    }
    
    .eic-toggle-btn.active {
        background-color: #ffffff;
        color: #1f77b4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .eic-toggle-btn:hover:not(.active) {
        color: #495057;
        background-color: #e9ecef;
    }
    
    /* Content visibility classes */
    .eic-full-content {
        display: block;
    }
    
    .eic-condensed-content {
        display: none;
    }
    
    .view-quick-fixes .eic-full-content {
        display: none;
    }
    
    .view-quick-fixes .eic-condensed-content {
        display: block;
    }
    
    /* Quick fixes styling */
    .quick-fixes-summary {
        background-color: #fff3cd;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin-bottom: 1rem;
    }
    
    .error-count-overview {
        background-color: #e7f3ff;
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
        font-size: 0.9rem;
    }
    
    .quick-fix-item {
        padding: 0.5rem 0;
        border-bottom: 1px solid #e9ecef;
    }
    
    .quick-fix-item:last-child {
        border-bottom: none;
    }
    
    .fix-severity {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
        margin-right: 8px;
    }
    
    .severity-critical {
        background-color: #f8d7da;
        color: #721c24;
    }
    
    .severity-high {
        background-color: #fff3cd;
        color: #856404;
    }
    
    .severity-medium {
        background-color: #d1ecf1;
        color: #0c5460;
    }
</style>

<script>
function toggleEiCView(mode) {
    const container = document.querySelector('.eic-container');
    const buttons = document.querySelectorAll('.eic-toggle-btn');
    
    // Remove active class from all buttons
    buttons.forEach(btn => btn.classList.remove('active'));
    
    // Add active class to clicked button
    const targetBtn = document.querySelector(`[data-mode="${mode}"]`);
    if (targetBtn) {
        targetBtn.classList.add('active');
    }
    
    // Toggle container class
    if (mode === 'quick') {
        container.classList.add('view-quick-fixes');
    } else {
        container.classList.remove('view-quick-fixes');
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Set default view to full analysis
    setTimeout(function() {
        const fullBtn = document.querySelector('[data-mode="full"]');
        if (fullBtn) {
            fullBtn.classList.add('active');
        }
    }, 100);
});
</script>
""", unsafe_allow_html=True)

def parse_eic_content(eic_response):
    """Parse EiC response to separate quick fixes from full analysis"""
    
    # Look for our structured markers
    quick_fixes_start = eic_response.find("<!-- QUICK_FIXES_START -->")
    quick_fixes_end = eic_response.find("<!-- QUICK_FIXES_END -->")
    full_analysis_start = eic_response.find("<!-- FULL_ANALYSIS_START -->")
    full_analysis_end = eic_response.find("<!-- FULL_ANALYSIS_END -->")
    
    if quick_fixes_start != -1 and quick_fixes_end != -1:
        quick_fixes_content = eic_response[quick_fixes_start+len("<!-- QUICK_FIXES_START -->"):quick_fixes_end].strip()
    else:
        # Fallback: extract Quick Fixes section manually
        lines = eic_response.split('\n')
        quick_fixes_lines = []
        in_quick_fixes = False
        
        for line in lines:
            if '🎯 QUICK FIXES NEEDED' in line:
                in_quick_fixes = True
                quick_fixes_lines.append(line)
            elif in_quick_fixes and (line.startswith('EDITORIAL SUMMARY') or line.startswith('PRIORITY ACTION LIST')):
                break
            elif in_quick_fixes:
                quick_fixes_lines.append(line)
        
        quick_fixes_content = '\n'.join(quick_fixes_lines)
    
    if full_analysis_start != -1 and full_analysis_end != -1:
        full_analysis_content = eic_response[full_analysis_start+len("<!-- FULL_ANALYSIS_START -->"):full_analysis_end].strip()
    else:
        # Fallback: use entire response
        full_analysis_content = eic_response
    
    return quick_fixes_content, full_analysis_content

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

# Writer context and options
st.markdown('<div class="section-header">📝 Step 1: Tell us about you and what you\'re working on</div>', unsafe_allow_html=True)
st.markdown("*The more the AI models know about what you're trying to do and what assistance you need, the better job they'll do in helping you.*")

# Writer role selection
writer_role = st.selectbox(
    "What describes you best?",
    ["Professional journalist", "Student journalist", "Academic writer", "Content creator", "Other writer"],
    index=0,
    help="This helps MECCA adjust the tone and depth of feedback"
)

# Editorial approach selection - 2 columns layout
col1, col2 = st.columns(2)

with col1:
    st.markdown("**How should the editors approach your work?**")
    editorial_role = st.radio(
        "editorial_role_radio",
        ["Copy Editor", "Writing Coach", "News Desk Editor", "Feature Editor", "Fact-Checker Focus", "Style Editor"],
        index=1,  # Default to Writing Coach
        help="This determines how the AI editors will focus their feedback and adopt different editorial perspectives when reviewing your work.",
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # Fact-checker warning
    if editorial_role == "Fact-Checker Focus":
        st.markdown('<div class="fact-check-warning">MECCA\'s fact-checking is experimental and often unreliable -- as is the case currently with all AI fact-checking programs. Treat all factual claims as suggestions requiring independent verification.</div>', unsafe_allow_html=True)
    
    st.markdown("**Content Type**")
    content_type = st.radio(
        "content_type_radio",
        ["Standard news article", "Investigation", "Feature", "Essay", "Review", "Other"],
        index=0,
        horizontal=True,
        label_visibility="collapsed"
    )

with col2:
    st.markdown("**Target Audience**")
    target_audience = st.radio(
        "target_audience_radio",
        ["General readers", "Specialists", "Students", "Other"],
        index=0,
        horizontal=True,
        label_visibility="collapsed"
    )

    # Move Custom Editor Context to right column
    st.markdown('<div class="custom-context-container">', unsafe_allow_html=True)
    custom_context = st.text_area(
        "**Custom Prompts** (optional)",
        placeholder='For instance, "Verify all titles" or "I\'m aiming at a breezy tone" or "Am I leaving anything important out?"',
        height=80,
        help="Use this optional space to be more specific about what you need or context that would help the AI models provide better assistance."
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Additional options row
st.markdown("**Process Stage**")
process_stage = st.radio(
    "process_stage_radio",
    ["Draft review", "Polish/copy edit", "Fact-check focus"],
    index=0,
    horizontal=True,
    label_visibility="collapsed"
)

col3, col4 = st.columns(2)

with col3:
    st.markdown("**Style Guide**")
    style_guide = st.radio(
        "style_guide_radio",
        ["AP", "Chicago", "MLA", "APA", "House style", "Other"],
        index=0,
        horizontal=True,
        label_visibility="collapsed"
    )

with col4:
    target_length = st.text_input("**Target Length** (optional)", placeholder="e.g., 800 words")

# Article input section
st.markdown('<div class="section-header">📄 Step 2: Your Article</div>', unsafe_allow_html=True)

# Simplified word limit notice
st.markdown("""
<div class="word-limit-notice">
<strong>3,000 words max.</strong> Processing may take a minute or more — do not refresh.
</div>
""", unsafe_allow_html=True)

headline = st.text_input(
    "**Headline:**",
    placeholder="Enter your article headline here...",
    key="headline_input"
)

article_text = st.text_area(
    "**Article Text:**",
    placeholder="Paste your article text here for enhanced editorial review...",
    height=200,
    key="article_input"
)

# Analysis button
analyze_button = st.button(
    "🔍 Get Enhanced Editorial Review",
    type="primary",
    use_container_width=True
)

# Analysis results
if analyze_button and article_text.strip():
    # Reset dialogue history and analysis state for new analysis
    st.session_state.dialogue_history = []
    st.session_state.has_analysis = False
    st.session_state.editor_responses = {}
    st.session_state.validation_history = []
    
    with st.spinner("🤖 Your enhanced editorial team is reviewing your article..."):
        
        # Get API keys
        openai_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        anthropic_key = st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY") 
        google_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
        perplexity_key = st.secrets.get("PERPLEXITY_API_KEY") or os.getenv("PERPLEXITY_API_KEY")
        
        # Prepare context for models
        context = {
            "content_type": content_type,
            "target_audience": target_audience,
            "process_stage": process_stage,
            "category_emphasis": "Comprehensive",  # Default since we removed the option
            "style_guide": style_guide,
            "target_length": target_length,
            "custom_context": custom_context,
            "headline": headline,
            "writer_role": writer_role,
            "editorial_role": editorial_role
        }
        
        # Store in session state for dialogue
        st.session_state.context = context
        st.session_state.original_article = f"HEADLINE: {headline}\n\n{article_text}"
        
        # Map writer role to expected format
        role_mapping = {
            "Professional journalist": "professional",
            "Student journalist": "student", 
            "Academic writer": "other",
            "Content creator": "other",
            "Other writer": "other"
        }
        mapped_role = role_mapping.get(writer_role, "other")
        
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
        
        # Call Claude as Editor-in-Chief with enhanced synthesis + toggle support
        claude_eic_prompt = get_eic_synthesis_prompt_v2(gpt_response, gemini_response, "", perplexity_response, mapped_role, context)
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
    
    # Create tabs for organized feedback display
    tab1, tab2, tab3 = st.tabs([
        "📋 Editor-in-Chief Overview", 
        "📝 Full Individual Responses", 
        "💬 Ask the Editor"
    ])
    
    with tab1:
        # EiC Header with Toggle
        st.markdown("""
        <div class="eic-header">
            <h2 class="eic-title">📋 Editor-in-Chief Summary</h2>
            <div class="eic-toggle">
                <button class="eic-toggle-btn" data-mode="full" onclick="toggleEiCView('full')">
                    📚 Full Analysis
                </button>
                <button class="eic-toggle-btn" data-mode="quick" onclick="toggleEiCView('quick')">
                    📝 Quick Fixes
                </button>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("*Synthesis of all editorial feedback using the 'embarrassment test' for prioritization*")
        
        # EiC content container with toggle classes
        st.markdown('<div class="eic-container">', unsafe_allow_html=True)
        
        # Parse the EiC response to separate quick fixes from full analysis
        eic_content = st.session_state.eic_summary
        quick_fixes_content, full_analysis_content = parse_eic_content(eic_content)
        
        # Quick Fixes Content (hidden by default)
        st.markdown('<div class="eic-condensed-content">', unsafe_allow_html=True)
        st.markdown('<div class="quick-fixes-summary">', unsafe_allow_html=True)
        st.markdown(quick_fixes_content)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Full Analysis Content (visible by default)  
        st.markdown('<div class="eic-full-content">', unsafe_allow_html=True)
        st.markdown(full_analysis_content)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close eic-container
        
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
        st.markdown('<div class="specialist-columns">', unsafe_allow_html=True)
        
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
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown("## 💬 Ask the Editor-in-Chief")
        st.markdown("*Ask questions about the feedback with complete transparency. The EiC will show you exactly what each specialist found, including their mistakes.*")
        
        # Display dialogue history (FIXED ORDER: Question first, then answer)
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
