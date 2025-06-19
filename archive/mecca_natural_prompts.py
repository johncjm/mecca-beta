# mecca_natural_prompts.py
# Enhanced version with hybrid overlap + specialization approach
# Natural language prompt templates for MECCA editorial system

def get_role_context(writer_role):
    """Return role-specific context for prompts"""
    contexts = {
        "student": """
        The writer is a journalism student learning the craft. Provide educational explanations 
        and teaching moments. Explain WHY things need to be changed, not just WHAT needs changing. 
        Use a supportive, instructional tone that helps them understand journalistic principles.
        
        IMPORTANT: Always identify 1-2 specific strengths in the writing to encourage the student's development.
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
    
    # CRITICAL CONTEXT OVERRIDE - Custom context gets TOP PRIORITY
    custom_context = advanced_options.get("custom_context")
    if custom_context and custom_context.strip():
        context_parts.append("=" * 50)
        context_parts.append("🚨 CRITICAL CONTEXT OVERRIDE - TOP PRIORITY:")
        context_parts.append(f"{custom_context}")
        context_parts.append("CRITICAL: If custom context provided above, override default role boundaries and editorial approaches to follow these specific instructions.")
        context_parts.append("=" * 50)
    
    # Content type context
    content_type = advanced_options.get("content_type", "Standard news article")
    context_parts.append(f"CONTENT TYPE: {content_type}")
    
    if content_type == "Investigation":
        context_parts.append("Focus on fact-checking, sourcing, and verification standards appropriate for investigative journalism.")
    elif content_type == "Feature":
        context_parts.append("Consider narrative flow, character development, and engaging storytelling alongside factual accuracy.")
    elif content_type == "Essay":
        context_parts.append("Evaluate argument structure, evidence quality, and persuasive writing techniques.")
    elif content_type == "Review":
        context_parts.append("Assess balance, expertise demonstration, and fair evaluation criteria.")
    elif content_type == "Standard news article":
        context_parts.append("Apply standard news writing principles: lead, supporting facts, balanced reporting, and clear attribution.")
    
    # Target audience context
    audience = advanced_options.get("target_audience", "General readers")
    context_parts.append(f"TARGET AUDIENCE: {audience}")
    
    if audience == "Specialists":
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
    focus = advanced_options.get("category_emphasis", "Comprehensive")
    if focus != "Comprehensive":
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
    
    # Editorial role context
    editorial_role = advanced_options.get("editorial_role")
    if editorial_role:
        context_parts.append(f"EDITORIAL APPROACH: {editorial_role}")
        
        if editorial_role == "Writing Coach":
            context_parts.append("Adopt a mentoring perspective focused on skill development and improvement.")
        elif editorial_role == "Copy Editor":
            context_parts.append("Focus on grammar, style, accuracy, and publication readiness.")
        elif editorial_role == "News Desk Editor":
            context_parts.append("Apply newsroom standards with focus on speed, accuracy, and reader engagement.")
        elif editorial_role == "Feature Editor":
            context_parts.append("Emphasize storytelling, narrative flow, and feature-specific techniques.")
        elif editorial_role == "Fact-Checker Focus":
            context_parts.append("Prioritize verification and sourcing above all other concerns.")
        elif editorial_role == "Style Editor":
            context_parts.append("Focus primarily on voice, tone, and stylistic consistency.")
    
    return "\n".join(context_parts)

def get_editorial_prompt(model_name, article_text, writer_role="professional", advanced_options=None):
    """Generate model-specific editorial prompts with hybrid overlap + specialization approach"""
    
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
    
    # Universal critical issue flagging (ALL MODELS)
    universal_critical_section = """
🚨 UNIVERSAL CRITICAL ISSUE FLAGGING (ALWAYS FLAG REGARDLESS OF YOUR PRIMARY ROLE):
- Obvious factual errors that could embarrass the publication
- Major credibility threats or ethical concerns
- Structural problems that fundamentally undermine the article
- Legal issues or potential liability concerns
- Claims that are clearly false or misleading

"""
    
    # Model-specific specialization boundaries
    specialization_sections = {
        "gpt-4o": """
YOUR PRIMARY SPECIALIZATION: FACT-CHECKING LEAD
Focus primarily on verification, sourcing, and accuracy, but always flag critical credibility issues in other areas.

SPECIALIZED RESPONSIBILITIES:
- Verify factual claims against reliable sources
- Check proper attribution and sourcing
- Identify claims needing independent verification
- Assess credibility of sources mentioned
- Flag potential legal or ethical issues

SECONDARY OVERSIGHT: Always flag critical issues in structure, style, or other areas that could harm publication credibility.
""",
        
        "gemini": """
YOUR PRIMARY SPECIALIZATION: STRUCTURE/FLOW LEAD
Focus primarily on organization, clarity, and reader comprehension, but always flag critical credibility issues in other areas.

SPECIALIZED RESPONSIBILITIES:
- Assess overall article organization and logical flow
- Identify unclear or confusing passages
- Evaluate paragraph transitions and coherence
- Check that the structure serves the content type
- Assess reader comprehension and engagement

SECONDARY OVERSIGHT: Always flag critical issues in facts, style, or other areas that could harm publication credibility.
""",
        
        "perplexity": """
YOUR PRIMARY SPECIALIZATION: REAL-TIME VERIFICATION
Use your web search capabilities for current fact-checking and source verification, but always flag critical credibility issues in other areas.

SPECIALIZED RESPONSIBILITIES:
- Verify current information using web search
- Check recent events, current officeholders, latest statistics
- Validate proper names, titles, and recent developments
- Cross-reference claims with current reliable sources
- Flag outdated information

SECONDARY OVERSIGHT: Always flag critical issues in structure, style, or other areas that could harm publication credibility.
""",
        
        "claude": """
YOUR PRIMARY SPECIALIZATION: TONE/STYLE LEAD
Focus primarily on voice, audience appropriateness, and engagement, but always flag critical credibility issues in other areas.

SPECIALIZED RESPONSIBILITIES:
- Assess tone appropriateness for target audience
- Evaluate voice consistency and style
- Check language accessibility and clarity
- Assess engagement and readability
- Identify stylistic inconsistencies

SECONDARY OVERSIGHT: Always flag critical issues in facts, structure, or other areas that could harm publication credibility.
"""
    }
    
    base_prompt = f"""You are acting as a professional editor reviewing this article using MECCA's hybrid specialization approach.

{role_context}

{advanced_context}

{universal_critical_section}

{specialization_sections.get(model_name, specialization_sections["claude"])}

{headline_section}ARTICLE TO REVIEW:
{article_text}

FEEDBACK REQUIREMENTS:
1. ALWAYS reference specific paragraphs when providing feedback (e.g., "Paragraph 3:" or "In Paragraph 1:")
2. Provide SPECIFIC, ACTIONABLE suggestions rather than vague observations
3. Include concrete examples of how to improve problematic passages
4. For factual claims, be explicit about verification status

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

    # Model-specific final instructions based on specialization
    if model_name == "perplexity":
        return base_prompt + """

REMEMBER: While you are the real-time verification specialist, you must still flag any critical issues you notice in structure, style, or other areas. Your web search capabilities make you especially valuable for current fact-checking."""

    elif model_name == "gpt-4o":
        return base_prompt + """

REMEMBER: While you are the fact-checking lead, you must still flag any critical issues you notice in structure, style, or other areas. Your strength in comprehensive analysis makes you valuable for overall editorial quality."""

    elif model_name == "gemini":
        return base_prompt + """

REMEMBER: While you are the structure/flow lead, you must still flag any critical issues you notice in facts, style, or other areas. Your systematic approach makes you valuable for organizing feedback clearly."""

    elif model_name == "claude":
        return base_prompt + """

REMEMBER: While you are the tone/style lead, you must still flag any critical issues you notice in facts, structure, or other areas. Your nuanced understanding makes you valuable for audience-appropriate communication."""

    else:
        return base_prompt

def get_eic_synthesis_prompt(gpt_response, gemini_response, claude_response, perplexity_response, writer_role="professional", advanced_options=None):
    """Generate prompt for Editor-in-Chief synthesis with advanced options"""
    
    role_guidance = {
        "student": "Focus on learning opportunities and educational explanations. Include encouragement about what the student is doing well.",
        "professional": "Focus on efficiency and industry standards with direct, actionable priorities.",
        "other": "Balance detail with clarity for a general audience."
    }
    
    # Get context from advanced options
    advanced_context = get_advanced_context(advanced_options) if advanced_options else ""
    
    return f"""You are the Editor-in-Chief synthesizing feedback from our specialized editorial team using the "embarrassment test" - prioritizing issues that would most embarrass the publication if published. {role_guidance.get(writer_role, role_guidance["other"])}

{advanced_context}

EDITORIAL TEAM COMPOSITION:
- GPT-4: Fact-Checking Lead (primary: verification/sourcing, secondary: critical issue flagging)
- Gemini: Structure/Flow Lead (primary: organization/clarity, secondary: critical issue flagging)  
- Perplexity: Real-time Verification (primary: current fact-checking, secondary: critical issue flagging)
- Your role: Synthesize using "embarrassment test" prioritization

EDITORIAL TEAM RESPONSES:

GPT-4 FACT-CHECKING LEAD FEEDBACK:
{gpt_response}

GEMINI STRUCTURE/FLOW LEAD FEEDBACK:  
{gemini_response}

CLAUDE TONE/STYLE LEAD FEEDBACK:
{claude_response}

PERPLEXITY REAL-TIME VERIFICATION FEEDBACK:
{perplexity_response}

Your synthesis should:

EDITORIAL SUMMARY:
Provide a 1-2 paragraph assessment of the article's overall quality and the team's consensus on major issues.

PRIORITY ACTION LIST:
Using the "embarrassment test" (what would embarrass us most if published as-is), list the most critical fixes needed with specific paragraph references where possible:
1. [Most critical issue with paragraph reference if applicable]
2. [Second priority with paragraph reference if applicable]
3. [Third priority with paragraph reference if applicable]
etc.

SYNTHESIS APPROACH:
- Don't just repeat what individual editors said
- Provide genuine editorial judgment about priorities
- Resolve conflicts between different editors' feedback
- Focus on actionable next steps
- Consider the specialized roles each editor played

IMPORTANT DISCLAIMER:
Always end with: "This AI-generated feedback is advisory only. The writer maintains full responsibility for fact-checking, editorial decisions, and final content. All suggestions, especially those related to factual claims, must be independently verified."

Focus on synthesis and meta-analysis that provides genuine editorial leadership."""

def get_model_display_name(model_key):
    """Convert model keys to display names"""
    display_names = {
        "gpt-4o": "GPT-4 Editor (Fact-Checking Lead)",
        "gemini": "Gemini Editor (Structure/Flow Lead)", 
        "claude": "Claude Editor (Tone/Style Lead)",
        "perplexity": "Perplexity Fact-Checker (Real-time Verification)"
    }
    return display_names.get(model_key, model_key)
