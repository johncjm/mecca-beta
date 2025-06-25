# Add this to your temp_forms.py or create a new file: custom_fcc.py

import requests
import openai
import streamlit as st
import json

def call_custom_fact_checking_coach(prompt, openai_key, search_api_key, search_engine_id):
    """
    Custom Fact-Checking Coach using GPT-4o-mini + Google Custom Search
    Focuses on verification methodology coaching, not definitive fact-checking
    """
    if not openai_key or not search_api_key or not search_engine_id:
        return "Custom Fact-Checking Coach configuration incomplete. Please check API keys and Search Engine ID."
    
    try:
        client = openai.OpenAI(api_key=openai_key)
        
        # Step 1: Extract key claims for verification
        claim_extraction_prompt = f"""You are a verification methodology coach. Analyze this content and identify key factual claims that should be verified.

Focus on claims that are:
- Specific and verifiable (names, dates, numbers, events)
- Central to the story's credibility
- Potentially controversial or surprising

For each claim, provide:
1. The exact claim
2. Why it needs verification
3. What type of sources would be most authoritative

Content to analyze:
{prompt}

Format your response as a numbered list of claims with verification guidance."""

        # Extract claims using GPT-4o-mini
        claims_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a fact-checking methodology coach who teaches verification processes."},
                {"role": "user", "content": claim_extraction_prompt}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        claims_analysis = claims_response.choices[0].message.content.strip()
        
        # Step 2: Search for verification sources (limit to top 3 claims to control costs)
        search_results = []
        
        # Extract first few claims for searching (simple parsing)
        claims_text = claims_analysis.lower()
        search_queries = []
        
        # Simple claim extraction for search (this could be more sophisticated)
        lines = claims_analysis.split('\n')
        for line in lines[:3]:  # Limit to first 3 claims
            if any(keyword in line.lower() for keyword in ['claim:', '1.', '2.', '3.', '-']):
                # Extract potential search terms (simple approach)
                clean_line = line.replace('claim:', '').replace('1.', '').replace('2.', '').replace('3.', '').strip()
                if len(clean_line) > 10 and len(clean_line) < 100:
                    search_queries.append(clean_line[:80])  # Truncate long queries
        
        # Perform searches
        for i, query in enumerate(search_queries[:2]):  # Limit to 2 searches to control costs
            try:
                search_result = search_google_custom(query, search_api_key, search_engine_id)
                if search_result:
                    search_results.append({
                        'query': query,
                        'results': search_result.get('items', [])[:3]  # Top 3 results
                    })
            except Exception as search_error:
                search_results.append({
                    'query': query,
                    'error': str(search_error)
                })
        
        # Step 3: Generate verification coaching
        coaching_prompt = f"""You are a fact-checking methodology coach. Based on the claims analysis and search results below, provide educational guidance on verification methodology.

CLAIMS ANALYSIS:
{claims_analysis}

SEARCH RESULTS:
{json.dumps(search_results, indent=2)}

Provide coaching in this format:

**VERIFICATION METHODOLOGY COACHING**

**KNOWN vs. UNKNOWN FRAMEWORK:**

What We Can Assess:
• [List what can be evaluated from available sources]

What Needs Further Verification:
• [List what requires additional investigation]

**VERIFICATION ROADMAP:**
• [Specific steps for verification]
• [Recommended source types]
• [Methodology suggestions]

**SOURCE QUALITY ASSESSMENT:**
• [Evaluate the reliability of found sources]
• [Suggest additional authoritative sources to check]

**COACHING NOTES:**
• [Educational observations about verification challenges]
• [Methodology lessons from this verification exercise]

IMPORTANT: Focus on teaching verification methodology, not providing definitive true/false judgments. Explain the verification process and what a journalist should do next."""

        # Generate final coaching response
        coaching_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a fact-checking methodology coach who teaches verification processes, not a definitive fact-checker."},
                {"role": "user", "content": coaching_prompt}
            ],
            max_tokens=1500,
            temperature=0.3
        )
        
        final_coaching = coaching_response.choices[0].message.content.strip()
        
        # Add implementation note
        return f"""{final_coaching}

**IMPLEMENTATION NOTE:** This Custom Fact-Checking Coach uses GPT-4o-mini + Google Custom Search to teach verification methodology. It provides guidance on how to verify claims rather than definitive fact-checking results.

**COST ESTIMATE:** ~$0.06-0.13 per analysis (much lower than full Perplexity integration)"""
        
    except Exception as e:
        return f"Custom Fact-Checking Coach Error: {str(e)}\n\nThis is the experimental Custom FCC. Please verify all information independently."

def search_google_custom(query, api_key, search_engine_id):
    """Perform Google Custom Search"""
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': search_engine_id,
            'q': query,
            'num': 3,  # Limit results to control costs
            'safe': 'medium'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Google Custom Search API error: {str(e)}")
    except Exception as e:
        raise Exception(f"Search error: {str(e)}")

# Integration function to replace Perplexity calls
def call_custom_fcc_integrated(prompt, openai_key, search_api_key, search_engine_id):
    """
    Drop-in replacement for call_perplexity() function
    """
    return call_custom_fact_checking_coach(prompt, openai_key, search_api_key, search_engine_id)
