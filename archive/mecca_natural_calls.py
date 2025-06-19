import os
import openai
import anthropic
import google.generativeai as genai
import requests
import streamlit as st

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
    """Call Perplexity API with web search capabilities"""
    try:
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
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"Error calling Perplexity: HTTP {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Error calling Perplexity: {str(e)}"
