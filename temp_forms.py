import streamlit as st

def render_user_context_form():
    """Render the user context form (Step 1) for Article mode"""
    
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
    """Render the article input form (Step 2) for Article mode"""
    
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

def render_story_conference_form():
    """Render the story conference form for Story Idea mode"""
    
    st.markdown('<div class="section-header">📋 Step 1: Story Conference Setup</div>', unsafe_allow_html=True)
    st.markdown("*Tell the editorial team about your story concept and get professional guidance on development.*")

    # Writer role selection
    writer_role = st.selectbox(
        "What describes you best?",
        ["Student journalist", "Professional journalist", "Academic writer", "Content creator", "Other writer"],
        index=0,
        help="This adjusts the tone and depth of editorial guidance"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Editorial Approach**")
        editorial_role = st.radio(
            "story_editorial_role_radio",
            ["Story Development", "News Judgment", "Investigation Focus", "Feature Planning", "Audience Strategy"],
            index=0,
            help="How should the editors approach your story concept?",
            horizontal=True,
            label_visibility="collapsed"
        )

        st.markdown("**Target Audience**")
        target_audience = st.radio(
            "story_target_audience_radio",
            ["General readers", "Subject specialists", "Other"],
            index=0,
            horizontal=True,
            label_visibility="collapsed"
        )

    with col2:
        # NEW: Specific readership targeting
        readership_detail = st.text_input(
            "**Describe your specific readership** (optional)",
            placeholder="e.g., 'College students at NYU,' 'Small business owners in Seattle,' 'Parents with young children'",
            help="Provide specific details about your target readers for more tailored editorial guidance"
        )

        # Custom context
        custom_context = st.text_area(
            "**Additional Context** (optional)",
            placeholder='e.g., "This is for a class assignment," "I have limited access to sources," "Deadline is next week"',
            height=80,
            help="Any special circumstances, constraints, or guidance for the editorial team"
        )

    # Story Conference Preparation Options
    st.markdown('<div class="section-header">📋 Step 2: Story Conference Preparation</div>', unsafe_allow_html=True)
    
    guided_mode = st.checkbox(
        "📝 **Use guided story conference prep** (optional)",
        help="Answer the core questions editors ask to get more structured feedback"
    )

    core_questions = {}
    if guided_mode:
        st.markdown("### Core Editorial Questions")
        st.markdown("*Answer these questions to prepare for your editorial story conference:*")
        
        core_questions["story_headline"] = st.text_input(
            "**1. What's your story?** (headline test)",
            placeholder="Write your story concept as a potential headline",
            help="If you can't state it clearly and compellingly, you may not have a firm grasp on the story yet"
        )
        
        core_questions["biggest_version"] = st.text_area(
            "**2. What's the biggest version?** / **So what?**",
            placeholder="How does this connect to larger patterns? Why will your specific readership care? What's the human impact?",
            height=80,
            help="Connect the specific instance to broader trends, systems, or universal experiences"
        )
        
        core_questions["pitfalls"] = st.text_area(
            "**3. What are the pitfalls?** (what could kill this story?)",
            placeholder="Sourcing problems? Access issues? Legal risks? Competition? Timing concerns? Provability challenges?",
            height=80,
            help="Think about potential fatal flaws that could make this 'not a story'"
        )
        
        core_questions["why_now"] = st.text_area(
            "**4. Why now?** (timing and urgency)",
            placeholder="What makes this timely? What's the news hook? Why should this be prioritized?",
            height=68,
            help="What creates urgency or timeliness for this story?"
        )

    # Story content input
    st.markdown('<div class="section-header">📄 Step 3: Your Story Concept</div>', unsafe_allow_html=True)

    if guided_mode:
        story_placeholder = """Additional context, notes, research, or draft materials:

Paste any supporting information, source notes, research findings, or draft materials that help explain your story concept. This can include:
• Background research or documents
• Source contact information or quotes
• Related articles or references
• Any preliminary reporting you've done"""
        
        story_help = "Provide any additional context that supports your story concept beyond the structured questions above."
    else:
        story_placeholder = """Describe your story idea, concept, or rough pitch:

Include anything that conveys what you're after and what makes you think there's a story here. This can be:
• A rough hunch or observation
• A detailed pitch with sources
• Questions you want to investigate
• Patterns you've noticed
• Tips you've received

Even fragmentary thoughts are fine - the editorial team can help you develop the concept."""
        
        story_help = "Provide your story concept in whatever form you have it - from rough ideas to detailed pitches."

    story_content = st.text_area(
        "**Story pitch, concept, or supporting materials:**",
        placeholder=story_placeholder,
        height=200,
        help=story_help,
        key="story_content_input"
    )

    return {
        "writer_role": writer_role,
        "editorial_role": editorial_role,
        "target_audience": target_audience,
        "readership_detail": readership_detail,
        "custom_context": custom_context,
        "guided_mode": guided_mode,
        "core_questions": core_questions,
        "story_content": story_content
    }
