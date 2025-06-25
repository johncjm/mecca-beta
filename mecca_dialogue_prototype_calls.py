import json
import requests
import time
import anthropic
import openai
import google.generativeai as genai
from datetime import datetime
import streamlit as st

def call_openai(prompt, api_key):
    """Call OpenAI GPT-4 API"""
    if not api_key:
        return "OpenAI API key not configured"
    
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert editorial assistant focusing on comprehensive analysis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"OpenAI API Error: {str(e)}"

def call_anthropic(prompt, article_text, api_key):
    """Call Anthropic Claude API"""
    if not api_key:
        return "Anthropic API key not configured"
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2500,
            temperature=0.3,
            system=prompt,
            messages=[
                {"role": "user", "content": article_text}
            ]
        )
        return message.content[0].text.strip()
    except Exception as e:
        return f"Anthropic API Error: {str(e)}"

def call_google(prompt, api_key):
    """Call Google Gemini API"""
    if not api_key:
        return "Google API key not configured"
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=2000,
                temperature=0.3,
            )
        )
        return response.text.strip()
    except Exception as e:
        return f"Google API Error: {str(e)}"

def call_perplexity(prompt, api_key):
    """Call Perplexity API (will be replaced by Custom Fact-Checking Coach)"""
    if not api_key:
        return "Perplexity API key not configured"
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama-3.1-sonar-large-128k-online",
            "messages": [
                {"role": "system", "content": "You are an expert fact-checking assistant with web search capabilities."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2000,
            "temperature": 0.3,
            "search_domain_filter": ["perplexity.ai"],
            "return_citations": True,
            "search_recency_filter": "month",
            "top_p": 0.9,
            "stream": False
        }
        
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        else:
            return f"Perplexity API Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Perplexity API Error: {str(e)}"

def call_custom_fact_checking_coach(prompt, openai_key, bing_key=None):
    """
    Custom Fact-Checking Coach using GPT-4o-mini + Bing Search API
    Placeholder implementation - will be fully developed when Bing API key is available
    """
    if not openai_key:
        return "OpenAI API key not configured for Custom Fact-Checking Coach"
    
    # TODO: Implement Bing Search integration when API key is available
    if not bing_key:
        # Placeholder response showing the intended functionality
        return """**Custom Fact-Checking Coach (Placeholder Implementation)**

This is a preview of the Custom Fact-Checking Coach that will replace Perplexity. When fully implemented, it will:

**VERIFICATION METHODOLOGY APPROACH:**
• Extract key factual claims from content
• Search current sources via Bing Search API  
• Provide verification coaching, not definitive answers
• Focus on "Known vs. Unknown" framework

**CURRENT STATUS:** Awaiting Bing Search API integration

**EDUCATIONAL NOTE:** This coach teaches verification methodology rather than claiming fact-checking authority. It will guide writers through proper verification processes while maintaining appropriate skepticism about AI capabilities.

**PLACEHOLDER GUIDANCE:**
• Always verify claims independently through authoritative sources
• Cross-reference multiple sources for controversial claims
• Be especially cautious with statistics, dates, and proper names
• Consider the publication date and currency of sources

*Full implementation pending Bing Search API key configuration.*"""
    
    try:
        # When Bing API is available, this will extract claims, search, and provide coaching
        client = openai.OpenAI(api_key=openai_key)
        
        coaching_prompt = f"""You are a Fact-Checking Coach focused on verification methodology, not definitive fact-checking.

Your role is to teach verification processes and help identify what needs checking, NOT to declare claims true or false.

METHODOLOGY FOCUS:
- Extract key factual claims that need verification
- Suggest appropriate verification methods and sources
- Identify gaps in sourcing or attribution
- Provide "Known vs. Unknown" framework analysis

BE TRANSPARENT about limitations:
- You cannot access current web data
- You cannot definitively verify claims
- Your role is coaching methodology, not providing answers

Content to analyze for verification methodology:
{prompt}"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a verification methodology coach, not a fact-checker."},
                {"role": "user", "content": coaching_prompt}
            ],
            max_tokens=1500,
            temperature=0.3
        )
        
        base_response = response.choices[0].message.content.strip()
        
        # Add implementation note
        return f"""{base_response}

**IMPLEMENTATION NOTE:** This is the Custom Fact-Checking Coach running on GPT-4o-mini. Full web search capabilities will be added when Bing Search API is configured."""
        
    except Exception as e:
        return f"Custom Fact-Checking Coach Error: {str(e)}"

class MECCAResponseValidator:
    """Validates EiC responses for transparency and accuracy"""
    
    def __init__(self):
        self.validation_flags = []
    
    def validate_specialist_quotes(self, eic_response, specialist_responses):
        """Check if EiC quotes are accurate"""
        flags = []
        
        # Extract quoted content from EiC response
        import re
        quotes = re.findall(r'"([^"]*)"', eic_response)
        
        for quote in quotes:
            if len(quote) > 10:  # Only check substantial quotes
                found_in_specialists = False
                for specialist_name, response in specialist_responses.items():
                    if quote.lower() in response.lower():
                        found_in_specialists = True
                        break
                
                if not found_in_specialists:
                    flags.append(f"Unverified quote: '{quote[:50]}...'")
        
        return flags
    
    def validate_performance_claims(self, eic_response, specialist_responses):
        """Check if claims about specialist performance are accurate"""
        flags = []
        
        # Look for performance claims
        performance_indicators = [
            "caught", "missed", "flagged", "identified", "failed to",
            "overlooked", "noted", "highlighted", "ignored"
        ]
        
        for indicator in performance_indicators:
            if indicator in eic_response.lower():
                # This would need more sophisticated parsing in production
                # For now, just flag for manual review
                flags.append(f"Performance claim detected: review accuracy of '{indicator}' statements")
                break
        
        return flags
    
    def validate_response(self, eic_response, specialist_responses):
        """Main validation function"""
        self.validation_flags = []
        
        quote_flags = self.validate_specialist_quotes(eic_response, specialist_responses)
        performance_flags = self.validate_performance_claims(eic_response, specialist_responses)
        
        self.validation_flags.extend(quote_flags)
        self.validation_flags.extend(performance_flags)
        
        return {
            'flags': self.validation_flags,
            'is_valid': len(self.validation_flags) == 0
        }

def enhanced_dialogue_handler_v2(user_question, session_state, anthropic_key):
    """Enhanced dialogue handler with transparency validation"""
    from mecca_dialogue_prototype_prompts import get_enhanced_dialogue_system_prompt_v2
    
    if not anthropic_key:
        return "Anthropic API key not configured for dialogue feature."
    
    try:
        # Get specialist responses from session state
        specialist_responses = {
            "gpt": session_state.editor_responses.get("gpt", ""),
            "gemini": session_state.editor_responses.get("gemini", ""),
            "perplexity": session_state.editor_responses.get("perplexity", "")
        }
        
        # Create enhanced system prompt with maximum transparency
        system_prompt = get_enhanced_dialogue_system_prompt_v2(
            specialist_responses["gpt"],
            specialist_responses["gemini"], 
            specialist_responses["perplexity"],
            session_state.original_article,
            session_state.context
        )
        
        # Build conversation history
        messages = []
        
        # Add conversation history
        for exchange in session_state.dialogue_history:
            messages.append({"role": "user", "content": exchange["question"]})
            messages.append({"role": "assistant", "content": exchange["answer"]})
        
        # Add current question
        messages.append({"role": "user", "content": user_question})
        
        # Call Claude with enhanced transparency protocols
        client = anthropic.Anthropic(api_key=anthropic_key)
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            temperature=0.3,
            system=system_prompt,
            messages=messages
        )
        
        eic_answer = response.content[0].text.strip()
        
        # Validate response for transparency
        validator = MECCAResponseValidator()
        validation_result = validator.validate_response(eic_answer, specialist_responses)
        
        # Store validation results
        if 'validation_history' not in session_state:
            session_state.validation_history = []
        
        session_state.validation_history.append({
            'question': user_question,
            'response': eic_answer,
            'validation_flags': validation_result['flags'],
            'timestamp': datetime.now().isoformat()
        })
        
        # Log for debugging if enabled
        if st.secrets.get("ENABLE_LOGGING", False):
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "question": user_question,
                "eic_response": eic_answer,
                "validation_flags": validation_result.get('flags', [])
            }
            st.write("DEBUG LOG:", log_data)
        
        # Add validation warnings if needed
        if validation_result['flags']:
            eic_answer += f"\n\n⚠️ Transparency Note: This response has been flagged for review: {', '.join(validation_result['flags'])}"
        
        return eic_answer
        
    except Exception as e:
        return f"Dialogue Error: {str(e)}"

# Legacy function for backward compatibility
def enhanced_dialogue_handler(user_question, session_state, anthropic_key):
    """Legacy wrapper for enhanced_dialogue_handler_v2"""
    return enhanced_dialogue_handler_v2(user_question, session_state, anthropic_key)
