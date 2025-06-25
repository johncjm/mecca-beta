import streamlit as st
import os
from mecca_dialogue_prototype_calls import call_openai, call_anthropic, call_google, call_perplexity, enhanced_dialogue_handler
from mecca_dialogue_prototype_prompts import get_editorial_prompt, get_eic_synthesis_prompt_v3, get_story_conference_prompt, get_story_eic_synthesis_prompt
    print("✅ Prompts imported successfully")
except ImportError as e:
    print(f"❌ Prompts import failed: {e}")
from ui.styles import load_custom_styles
from ui.forms import render_user_context_form, render_article_input, render_story_conference_form
    print("✅ Forms imported successfully")
except ImportError as e:
    print(f"❌ Forms import failed: {e}")
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
The <strong>Multiple Edit and Cross-Check Assistant</strong> helps writers develop story ideas and improve finished articles through AI editorial feedback. From initial concept to final draft, MECCA teaches editorial thinking while maintaining appropriate skepticism about AI capabilities.
</div>
""", unsafe_allow_html=True)

# Inline Learn More expandable section
with st.expander("📖 Learn More About MECCA Interactive"):
    st.markdown("""
    **How MECCA Interactive Works:**
    
    MECCA offers two modes with hybrid specialization and dialogue capability:
    
    **📋 Story Conference Mode:**
    • Evaluate story ideas before you start reporting
    • Learn editorial thinking through core questions professionals ask
    • Get guidance on story development, sourcing strategy, and pitfalls
    • Optional guided prep or free-form pitch formats
    
    **📝 Article Editing Mode:**
    • **GPT-4 (Comprehensive Analysis)**: Organization, structure, comprehensive review
    • **Gemini (Copy Editing & Style)**: Grammar, style, tone, language clarity
    • **Perplexity (Fact-Checking)**: Web search verification (with reliability monitoring)
    • **Claude (Editor-in-Chief)**: Synthesizes feedback + answers your questions
    
    **Enhanced Features:**
    
    • **Honest AI Assessment**: Shows exactly what each AI found (including mistakes)
    • **Educational Dialogue**: Learn why AI systems fail and how to verify their work
    • **Transparency Requirements**: EiC quotes specialists exactly, including errors
    • **"Editorial Thinking Partner"**: Teaches professional judgment, not just corrections
    
    **Best Practices:**
    
    • Use dialogue to understand both AI strengths AND limitations
    • Always verify AI fact-checking independently
    • Learn from AI failures as teaching moments
    • Maintain editorial control over all decisions
    """)

# Content type selection (Step 0)
st.markdown('<div class="section-header">📋 What are you working on?</div>', unsafe_allow_html=True)

content_mode = st.radio(
    "Choose your mode:",
    ["Article (finished/draft)", "Story Idea (pitch/concept)"],
    index=0,
    horizontal=True,
    help="Article mode provides editing feedback. Story Conference mode helps develop story concepts."
)

# Render appropriate form based on content mode
if content_mode == "Story Idea (pitch/concept)":
    # Story Conference Mode
    story_data = render_story_conference_form()
    
    # Analysis button for story mode
    if st.button("🎯 Convene Editorial Story Conference", type="primary", use_container_width=True):
        if not story_data["story_content"].strip():
            st.error("Please provide your story idea, pitch, or concept.")
        else:
            # Reset analysis state for new story conference
            reset_analysis_state()
            st.session_state.content_mode = "story"
            
            with st.spinner("🤖 Editorial team evaluating your story concept..."):
                
                # Get API keys
                openai_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
                anthropic_key = st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY") 
                google_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
                perplexity_key = st.secrets.get("PERPLEXITY_API_KEY") or os.getenv("PERPLEXITY_API_KEY")
                
                # Prepare context for story conference
                story_context = {
                    "content_type": "story_idea",
                    "writer_role": story_data["writer_role"],
                    "editorial_role": story_data["editorial_role"],
                    "target_audience": story_data["target_audience"],
                    "readership_detail": story_data["readership_detail"],
                    "custom_context": story_data["custom_context"],
                    "guided_mode": story_data["guided_mode"],
                    "core_questions": story_data["core_questions"] if story_data["guided_mode"] else None
                }
                
                # Store in session state
                st.session_state.context = story_context
                st.session_state.original_article = story_data["story_content"]
                
                # Map writer role
                role_mapping = {
                    "Student journalist": "student",
                    "Professional journalist": "professional", 
                    "Academic writer": "other",
                    "Content creator": "other",
                    "Other writer": "other"
                }
                mapped_role = role_mapping.get(story_data["writer_role"], "other")
                
                # Call models with story conference prompts
                gpt_response = call_openai(get_story_conference_prompt("gpt-4o", story_data, mapped_role, story_context), openai_key) if openai_key else "OpenAI API key not configured"
                gemini_response = call_google(get_story_conference_prompt("gemini", story_data, mapped_role, story_context), google_key) if google_key else "Google API key not configured"
                perplexity_response = call_perplexity(get_story_conference_prompt("perplexity", story_data, mapped_role, story_context), perplexity_key) if perplexity_key else "Perplexity API key not configured"
                
                # Store responses
                st.session_state.editor_responses = {
                    "gpt": gpt_response,
                    "gemini": gemini_response, 
                    "perplexity": perplexity_response
                }
                
                # EiC synthesis for story conference
                claude_eic_prompt = get_story_eic_synthesis_prompt(gpt_response, gemini_response, perplexity_response, mapped_role, story_context)
                combined_analysis = f"""
GPT-4 Story Analysis:
{gpt_response}

Gemini Story Analysis:
{gemini_response}

Perplexity Story Analysis:
{perplexity_response}
                """
                
                claude_response = call_anthropic(claude_eic_prompt, combined_analysis, anthropic_key) if anthropic_key else "Anthropic API key not configured"
                
                st.session_state.eic_summary = claude_response
                st.session_state.has_analysis = True

else:
    # Article Editing Mode (existing functionality)
    form_data = render_user_context_form()
    headline, article_text, analyze_button = render_article_input()
    
    # Analysis results for article mode
    if analyze_button and article_text.strip():
        # Reset dialogue history and analysis state for new analysis
        reset_analysis_state()
        st.session_state.content_mode = "article"
        
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
                "category_emphasis": "Comprehensive",
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

    # Dynamic header based on mode
    if st.session_state.get('content_mode') == 'story':
        st.markdown('<div class="section-header">📋 Editorial Story Conference Results</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="section-header">📋 Your Editorial Feedback</div>', unsafe_allow_html=True)
    
    # Initialize tab state if not exists
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0
    
    # Create tabs for organized feedback display
    if st.session_state.get('content_mode') == 'story':
        tab1, tab2, tab3 = st.tabs([
            "🎯 Editorial Assessment", 
            "📋 Specialist Perspectives", 
            "💬 Ask the Editor"
        ])
    else:
        tab1, tab2, tab3 = st.tabs([
            "📋 Editor-in-Chief Overview", 
            "📝 Full Individual Responses", 
            "💬 Ask the Editor"
        ])
    
    with tab1:
        if st.session_state.get('content_mode') == 'story':
            st.markdown("## 🎯 Editor-in-Chief Story Assessment")
            st.markdown("*Editorial evaluation using story conference principles*")
        else:
            st.markdown("## 📋 Editor-in-Chief Summary")
            st.markdown("*Synthesis of all editorial feedback using the 'embarrassment test' for prioritization*")
        
        # Display EiC content directly
        st.markdown(st.session_state.eic_summary)
        
        # Encourage dialogue immediately after EiC feedback
        if st.session_state.get('content_mode') == 'story':
            st.info("""
            💬 **Continue the story conference!** Use the "Ask the Editor" tab to explore:
            • Why did the Editor-in-Chief reach this assessment?
            • How would you approach the biggest concerns identified?
            • What would strengthen this story concept?
            
            **Real editorial learning happens through dialogue.**
            """)
        else:
            st.markdown("---")
            st.markdown("""
            **💡 Next Steps:**
            - Check **Full Individual Responses** tab for detailed specialist feedback
            - Use **Ask the Editor** tab to understand the reasoning behind suggestions
            - Remember: This is advisory feedback - you maintain full editorial control
            """)
    
    with tab2:
        if st.session_state.get('content_mode') == 'story':
            st.markdown("## 📋 Specialist Story Perspectives")
            st.markdown("*Compare how different editorial specialists evaluated your story concept*")
        else:
            st.markdown("## Full Individual Responses")
            st.markdown("*Compare all specialist feedback side by side - transparency is key to learning AI limitations.*")
        
        # Search bar for responses
        search_query = st.text_input("🔍 Search within responses:", placeholder="Search for specific terms across all responses...", key="response_search")
        
        # Three-column layout for specialist responses
        editor_responses = st.session_state.editor_responses
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.session_state.get('content_mode') == 'story':
                st.markdown("#### 📊 GPT-4 (Comprehensive Analysis)")
                st.markdown("**Focus:** Story viability, evidence gaps, editorial judgment")
            else:
                st.markdown("#### 📝 GPT-4 (Comprehensive Analysis)")
                st.markdown("**Focus:** Organization, structure, comprehensive review")
            
            gpt_content = editor_responses.get("gpt", "Response not available")
            if search_query and search_query.lower() in gpt_content.lower():
                st.markdown(f"🔍 *Contains: '{search_query}'*")
            st.markdown(gpt_content)
            
            if st.session_state.get('content_mode') == 'story':
                st.markdown("💡 **Ask the EiC:** 'How should I prioritize these development areas?'")
        
        with col2:
            if st.session_state.get('content_mode') == 'story':
                st.markdown("#### 📝 Gemini (Structure & Audience)")
                st.markdown("**Focus:** Story structure, narrative potential, reader engagement")
            else:
                st.markdown("#### ✏️ Gemini (Copy Editing & Style)")
                st.markdown("**Focus:** Grammar, style, language clarity")
            
            gemini_content = editor_responses.get("gemini", "Response not available")
            if search_query and search_query.lower() in gemini_content.lower():
                st.markdown(f"🔍 *Contains: '{search_query}'*")
            st.markdown(gemini_content)
            
            if st.session_state.get('content_mode') == 'story':
                st.markdown("💡 **Ask the EiC:** 'Walk me through how you'd structure this story.'")
        
        with col3:
            if st.session_state.get('content_mode') == 'story':
                st.markdown("#### 🔍 Perplexity (Reporting Strategy)")
                st.markdown("**Focus:** Fact-checking methodology, verification approach")
            else:
                st.markdown("#### 🔍 Perplexity (Fact-Checking)")
                st.markdown("**Focus:** Web search fact-checking")
            
            perplexity_content = editor_responses.get("perplexity", "Response not available")
            if search_query and search_query.lower() in perplexity_content.lower():
                st.markdown(f"🔍 *Contains: '{search_query}'*")
            st.markdown(perplexity_content)
            
            if st.session_state.get('content_mode') == 'story':
                st.markdown("💡 **Ask the EiC:** 'What's your verification roadmap for this story?'")
            else:
                st.markdown("⚠️ **Fact-checking results below can often be wrong. Notices of mistakes are not the result of a bug - it's a feature designed to teach appropriate AI skepticism.**")
        
        # Final dialogue encouragement for story mode
        if st.session_state.get('content_mode') == 'story':
            st.success("""
            🎯 **Next Step: Engage with the Editor-in-Chief!**
            
            Use the "Ask the Editor" tab to continue the conversation. Ask WHY decisions were made, HOW to approach challenges, and WHAT IF you tried different angles.
            
            **Great journalists don't just take advice - they understand the editorial thinking behind it.**
            """)
    
    with tab3:
        # Set active tab when this tab is accessed
        if st.session_state.get('form_submitted', False):
            st.session_state.active_tab = 2
            st.session_state.form_submitted = False
            
        st.markdown("## 💬 Ask the Editor-in-Chief")
        
        if st.session_state.get('content_mode') == 'story':
            st.markdown("*Continue the story conference dialogue. Ask about the assessment, explore alternatives, understand the editorial thinking.*")
        else:
            st.markdown("*Ask questions about the feedback with complete transparency. The EiC will show you exactly what each specialist found, including their mistakes.*")
        
        # Display dialogue history
        for i, exchange in enumerate(st.session_state.dialogue_history):
            st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {exchange["question"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-message eic-message"><strong>Editor-in-Chief:</strong> {exchange["answer"]}</div>', unsafe_allow_html=True)
        
        # Question input form
        with st.form("dialogue_form"):
            if st.session_state.get('content_mode') == 'story':
                placeholder_text = "e.g., 'Why did you rate this as promising but risky?' or 'How would you approach the access challenges?' or 'What if I focused on the economic impact instead?'"
                help_text = "Ask WHY as well as WHAT. The Editor-in-Chief can explain editorial reasoning and help develop your story concept."
            else:
                placeholder_text = "e.g., 'Show me exactly what your fact-checker said about Mario Cuomo' or 'Which specialists missed the State Senator error?'"
                help_text = "Ask about specific feedback, reasoning behind suggestions, or request clarification on any editorial advice."
            
            user_question = st.text_input(
                "Continue the editorial conversation:",
                placeholder=placeholder_text,
                help=help_text,
                key="dialogue_question_input"
            )
            
            submitted = st.form_submit_button("Ask Editor-in-Chief", type="primary")
            
            if submitted and user_question.strip():
                anthropic_key = st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
                if anthropic_key:
                    with st.spinner("🤔 Editor-in-Chief is thinking..."):
                        # Set flag to stay on this tab after rerun
                        st.session_state.form_submitted = True
                        
                        # Use enhanced dialogue handler
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
        
        # Educational note and dialogue prompts
        if not st.session_state.get('dialogue_history'):
            if st.session_state.get('content_mode') == 'story':
                st.markdown("---")
                st.markdown("""
                **🎯 Story Conference Dialogue Ideas:**
                
                **Understanding the Assessment:**
                - "Why did you prioritize [specific concern] over [other issue]?"
                - "What makes you think this story has/lacks potential?"
                
                **Developing the Story:**
                - "How would you approach [difficult source/situation]?"
                - "What if I took a different angle focusing on [alternative approach]?"
                - "Walk me through your reporting roadmap for this story"
                
                **Editorial Judgment:**
                - "What would make this story stronger?"
                - "How do you assess the risk/reward balance here?"
                - "What similar stories have you seen succeed or fail?"
                """)
            else:
                st.markdown("---")
                st.markdown("""
                **🎓 Educational Note:** The Editor-in-Chief can reference what each specialist 
                found and explain the reasoning behind editorial decisions. This dialogue helps 
                you understand not just *what* to change, but *why* changes are needed.
                """)

# Sidebar with dialogue encouragement
with st.sidebar:
    st.markdown("### 💬 Editorial Dialogue")
    
    if not st.session_state.get('has_analysis'):
        if content_mode == "Story Idea (pitch/concept)":
            st.markdown("""
            **After your story conference, engage with the Editor-in-Chief!**
            
            The real value comes from dialogue:
            • *Why* did you assess this story this way?
            • *How* should I approach the biggest challenges?
            • *What if* I took a different angle?
            
            **Don't just take the advice - understand the editorial thinking behind it.**
            """)
        else:
            st.markdown("""
            **After receiving feedback, engage with the Editor-in-Chief!**
            
            The real value comes from dialogue:
            • *Why* did you prioritize X over Y?
            • *How* should I approach this revision?
            • *What if* I tried a different approach?
            
            **Don't just take the advice - understand the thinking behind it.**
            """)
    else:
        if st.session_state.get('content_mode') == 'story':
            st.markdown("**🎯 Keep the story conference going!**")
            st.markdown("Ask the Editor-in-Chief to explain their assessment, explore alternatives, or dive deeper into development strategies.")
        else:
            st.markdown("**🎯 Keep the conversation going!**")
            st.markdown("Ask the Editor-in-Chief to explain their reasoning, explore alternatives, or dive deeper into specific concerns.")
        
        if not st.session_state.get('dialogue_history'):
            if st.session_state.get('content_mode') == 'story':
                st.markdown("💡 **Try asking:**")
                st.markdown("""
                - "Why is [specific concern] the top priority?"
                - "How would you develop this story concept?"
                - "What if I focused on [different angle]?"
                - "Walk me through the reporting strategy"
                - "What makes similar stories succeed?"
                """)
            else:
                st.markdown("💡 **Try asking:**")
                st.markdown("""
                - "Why is [specific concern] the top priority?"
                - "How would you approach [difficult issue]?"
                - "What if I took a different approach?"
                - "Walk me through your reasoning on [topic]"
                - "What would make this piece stronger?"
                """)

# Footer with enhanced messaging
st.markdown("---")
st.markdown(
    "Built with ❤️ for writers, journalists, and students. "
    "MECCA Interactive teaches both AI capabilities AND limitations through transparent feedback and honest dialogue. "
    "**From story idea to finished piece - your editorial thinking partner.**"
)
