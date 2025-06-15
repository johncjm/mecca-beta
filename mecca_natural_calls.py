# mecca_natural_calls.py
# Enhanced version with advanced options support
# Core API orchestration for MECCA editorial system

import os
import openai
import anthropic
import google.generativeai as genai
import requests
from dotenv import load_dotenv
from mecca_natural_prompts import get_editorial_prompt, get_eic_synthesis_prompt, get_model_display_name

# Load environment variables
load_dotenv()

def call_openai_gpt4(prompt):
    """Call OpenAI GPT-4 API"""
    try:
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling GPT-4: {str(e)}"

def call_anthropic_claude(prompt):
    """Call Anthropic Claude API"""
    try:
        client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        return f"Error calling Claude: {str(e)}"

def call_google_gemini(prompt):
    """Call Google Gemini API"""
    try:
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
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

def call_perplexity(prompt):
    """Call Perplexity API with web search capabilities"""
    try:
        headers = {
            "Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}",
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
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"Error calling Perplexity: HTTP {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Error calling Perplexity: {str(e)}"

def preprocess_article_with_paragraphs(article_text):
    """Add paragraph numbers to article text for easier reference"""
    if not article_text.strip():
        return article_text
    
    # Split into paragraphs (by double newlines or single newlines)
    paragraphs = [p.strip() for p in article_text.split('\n') if p.strip()]
    
    # Add paragraph numbers
    numbered_paragraphs = []
    for i, paragraph in enumerate(paragraphs, 1):
        numbered_paragraphs.append(f"Paragraph {i}: {paragraph}")
    
    return '\n\n'.join(numbered_paragraphs)

def get_model_response(model_name, article_text, writer_role, advanced_options=None):
    """Get response from specified model with advanced options"""
    # Preprocess article with paragraph numbers for easier reference
    numbered_article = preprocess_article_with_paragraphs(article_text)
    
    prompt = get_editorial_prompt(model_name, numbered_article, writer_role, advanced_options)
    
    if model_name == "gpt-4o":
        return call_openai_gpt4(prompt)
    elif model_name == "gemini":
        return call_google_gemini(prompt)
    elif model_name == "claude":
        return call_anthropic_claude(prompt)
    elif model_name == "perplexity":
        return call_perplexity(prompt)
    else:
        return f"Unknown model: {model_name}"

def get_complete_editorial_review(article_text, selected_models, writer_role="professional", advanced_options=None):
    """
    Get complete editorial review from selected models plus EiC synthesis
    
    Args:
        article_text (str): The article to review
        selected_models (list): List of model names to use as editors
        writer_role (str): Role of the writer (student/professional/other)
        advanced_options (dict): Advanced configuration options
    
    Returns:
        dict: Contains EiC synthesis and individual model responses
    """
    
    # Default advanced options if none provided
    if advanced_options is None:
        advanced_options = {
            "content_type": "News Article",
            "target_audience": "General readers",
            "process_stage": "Draft review",
            "category_focus": "Comprehensive review",
            "style_guide": "AP",
            "target_length": None,
            "editor_context": None
        }
    
    # Get responses from selected editor models
    model_responses = {}
    
    for model in selected_models:
        print(f"Getting feedback from {get_model_display_name(model)}...")
        response = get_model_response(model, article_text, writer_role, advanced_options)
        model_responses[model] = response
    
    # Ensure we have responses for EiC synthesis (pad with empty if needed)
    gpt_response = model_responses.get("gpt-4o", "No feedback provided from GPT-4.")
    gemini_response = model_responses.get("gemini", "No feedback provided from Gemini.")
    claude_response = model_responses.get("claude", "No feedback provided from Claude.")
    perplexity_response = model_responses.get("perplexity", "No feedback provided from Perplexity.")
    
    # Get Editor-in-Chief synthesis from Claude
    print("Generating Editor-in-Chief synthesis...")
    eic_prompt = get_eic_synthesis_prompt(
        gpt_response, 
        gemini_response, 
        claude_response, 
        perplexity_response, 
        writer_role,
        advanced_options
    )
    
    eic_synthesis = call_anthropic_claude(eic_prompt)
    
    return {
        "eic_synthesis": eic_synthesis,
        "individual_responses": model_responses,
        "selected_models": selected_models,
        "writer_role": writer_role,
        "advanced_options": advanced_options
    }

def test_api_connections():
    """Test all API connections"""
    test_prompt = "Hello, please respond with just 'API working' to test the connection."
    
    results = {}
    
    # Test OpenAI
    try:
        results["openai"] = call_openai_gpt4(test_prompt)
    except Exception as e:
        results["openai"] = f"Failed: {str(e)}"
    
    # Test Anthropic
    try:
        results["anthropic"] = call_anthropic_claude(test_prompt)
    except Exception as e:
        results["anthropic"] = f"Failed: {str(e)}"
    
    # Test Google
    try:
        results["google"] = call_google_gemini(test_prompt)
    except Exception as e:
        results["google"] = f"Failed: {str(e)}"
    
    # Test Perplexity
    try:
        results["perplexity"] = call_perplexity(test_prompt)
    except Exception as e:
        results["perplexity"] = f"Failed: {str(e)}"
    
    return results

if __name__ == "__main__":
    # Test API connections when run directly
    print("Testing API connections...")
    results = test_api_connections()
    
    for service, result in results.items():
        print(f"{service}: {result}")
