import streamlit as st

def render_user_context_form():
    """Render the user context form (Step 1)"""
    
    st.markdown('<div class="section-header">📝 Step 1: Tell us about you and what you\'re working on</div>', unsafe_allow_html=True)
    st.markdown("*The more the AI models know about what you're trying to do and what assistance you need, the better job they'll do in helping you.*")

    # Writer role selection - Student first per user request
    writer_role = st.selectbox(
        "What describes you best?",
        ["Student journalist", "Professional journalist", "Academic writer", "Content creator", "Other writer"],
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

        # Custom Editor Context
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

    return {
        "writer_role": writer_role,
        "editorial_role": editorial_role,
        "content_type": content_type,
        "target_audience": target_audience,
        "custom_context": custom_context,
        "process_stage": process_stage,
        "style_guide": style_guide,
        "target_length": target_length
    }

def render_article_input():
    """Render the article input form (Step 2)"""
    
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

    return headline, article_text, analyze_button
