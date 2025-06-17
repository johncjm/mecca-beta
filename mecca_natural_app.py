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
    .word-limit-notice {
        background-color: #e7f3ff;
        padding: 0.8rem;
        border-radius: 6px;
        border-left: 3px solid #1f77b4;
        margin-bottom: 1rem;
        font-size: 0.9rem;
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
        
        MECCA uses a **hybrid specialization approach** - each AI editor has a primary focus area while maintaining oversight for critical issues that could harm credibility:
        
        • **GPT-4 (Fact-Checking Lead)**: Primary focus on verification, sourcing, and accuracy. Also flags critical credibility issues in other areas.
        • **Gemini (Structure/Flow Lead)**: Primary focus on organization, clarity, and reader comprehension. Also flags critical credibility issues in other areas.
        • **Perplexity (Real-time Verification)**: Web search capabilities for current fact-checking and source verification.
        • **Claude (Editor-in-Chief)**: Synthesizes all feedback using the "embarrassment test" - prioritizing issues that would most embarrass the publication if published.
        
        **Key Features:**
        
        • **Specialized but Safe**: Each editor focuses on their strength while maintaining a safety net for critical issues
        • **Custom Context Override**: Your specific instructions always take priority over default editorial approaches
        • **Paragraph-Specific Feedback**: All suggestions reference specific paragraphs for maximum actionability
        • **Educational Support**: Student writers receive additional encouragement and teaching moments
        
        **Customization Options:**
        
        **Writer Role:** Professional journalist, Student journalist, Academic writer, Content creator - affects tone and depth of feedback
        
        **Editorial Approach:** Determines how the AI editors approach your work - copy editing focus, coaching style, newsroom standards, etc.
        
        **Content Type:** News, Investigation, Feature, Essay, Review, or Other - specialized feedback for each format
        
        **Publication Style:** Edit in the style of major publications like NYT, WSJ, etc. - matches industry standards
        
        **Category Emphasis:** What type of editing focus - fact-checking, style, structure, comprehensive
        
        **Target Audience, Process Stage, Style Guide:** Further customization for specific needs
        
        **Custom Context:** Override default editorial approaches with your specific requirements
        
        **Best Practices for Using MECCA:**
        
        • Treat feedback as advisory - you maintain full editorial control
        • Use for drafts and revisions, not final copy editing
        • Verify all factual claims independently
        • Consider feedback in context of your publication's standards
        • Most effective for articles 200+ words with clear structure
        • Use Custom Context to specify any special requirements or override default approaches
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

# Editorial approach selection
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
    
    st.markdown("**Content Type**")
    content_type = st.radio(
        "content_type_radio",
        ["Standard news article", "Investigation", "Feature", "Essay", "Review", "Other"],
        index=0,
        horizontal=True,
        label_visibility="collapsed"
    )

with col2:
    st.markdown("**Category Emphasis**")
    category_emphasis = st.radio(
        "category_emphasis_radio",
        ["Comprehensive", "Fact-checking heavy", "Style focus", "Structure focus"],
        index=0,
        help="What type of editing focus?",
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.markdown("**Target Audience**")
    target_audience = st.radio(
        "target_audience_radio",
        ["General readers", "Specialists", "Students", "Other"],
        index=0,
        horizontal=True,
        label_visibility="collapsed"
    )

# Additional options
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
    target_length = st.text_input("Target Length (optional)", placeholder="e.g., 800 words")

custom_context = st.text_area(
    "Custom Editor Context (optional)",
    placeholder='Use this space to emphasize your most important need or to give the AI models the kind of important context your editor might know -- "Fact check all names" or "Identify any \'holes\' that call for more reporting" or "The informal tone is deliberate, as this is for an internal newsletter"',
    height=80,
    help="Your custom instructions will take priority over all default editorial approaches. Use this to specify tone preferences, special requirements, or any other specific guidance for the editorial team."
)

# Article input section
st.markdown("## 📄 Step 2: Your Article")

# Word limit notice
st.markdown("""
<div class="word-limit-notice">
<strong>📊 Article Length Guidance:</strong> MECCA works best with articles up to 3,000 words. Longer pieces may be truncated during processing. For optimal results, consider reviewing longer works in sections.
</div>
""", unsafe_allow_html=True)

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
            "writer_role": writer_role,
            "editorial_role": editorial_role
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
    
    with st.expander("📝 GPT-4 Editor (Fact-Checking Lead)"):
        st.markdown(gpt_response)
    
    with st.expander("📝 Gemini Editor (Structure/Flow Lead)"):
        st.markdown(gemini_response)
    
    with st.expander("📝 Perplexity Fact-Checker (Real-time Verification)"):
        st.markdown(perplexity_response)

elif analyze_button:
    st.warning("⚠️ Please enter some article text to analyze.")

# Footer
st.markdown("---")
st.markdown(
    "Built with ❤️ for writers, journalists, and students. "
    "MECCA helps improve your writing through collaborative AI feedback."
)
