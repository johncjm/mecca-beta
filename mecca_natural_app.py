# MECCA v4 - FINAL VERSION WITH CORRECT IMPORTS
import streamlit as st
import os
from mecca_natural_calls import call_openai, call_anthropic, call_google, call_perplexity
from mecca_natural_prompts import get_editorial_prompt, get_eic_synthesis_prompt

# Configure page
st.set_page_config(
    page_title="MECCA - AI Editorial Assistant",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
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
    .model-selection {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .eic-summary {
        background-color: #fff3cd;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
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
    .individual-response {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<div class="main-header">📝 MECCA</div>', unsafe_allow_html=True)

# About MECCA section (collapsible)
with st.container():
    st.markdown('<div class="about-section">', unsafe_allow_html=True)
    
    # Always visible preview
    st.markdown("""
    The **Multiple Edit and Cross-Check Assistant** aims to **HELP** writers and editors, not **REPLACE** them. It won't write or rewrite your copy; it will check facts, flag typos and other problems and make suggestions. To offset the limits of AI bots, it brings several different models into the mix. To make the results easy to digest, it assigns another bot to act as Editor in Chief and synthesize feedback.
    """)
    
    # Expandable details
    with st.expander("📖 Learn More About MECCA"):
        st.markdown("""
        **How MECCA Works:**
        
        • **GPT-4**: Comprehensive editorial analysis and writing guidance  
        • **Gemini**: Systematic issue categorization and structural feedback  
        • **Perplexity**: Real-time fact-checking with web search capabilities
        • **Claude**: Serves as Editor-in-Chief, synthesizing all feedback into actionable priorities
        
        The system provides paragraph-specific feedback for maximum actionability and adapts to your specific content requirements.
        
        **Advanced Customization Options:**
        
        **Content Type:** News, Investigation, Feature, Essay, Review, or Other - each gets specialized feedback appropriate to the format
        
        **Target Audience:** General readers, Specialists, Students, or custom audience - feedback adapts to your readers' needs
        
        **Process Stage:** Draft review, Polish/copy edit, or Fact-check focus - emphasizes different editorial priorities
        
        **Category Emphasis:** Comprehensive, Fact-checking heavy, Style focus, or Structure focus - tailors the depth and type of feedback
        
        **Style Guide:** AP, Chicago, MLA, APA, House style, or Other - ensures consistency with your publication standards
        
        **Target Length & Custom Context:** Additional guidance to help editors understand your specific needs
        
        **Best Practices for Using MECCA:**
        
        • Treat feedback as advisory - you maintain full editorial control
        • Use for drafts and revisions, not final copy editing
        • Verify all factual claims independently
        • Consider feedback in context of your publication's standards
        • Most effective for articles 200+ words with clear structure
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Writer context and options
st.markdown("## 📝 Step 1: Tell us about you and what you're working on")
st.markdown("*The models work best when they're given this kind of context. (All items are optional.)*")

# Writer role selection
writer_role = st.selectbox(
    "What describes you best?",
    ["Professional journalist", "Student journalist", "Academic writer", "Content creator", "Other writer"],
    index=0,
    help="This helps MECCA adjust the tone and depth of feedback"
)

# Options (no longer called "advanced")
col1, col2 = st.columns(2)

with col1:
    content_type = st.selectbox(
        "Content Type",
        ["News", "Investigation", "Feature", "Essay", "Review", "Other"],
        index=0
    )
    
    target_audience = st.selectbox(
        "Target Audience", 
        ["General readers", "Specialists", "Students", "Other"],
        index=0
    )
    
    process_stage = st.selectbox(
        "Process Stage",
        ["Draft review", "Polish/copy edit", "Fact-check focus"],
        index=0
    )

with col2:
    category_emphasis = st.selectbox(
        "Category Emphasis",
        ["Comprehensive", "Fact-checking heavy", "Style focus", "Structure focus"],
        index=0
    )
    
    style_guide = st.selectbox(
        "Style Guide",
        ["AP", "Chicago", "MLA", "APA", "House style", "Other"],
        index=0
    )
    
    target_length = st.text_input("Target Length (optional)", placeholder="e.g., 800 words")

custom_context = st.text_area(
    "Custom Editor Context (optional)",
    placeholder="Any specific guidance for the editorial team...",
    height=80
)

# Article input section
st.markdown("## 📄 Step 2: Your Article")

headline = st.text_input(
    "**Headline:**",
    placeholder="Enter your article headline here...",
    key="headline_input"
)

article_text = st.text_area(
    "**Article Text:**",
    placeholder="Paste your article text here for editorial review...",
    height=200,
    key="article_input"
)

# Analysis button
analyze_button = st.button(
    "🔍 Get Editorial Review",
    type="primary",
    use_container_width=True
)

# Analysis results
if analyze_button and article_text.strip():
    with st.spinner("🤖 Your editorial team is reviewing your article..."):
        
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
            "category_emphasis": category_emphasis,
            "style_guide": style_guide,
            "target_length": target_length,
            "custom_context": custom_context,
            "headline": headline,
            "writer_role": writer_role
        }
        
        # Map writer role to expected format
        role_mapping = {
            "Professional journalist": "professional",
            "Student journalist": "student", 
            "Academic writer": "other",
            "Content creator": "other",
            "Other writer": "other"
        }
        mapped_role = role_mapping.get(writer_role, "other")
        
        # Call individual models
        gpt_response = call_openai(get_editorial_prompt("gpt-4o", article_text, mapped_role, context), openai_key) if openai_key else "OpenAI API key not configured"
        gemini_response = call_google(get_editorial_prompt("gemini", article_text, mapped_role, context), google_key) if google_key else "Google API key not configured"
        perplexity_response = call_perplexity(get_editorial_prompt("perplexity", article_text, mapped_role, context), perplexity_key) if perplexity_key else "Perplexity API key not configured"
        
        # Prepare combined responses for EiC
        combined_analysis = f"""
GPT-4 Editor Response:
{gpt_response}

Gemini Editor Response:
{gemini_response}

Perplexity Fact-Checker Response:
{perplexity_response}
        """
        
        # Call Claude as Editor-in-Chief
        claude_eic_prompt = get_eic_synthesis_prompt(gpt_response, gemini_response, "", perplexity_response, mapped_role, context)
        claude_response = call_anthropic(claude_eic_prompt, combined_analysis, anthropic_key) if anthropic_key else "Anthropic API key not configured"

    # AI Disclaimer
    st.markdown("""
    <div class="ai-disclaimer">
    <strong>⚠️ Using AI Editorial Feedback Responsibly</strong><br>
    This AI-generated feedback is advisory only. The writer maintains full responsibility for fact-checking, editorial decisions, and final content. All suggestions, especially those related to factual claims, must be independently verified. MECCA serves as an editorial assistant, not a replacement for human judgment and professional editorial oversight.
    </div>
    """, unsafe_allow_html=True)

    # Editor-in-Chief Summary
    st.markdown('<div class="eic-summary">', unsafe_allow_html=True)
    st.markdown("## 📋 Editor-in-Chief Summary")
    st.markdown(claude_response)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Individual responses
    st.markdown("## 👥 Individual Editor Responses")
    st.markdown("*Click to expand individual editor feedback*")
    
    with st.expander("📝 GPT-4 Editor"):
        st.markdown(gpt_response)
    
    with st.expander("📝 Gemini Editor"):
        st.markdown(gemini_response)
    
    with st.expander("📝 Perplexity Fact-Checker"):
        st.markdown(perplexity_response)

elif analyze_button:
    st.warning("⚠️ Please enter some article text to analyze.")

# Footer
st.markdown("---")
st.markdown(
    "Built with ❤️ for writers, journalists, and students. "
    "MECCA helps improve your writing through collaborative AI feedback."
)
