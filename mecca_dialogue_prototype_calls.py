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
                closest_match
