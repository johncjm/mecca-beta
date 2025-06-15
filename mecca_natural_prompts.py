# mecca_natural_prompts.py
# Enhanced version with advanced options support
# Natural language prompt templates for MECCA editorial system

def get_role_context(writer_role):
    """Return role-specific context for prompts"""
    contexts = {
        "student": """
        The writer is a journalism student learning the craft. Provide educational explanations 
        and teaching moments. Explain WHY things need to be changed, not just WHAT needs changing. 
        Use a supportive, instructional tone that helps them understand journalistic principles.
        """,
        
        "professional": """
        The writer is a professional journalist. Provide concise, direct feedback focused on 
        industry standards and efficiency. Flag issues clearly and prioritize based on potential 
        impact to credibility and publication standards.
        """,
        
        "other": """
        The writer may have varying experience levels. Provide balanced feedback with helpful 
        explanations while remaining concise. Focus on clarity, accuracy, and effective communication.
        """
    }
    return contexts.get(writer_role, contexts["other"])

def get_advanced_context(advanced_options):
    """Generate context from advanced options"""
    if not advanced_options:
        return ""
    
    context_parts = []
    
    # Content type context
    content_type = advanced_options.get("content_type", "News Article")
    context_parts.append(f"CONTENT TYPE: {content_type}")
    
    if content_type == "Investigation":
        context_parts.append("Focus on fact-checking, sourcing, and verification standards appropriate for investigative journalism.")
    elif content_type == "Feature":
        context_parts.append("Consider narrative flow, character development, and engaging storytelling alongside factual accuracy.")
    elif content_type == "Essay":
        context_parts.append("Evaluate argument structure, evidence quality, and persuasive writing techniques.")
    elif content_type == "Review":
        context_parts.append("Assess balance, expertise demonstration, and fair evaluation criteria.")
    
    # Target audience context
    audience = advanced_options.get("target_audience", "General readers")
    context_parts.append(f"TARGET AUDIENCE: {audience}")
    
    if audience == "Subject specialists":
        context_parts.append("Readers will have domain expertise. Technical accuracy and depth are crucial.")
    elif audience == "Students":
        context_parts.append("Educational clarity and accessible explanations are important.")
    elif audience == "General readers":
        context_parts.append("Clear explanations of technical concepts and accessible language are essential.")
    
    # Process stage context
    stage = advanced_options.get("process_stage", "Draft review")
    context_parts.append(f"PROCESS STAGE: {stage}")
    
    if stage == "Fact-check focus":
        context_parts.append("Prioritize verification of factual claims, sourcing, and accuracy over style issues.")
    elif stage == "Polish/copy edit":
        context_parts.append("Focus on grammar, style, clarity, and final publication readiness.")
    elif stage == "Draft review":
        context_parts.append("Address both structural and detailed issues appropriate for comprehensive revision.")
    
    # Category focus
    focus = advanced_options.get("category_focus", "Comprehensive review")
    if focus != "Comprehensive review":
        context_parts.append(f"FOCUS AREA: {focus}")
        
        if focus == "Fact-checking heavy":
            context_parts.append("Emphasize verification, sourcing, and factual accuracy above other concerns.")
        elif focus == "Style focus":
            context_parts.append("Emphasize writing quality, clarity, tone, and adherence to style guidelines.")
        elif focus == "Structure focus":
            context_parts.append("Emphasize organization, flow, narrative structure, and logical development.")
    
    # Style guide
    style_guide = advanced_options.get("style_guide", "AP")
    if style_guide:
        context_parts.append(f"STYLE GUIDE: {style_guide}")
        
        if style_guide == "AP":
            context_parts.append("Follow Associated Press style for journalism standards.")
        elif style_guide == "Chicago":
            context_parts.append("Follow Chicago Manual of Style guidelines.")
        elif style_guide == "APA":
            context_parts.append("Follow APA style guidelines appropriate for academic writing.")
        elif style_guide == "MLA":
            context_parts.append("Follow MLA style guidelines for humanities writing.")
    
    # Target length
    target_length = advanced_options.get("target_length")
    if target_length:
        context_parts.append(f"TARGET LENGTH: {target_length}")
        context_parts.append("Consider whether the current length serves the content well and suggest adjustments if needed.")
    
    # Additional context
    editor_context = advanced_options.get("editor_context")
    if editor_context:
        context_parts.append(f"ADDITIONAL CONTEXT: {editor_context}")
    
    return "\n".join(context_parts)

def get_editorial_prompt(model_name, article_text, writer_role="professional", advanced_options=None):
    """Generate model-specific editorial prompts with advanced options"""
    
    role_context = get_role_context(writer_role)
    advanced_context = get_advanced_context(advanced_options)
    
    # Handle headline if provided
    headline_section = ""
    if advanced_options and advanced_options.get("headline"):
        headline_section = f"""
HEADLINE: {advanced_options['headline']}

Please also evaluate the headline for:
- Accuracy and clarity
- Appropriate tone for the content type
- Effectiveness in attracting target audience
- Length and style guide compliance

"""
    
    base_prompt = f"""You are acting as a professional editor reviewing this article. 

{role_context}

{advanced_context}

{headline_section}ARTICLE TO REVIEW:
{article_text}

IMPORTANT: The article text above has been numbered by paragraphs for easy reference. When providing feedback, please reference specific paragraphs (e.g., "Paragraph 3:" or "In Paragraph 1:") to help the writer locate issues quickly.

FACT-CHECKING PRIORITY:
For each factual claim, decide whether to verify or flag:
- ✓ VERIFIED: [claim] - [source/reasoning for verification]
- ⚠️ FLAG: [claim] - [why this needs manual verification]  
- ❌ FALSE: [claim] - [correct information and source]

Focus especially on:
- Names, titles, and positions of people mentioned
- Specific dates, locations, and numbers
- Quotes and their attribution
- Claims that could be easily verified or disproven

OTHER EDITORIAL AREAS:
- Grammar, spelling, and punctuation
- Clarity and readability
- Structure and organization
- Tone and style appropriateness
- Attribution and sourcing

SEVERITY ASSESSMENT:
- CRITICAL: Could embarrass publication or harm credibility
- HIGH: Significantly impacts quality or accuracy
- MEDIUM: Noticeable but manageable issues
- LOW: Minor improvements that would enhance the piece

Provide specific, actionable feedback that helps the writer improve their work."""

    # Model-specific customizations
    if model_name == "perplexity":
        return base_prompt + """

SPECIAL FOCUS FOR YOUR REVIEW:
As our fact-checking specialist, prioritize verification of factual claims using current, reliable sources. 
Use your web search capabilities to verify:
- Current officeholders and their correct titles
- Recent events and their accurate details
- Proper names and their correct spelling
- Statistics and their sources

Be especially thorough with fact-checking - this is your primary strength in our editorial team."""

    elif model_name == "gpt-4o":
        return base_prompt + """

SPECIAL FOCUS FOR YOUR REVIEW:
Provide comprehensive editorial feedback with strong attention to journalistic ethics and standards. 
Focus on sourcing requirements, attribution standards, and overall editorial quality. Consider how 
this piece would be received by readers and what questions they might have."""

    elif model_name == "gemini":
        return base_prompt + """

SPECIAL FOCUS FOR YOUR REVIEW:
Provide systematic categorization of issues with clear severity assessment. Focus on organizing 
your feedback in a structured way that helps prioritize fixes. Consider the overall coherence 
and logical flow of the article."""

    elif model_name == "claude":
        return base_prompt + """

SPECIAL FOCUS FOR YOUR REVIEW:
Provide educational explanations for your suggestions, helping the writer understand the reasoning 
behind each recommendation. Focus on teaching moments and building journalistic skills."""

    else:
        return base_prompt

def get_eic_synthesis_prompt(gpt_response, gemini_response, claude_response, perplexity_response, writer_role="professional", advanced_options=None):
    """Generate prompt for Editor-in-Chief synthesis with advanced options"""
    
    role_guidance = {
        "student": "Focus on learning opportunities and educational explanations.",
        "professional": "Focus on efficiency and industry standards.",
        "other": "Balance detail with clarity for a general audience."
    }
    
    # Get context from advanced options
    advanced_context = get_advanced_context(advanced_options) if advanced_options else ""
    
    return f"""You are the Editor-in-Chief synthesizing feedback from our editorial team. {role_guidance.get(writer_role, role_guidance["other"])}

{advanced_context}

EDITORIAL TEAM RESPONSES:

GPT-4 EDITOR FEEDBACK:
{gpt_response}

GEMINI EDITOR FEEDBACK:  
{gemini_response}

CLAUDE EDITOR FEEDBACK:
{claude_response}

PERPLEXITY FACT-CHECKER FEEDBACK:
{perplexity_response}

Your job is to synthesize these four perspectives into actionable editorial guidance:

EDITORIAL SUMMARY:
Provide a 1-2 paragraph assessment of the article's overall quality and the team's consensus on major issues.

PRIORITY ACTION LIST:
Using the "embarrassment test" (what would embarrass us most if published as-is), list the most critical fixes needed with specific paragraph references where possible:
1. [Most critical issue with paragraph reference if applicable]
2. [Second priority with paragraph reference if applicable]
3. [Third priority with paragraph reference if applicable]
etc.

IMPORTANT DISCLAIMER:
Always end with: "This AI-generated feedback is advisory only. The writer maintains full responsibility for fact-checking, editorial decisions, and final content. All suggestions, especially those related to factual claims, must be independently verified."

Focus on synthesis and meta-analysis - don't just repeat what the individual editors said, but provide genuine editorial judgment about priorities and actionable next steps."""

def get_model_display_name(model_key):
    """Convert model keys to display names"""
    display_names = {
        "gpt-4o": "GPT-4O Editor",
        "gemini": "Gemini Editor", 
        "claude": "Claude Editor",
        "perplexity": "Perplexity Fact-Checker"
    }
    return display_names.get(model_key, model_key)
