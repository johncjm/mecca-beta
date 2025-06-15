# mecca_natural_app.py
# Enhanced Streamlit interface with advanced options for targeted editorial feedback
# AI-Powered Editorial Team Simulator

import streamlit as st
from mecca_natural_calls import get_complete_editorial_review, test_api_connections
from mecca_natural_prompts import get_model_display_name

# Page configuration
st.set_page_config(
    page_title="MECCA - AI Editorial Team",
    page_icon="🗞️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2E86AB;
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #FFF3CD;
        border: 1px solid #FFEAA7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .eic-summary {
        background-color: #E8F4FD;
        border-left: 4px solid #2E86AB;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    .model-response {
        background-color: #F8F9FA;
        border: 1px solid #DEE2E6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .advanced-section {
        background-color: #F8F9FA;
        border: 1px solid #DEE2E6;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🗞️ MECCA</h1>', unsafe_allow_html=True)
    st.markdown("### Multiple Edits and Cross Check App")
    st.markdown("*AI-Powered Editorial Team Simulator*")
    
    # Warning box about AI limitations
    st.markdown("""
    <div class="warning-box">
        <h4>⚠️ Using AI Editorial Feedback Responsibly</h4>
        <ul>
            <li><strong>This is advisory, not authoritative</strong> - Use these suggestions as a starting point for your own editorial judgment</li>
            <li><strong>Fact-checking limitations</strong> - AI models can have outdated information, make confident but incorrect claims, or miss nuances. Always verify important facts independently</li>
            <li><strong>You remain responsible</strong> - Final decisions about content, accuracy, and publication rest with human reporters and editors</li>
            <li><strong>Context matters</strong> - AI doesn't understand your publication's style, audience, or editorial priorities the way you do</li>
            <li><strong>When in doubt, check</strong> - Treat AI suggestions as a "second opinion" that still requires professional verification</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for setup and instructions
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("## 📝 Setup")
        
        # Writer role selection
        st.markdown("**Writer Role:**")
        writer_role = st.selectbox(
            "Choose your role",
            ["Professional Journalist", "Student", "Other Writer"],
            key="writer_role"
        )
        
        # Convert display names to internal values
        role_mapping = {
            "Professional Journalist": "professional",
            "Student": "student", 
            "Other Writer": "other"
        }
        selected_role = role_mapping[writer_role]
        
        # Required: Content Type
        st.markdown("**Content Type:** *")
        content_type = st.selectbox(
            "What type of content are you working on?",
            ["News Article", "Investigation", "Feature", "Essay", "Review", "Other"],
            key="content_type"
        )
        
        st.markdown("### Editorial Team")
        st.markdown("**Choose up to 3 editors:**")
        
        # Model selection with defaults
        selected_editors = []
        
        # Create checkboxes for each model
        gpt4_selected = st.checkbox("GPT-4O - Comprehensive editorial analysis", value=True, key="gpt4")
        gemini_selected = st.checkbox("Gemini - Systematic issue categorization", value=True, key="gemini") 
        perplexity_selected = st.checkbox("Perplexity - Real-time fact-checking", value=True, key="perplexity")
        
        # Add to selected list
        if gpt4_selected:
            selected_editors.append("gpt-4o")
        if gemini_selected:
            selected_editors.append("gemini")
        if perplexity_selected:
            selected_editors.append("perplexity")
        
        # Show count and limit info
        editor_count = len(selected_editors)
        if editor_count > 3:
            st.warning("⚠️ Please select a maximum of 3 editors. Currently selected: " + str(editor_count))
        elif editor_count == 0:
            st.info("ℹ️ Select at least 1 editor to proceed.")
        
        # Show selected editors
        if selected_editors and editor_count <= 3:
            editor_names = [get_model_display_name(model) for model in selected_editors]
            st.success(f"Selected: {', '.join(editor_names)}")
        
        # Editor-in-Chief info
        st.markdown("**Editor-in-Chief:** Claude (synthesizes all feedback)")
    
    with col2:
        st.markdown("## 📋 Editorial Feedback")
        
        # Instructions
        st.markdown("### How MECCA works:")
        st.markdown("""
        1. **Choose your role** - Student, Professional, or Other Writer
        2. **Select content type** - Helps tailor feedback appropriately
        3. **Choose AI editors** - Each brings different editorial strengths  
        4. **Customize options** - Target the feedback to your specific needs
        5. **Get synthesis** - Editor-in-Chief combines all feedback into actionable guidance
        """)
        
        # Advanced Options Section
        st.markdown('<div class="advanced-section">', unsafe_allow_html=True)
        
        with st.expander("⚙️ Advanced Options", expanded=False):
            st.markdown("**Customize your editorial feedback:**")
            
            # Target Audience
            target_audience = st.selectbox(
                "Target Audience:",
                ["General readers", "Subject specialists", "Students", "Other"],
                key="target_audience"
            )
            
            # Process Stage
            process_stage = st.selectbox(
                "Process Stage:",
                ["Draft review", "Polish/copy edit", "Fact-check focus"],
                key="process_stage"
            )
            
            # Category Focus
            category_focus = st.selectbox(
                "Category Focus:",
                ["Comprehensive review", "Fact-checking heavy", "Style focus", "Structure focus"],
                key="category_focus"
            )
            
            # Style Guide
            style_guide = st.selectbox(
                "Style Guide:",
                ["AP", "Chicago", "MLA", "APA", "House style", "Other"],
                key="style_guide"
            )
            
            # Target Length
            target_length = st.text_input(
                "Target Length (optional):",
                placeholder="e.g., 800 words, 2-3 pages, brief summary",
                key="target_length"
            )
            
            # Context Box
            editor_context = st.text_area(
                "What should the editors know? (optional):",
                placeholder="e.g., This is for a specific publication, deadline constraints, particular concerns to focus on...",
                height=80,
                key="editor_context"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("Complete the setup on the left to get started.")
    
    # Article input
    st.markdown("### Article")
    
    # Headline input
    st.markdown("**Headline:**")
    headline_text = st.text_input(
        "Article headline:",
        placeholder="Enter your article headline here...",
        label_visibility="collapsed"
    )
    
    st.markdown("**Article Text:**")
    article_text = st.text_area(
        "Article text:",
        height=200,
        placeholder="Paste your article text here for editorial review...",
        label_visibility="collapsed"
    )
    
    # Submit button
    can_submit = (article_text.strip() and 
                  selected_editors and 
                  len(selected_editors) <= 3)
    
    if st.button("Get Editorial Review", type="primary", disabled=not can_submit):
        if not article_text.strip():
            st.error("Please paste an article to review.")
            return
        
        if not selected_editors:
            st.error("Please select at least one editor.")
            return
            
        if len(selected_editors) > 3:
            st.error("Please select a maximum of 3 editors.")
            return
        
        # Prepare advanced options context
        advanced_options = {
            "content_type": content_type,
            "target_audience": target_audience,
            "process_stage": process_stage,
            "category_focus": category_focus,
            "style_guide": style_guide,
            "target_length": target_length if target_length.strip() else None,
            "editor_context": editor_context if editor_context.strip() else None,
            "headline": headline_text.strip() if headline_text.strip() else None
        }
        
        # Show progress
        with st.spinner("Getting editorial feedback..."):
            try:
                # Get the complete review
                results = get_complete_editorial_review(
                    article_text, 
                    selected_editors, 
                    selected_role,
                    advanced_options=advanced_options
                )
                
                # Display results
                st.success("Editorial review complete!")
                
                # Editor-in-Chief Summary (prominent display)
                st.markdown('<div class="eic-summary">', unsafe_allow_html=True)
                st.markdown("## **📋 Editor-in-Chief Summary**")
                st.markdown(results["eic_synthesis"])
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Individual editor responses (expandable)
                st.markdown("## 👥 Individual Editor Responses")
                st.markdown("*Click to expand individual editor feedback*")
                
                for model_key, response in results["individual_responses"].items():
                    model_name = get_model_display_name(model_key)
                    
                    with st.expander(f"📝 {model_name}"):
                        st.markdown(response)
                
                # Session metadata (collapsed)
                with st.expander("ℹ️ Session Details"):
                    st.markdown(f"**Writer Role:** {writer_role}")
                    st.markdown(f"**Content Type:** {content_type}")
                    st.markdown(f"**Target Audience:** {target_audience}")
                    st.markdown(f"**Process Stage:** {process_stage}")
                    st.markdown(f"**Category Focus:** {category_focus}")
                    st.markdown(f"**Style Guide:** {style_guide}")
                    if headline_text:
                        st.markdown(f"**Headline:** {headline_text}")
                    if target_length:
                        st.markdown(f"**Target Length:** {target_length}")
                    if editor_context:
                        st.markdown(f"**Additional Context:** {editor_context}")
                    st.markdown(f"**Editors Used:** {', '.join([get_model_display_name(m) for m in selected_editors])}")
                    st.markdown(f"**Editor-in-Chief:** Claude")
                    st.markdown(f"**Article Length:** {len(article_text.split())} words")
                
            except Exception as e:
                st.error(f"Error getting editorial review: {str(e)}")
                st.info("Please check your internet connection and API keys.")
    
    # Sidebar with additional info
    with st.sidebar:
        st.markdown("## About MECCA")
        st.markdown("""
        MECCA simulates a real editorial team by using multiple AI models, 
        each bringing different strengths:
        
        - **GPT-4O**: Comprehensive editorial analysis and writing guidance
        - **Gemini**: Systematic issue categorization and structural feedback
        - **Perplexity**: Real-time fact-checking with web search capabilities
        - **Claude**: Editor-in-Chief synthesis and educational guidance
        
        The Editor-in-Chief synthesizes all feedback into actionable priorities 
        using editorial best practices and your specific content requirements.
        """)
        
        st.markdown("---")
        st.markdown("### Advanced Options")
        st.markdown("""
        Use the advanced options to get more targeted feedback:
        
        - **Content Type**: Adjusts expectations for different formats
        - **Target Audience**: Influences complexity and tone recommendations
        - **Process Stage**: Focuses on appropriate level of revision
        - **Category Focus**: Emphasizes specific editorial areas
        - **Style Guide**: Ensures consistency with publication standards
        """)
        
        st.markdown("---")
        
        # API Status Check
        if st.button("Test API Connections"):
            with st.spinner("Testing APIs..."):
                api_results = test_api_connections()
                
                st.markdown("**API Status:**")
                for service, result in api_results.items():
                    if "working" in result.lower() or "api working" in result.lower():
                        st.success(f"✅ {service.title()}")
                    else:
                        st.error(f"❌ {service.title()}: {result}")
        
        st.markdown("---")
        st.markdown("*Built with Streamlit and multiple AI APIs*")

if __name__ == "__main__":
    main()
