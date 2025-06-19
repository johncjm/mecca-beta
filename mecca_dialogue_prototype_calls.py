import os
import re
import difflib
import openai
import anthropic
import google.generativeai as genai
import requests
import streamlit as st
from typing import Dict, List, Tuple, Optional

def call_openai(prompt, api_key):
    """Call OpenAI GPT-4 API"""
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling GPT-4: {str(e)}"

def call_anthropic(prompt, combined_analysis, api_key):
    """Call Anthropic Claude API - for EiC synthesis"""
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        # For EiC synthesis, use the combined analysis
        full_prompt = f"{prompt}\n\nEditor responses to synthesize:\n{combined_analysis}"
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            temperature=0.3,
            messages=[{"role": "user", "content": full_prompt}]
        )
        return response.content[0].text
    except Exception as e:
        return f"Error calling Claude: {str(e)}"

def call_anthropic_dialogue(messages, api_key):
    """Call Anthropic Claude API for interactive dialogue with EiC"""
    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,  # Shorter responses for dialogue
            temperature=0.3,
            messages=messages
        )
        return response.content[0].text
    except Exception as e:
        return f"Error in dialogue: {str(e)}"

def call_google(prompt, api_key):
    """Call Google Gemini API"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.3,
                'max_output_tokens': 2000,
            }
        )
        return response.text
    except Exception as e:
        return f"Error calling Gemini: {str(e)}"

def call_perplexity(prompt, api_key):
    """Call Perplexity API with enhanced verification capabilities"""
    try:
        # Check if we have a valid API key
        if not api_key or api_key == "placeholder-for-now":
            return "Perplexity API key not configured - skipping real-time verification"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2000,
            "temperature": 0.3
        }
        
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=data,
            timeout=45  # Increased timeout for web searches
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"Perplexity API Error: HTTP {response.status_code} - {response.text[:200]}"
            
    except requests.exceptions.Timeout:
        return "Perplexity API timeout - web search took too long"
    except requests.exceptions.RequestException as e:
        return f"Perplexity network error: {str(e)}"
    except Exception as e:
        return f"Perplexity unexpected error: {str(e)}"

class MECCAResponseValidator:
    """Validates that Claude EiC accurately represents specialist responses"""
    
    def __init__(self, specialist_responses: Dict[str, str]):
        """
        Initialize with the actual specialist responses
        Args:
            specialist_responses: Dict with keys 'gpt', 'gemini', 'perplexity'
        """
        self.specialist_responses = specialist_responses
        self.validation_flags = []
    
    def validate_claude_response(self, claude_response: str) -> Dict:
        """
        Validate Claude's response for accuracy and transparency
        Returns validation report with flags and recommendations
        """
        self.validation_flags = []
        
        # Check for quotes and their accuracy
        quote_accuracy = self._validate_quotes(claude_response)
        
        # Check for forbidden behaviors
        forbidden_behaviors = self._check_forbidden_behaviors(claude_response)
        
        # Check for transparency requirements
        transparency_check = self._check_transparency(claude_response)
        
        # Check for educational opportunities from failures
        educational_opportunities = self._check_educational_use_of_failures(claude_response)
        
        return {
            'overall_valid': len(self.validation_flags) == 0,
            'quote_accuracy': quote_accuracy,
            'forbidden_behaviors': forbidden_behaviors,
            'transparency_score': transparency_check,
            'educational_value': educational_opportunities,
            'flags': self.validation_flags,
            'recommendations': self._generate_recommendations()
        }
    
    def _validate_quotes(self, claude_response: str) -> Dict:
        """Check if quotes from specialists are accurate"""
        quote_issues = []
        
        # Find all quoted text in Claude's response
        quotes = re.findall(r'"([^"]*)"', claude_response)
        
        for quote in quotes:
            if len(quote) > 10:  # Ignore short quotes like "yes" or "no"
                # Check if this quote actually appears in any specialist response
                found_in_specialist = False
                closest_match = None
                
                for specialist, response in self.specialist_responses.items():
                    if response and quote.lower() in response.lower():
                        found_in_specialist = True
                        break
                    
                    # Check for close matches (paraphrasing detection)
                    if response:
                        similarity = difflib.SequenceMatcher(None, quote.lower(), response.lower()).ratio()
                        if similarity > 0.7:  # Likely paraphrasing
                            closest_match = (specialist, similarity)
                
                if not found_in_specialist:
                    if closest_match:
                        quote_issues.append({
                            'type': 'likely_paraphrase',
                            'quote': quote,
                            'specialist': closest_match[0],
                            'similarity': closest_match[1]
                        })
                        self.validation_flags.append(f"Possible paraphrase detected: '{quote[:50]}...'")
                    else:
                        quote_issues.append({
                            'type': 'fabricated_quote',
                            'quote': quote
                        })
                        self.validation_flags.append(f"Fabricated quote detected: '{quote[:50]}...'")
        
        return {
            'total_quotes': len([q for q in quotes if len(q) > 10]),
            'issues': quote_issues,
            'accuracy_score': 1.0 - (len(quote_issues) / max(len([q for q in quotes if len(q) > 10]), 1))
        }
    
    def _check_forbidden_behaviors(self, claude_response: str) -> List[str]:
        """Check for forbidden behaviors in Claude's response"""
        violations = []
        
        # Check for performance inflation language
        inflation_phrases = [
            "all specialists caught",
            "my team successfully identified", 
            "properly verified",
            "comprehensive analysis revealed"
        ]
        
        for phrase in inflation_phrases:
            if phrase.lower() in claude_response.lower():
                violations.append(f"Performance inflation detected: '{phrase}'")
                self.validation_flags.append(f"FORBIDDEN: Performance inflation - '{phrase}'")
        
        # Check for selective quoting (mentioning specialist without showing their actual words)
        specialist_mentions = re.findall(r'my (gpt-4|gemini|perplexity|fact-checker|copy editor)', 
                                       claude_response.lower())
        
        for mention in specialist_mentions:
            # Look for actual quotes following the mention
            mention_index = claude_response.lower().find(mention)
            following_text = claude_response[mention_index:mention_index+200]
            
            if '"' not in following_text and "said:" not in following_text.lower():
                violations.append(f"Referenced {mention} without providing exact quote")
                self.validation_flags.append(f"FORBIDDEN: Referenced {mention} without quote")
        
        return violations
    
    def _check_transparency(self, claude_response: str) -> float:
        """Check how well Claude demonstrates transparency about AI limitations"""
        transparency_indicators = 0
        total_possible = 5
        
        # Check for acknowledgment of AI limitations
        limitation_phrases = [
            "ai limitations", "cannot rely solely", "demonstrates why", 
            "this shows", "missed", "failed to", "incorrectly"
        ]
        
        for phrase in limitation_phrases:
            if phrase.lower() in claude_response.lower():
                transparency_indicators += 1
                break
        
        # Check for educational framing of failures
        educational_phrases = [
            "teaching moment", "demonstrates", "shows why", "example of"
        ]
        
        for phrase in educational_phrases:
            if phrase.lower() in claude_response.lower():
                transparency_indicators += 1
                break
        
        # Check for honest assessment language
        honest_phrases = [
            "actually", "let me be honest", "completely missed", "failed to catch"
        ]
        
        for phrase in honest_phrases:
            if phrase.lower() in claude_response.lower():
                transparency_indicators += 1
                break
        
        # Check for proper specialist error acknowledgment
        if any(specialist_name in claude_response.lower() for specialist_name in ['gpt', 'gemini', 'perplexity']):
            if any(error_word in claude_response.lower() for error_word in ['missed', 'wrong', 'incorrect', 'failed']):
                transparency_indicators += 1
        
        # Check for "Not an Oracle" messaging
        oracle_phrases = [
            "not an oracle", "human verification", "double-check", "independently verify"
        ]
        
        for phrase in oracle_phrases:
            if phrase.lower() in claude_response.lower():
                transparency_indicators += 1
                break
        
        return transparency_indicators / total_possible
    
    def _check_educational_use_of_failures(self, claude_response: str) -> Dict:
        """Check if Claude is using AI failures as educational opportunities"""
        educational_elements = []
        
        # Look for specific educational patterns
        if "this demonstrates" in claude_response.lower():
            educational_elements.append("Uses demonstrative teaching")
        
        if any(word in claude_response.lower() for word in ["why", "because", "shows that"]):
            educational_elements.append("Provides explanatory reasoning")
        
        if "human oversight" in claude_response.lower() or "verification" in claude_response.lower():
            educational_elements.append("Emphasizes human verification importance")
        
        # Check for specific error analysis
        error_analysis_phrases = [
            "missed this", "failed to catch", "incorrectly stated", "should have"
        ]
        
        for phrase in error_analysis_phrases:
            if phrase.lower() in claude_response.lower():
                educational_elements.append("Analyzes specific errors")
                break
        
        return {
            'educational_elements': educational_elements,
            'educational_score': len(educational_elements) / 4  # Max 4 elements
        }
    
    def _verify_performance_claim(self, claim: str, claude_response: str) -> bool:
        """Verify if a performance claim made by Claude is actually supported by specialist responses"""
        # Conservative approach - flag all performance claims for review
        return False
    
    def _generate_recommendations(self) -> List[str]:
        """Generate specific recommendations based on validation results"""
        recommendations = []
        
        if any("fabricated_quote" in str(flag) for flag in self.validation_flags):
            recommendations.append("CRITICAL: Stop fabricating quotes. Only use exact text from specialist responses.")
        
        if any("paraphrase" in str(flag) for flag in self.validation_flags):
            recommendations.append("Use exact quotes instead of paraphrasing. Students need to see actual AI output.")
        
        if len(self.validation_flags) > 3:
            recommendations.append("Major transparency issues detected. Review prompt compliance requirements.")
        
        recommendations.append("Remember: Your role is educational transparency, not AI performance advocacy.")
        
        return recommendations

def enhanced_dialogue_handler_with_validation(user_question, st_session_state, anthropic_key):
    """Enhanced dialogue handler with validation system"""
    
    # Import the enhanced dialogue prompt function
    from mecca_dialogue_prototype_prompts import get_enhanced_dialogue_system_prompt
    
    # Prepare enhanced dialogue messages with individual responses
    system_prompt = get_enhanced_dialogue_system_prompt(
        st_session_state.original_article, 
        st_session_state.eic_summary, 
        st_session_state.context,
        st_session_state.editor_responses
    )
    
    # Build conversation history
    messages = [{"role": "user", "content": system_prompt}]
    
    # Add previous dialogue
    for exchange in st_session_state.dialogue_history:
        messages.append({"role": "user", "content": exchange["question"]})
        messages.append({"role": "assistant", "content": exchange["answer"]})
    
    # Add current question
    messages.append({"role": "user", "content": user_question})
    
    # Get response from Claude
    eic_answer = call_anthropic_dialogue(messages, anthropic_key)
    
    # VALIDATION STEP
    if st_session_state.editor_responses:
        validator = MECCAResponseValidator(st_session_state.editor_responses)
        validation_result = validator.validate_claude_response(eic_answer)
        
        # Store validation metrics for analysis
        if 'validation_history' not in st_session_state:
            st_session_state.validation_history = []
        
        st_session_state.validation_history.append({
            'question': user_question,
            'answer': eic_answer,
            'validation': validation_result
        })
        
        # Log validation results for debugging
        if not validation_result['overall_valid']:
            print(f"MECCA VALIDATION FLAGS: {validation_result['flags']}")
            print(f"TRANSPARENCY SCORE: {validation_result['transparency_score']}")
            print(f"RECOMMENDATIONS: {validation_result['recommendations']}")
            
            # In development mode, optionally show validation warnings
            if st.secrets.get("MECCA_DEBUG_MODE", False):
                debug_info = f"\n\n[DEBUG - Validation Issues: {len(validation_result['flags'])} flags]"
                eic_answer += debug_info
        
        return eic_answer, validation_result
    else:
        # No specialist responses available for validation
        return eic_answer, None

# Wrapper function for the main app to use
def enhanced_dialogue_handler(user_question, st_session_state, anthropic_key):
    """Production wrapper that returns just the answer"""
    result = enhanced_dialogue_handler_with_validation(user_question, st_session_state, anthropic_key)
    
    if isinstance(result, tuple):
        return result[0]  # Return just the answer
    else:
        return result
