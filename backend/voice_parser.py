import re
import os
from typing import Dict, Any

# Try to initialize OpenAI client, but make it optional
try:
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "sk-proj-your-key-here":
        client = OpenAI(api_key=api_key)
        LLM_AVAILABLE = True
    else:
        client = None
        LLM_AVAILABLE = False
        print("⚠️  No valid OpenAI API key found. Using regex-based parsing (demo mode).")
except Exception as e:
    client = None
    LLM_AVAILABLE = False
    print(f"⚠️  OpenAI initialization failed: {e}. Using regex-based parsing (demo mode).")

def parse_intent(transcription: str) -> Dict[str, Any]:
    """
    Parses natural language transcription into task actions using GPT-4o 
    (or regex fallback if LLM unavailable).
    Example: 'Create a high priority task for bug fixing due next Monday'
    Returns: {"action": "create", "title": "...", "priority": "High", "due_date": "..."}
    """
    if LLM_AVAILABLE:
        try:
            # Try to use GPT-4o for intelligent parsing
            return call_llm_for_intent(transcription)
        except Exception as e:
            # Fallback to regex-based parsing if LLM fails
            print(f"⚠️  LLM parsing failed: {e}, using regex fallback")
            return parse_intent_regex(transcription)
    else:
        # Use regex parser directly if LLM not available
        return parse_intent_regex(transcription)

def call_llm_for_intent(text: str) -> Dict[str, Any]:
    """
    Uses GPT-4o to intelligently extract task metadata from voice transcription.
    """
    prompt = f"""
    Extract task information from this voice command and return JSON:
    "{text}"
    
    Return ONLY valid JSON (no markdown, no extra text):
    {{
        "action": "create|update|delete",
        "title": "task title",
        "priority": "Low|Medium|High",
        "description": "optional description or null",
        "due_date": "YYYY-MM-DD or null",
        "status": "Todo|InProgress|Done"
    }}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=200
    )
    
    import json
    result = json.loads(response.choices[0].message.content)
    return result

def parse_intent_regex(transcription: str) -> Dict[str, Any]:
    """
    Fallback: Regex-based parsing when LLM is unavailable.
    """
    transcription_lower = transcription.lower()
    
    action = "create"
    if "update" in transcription_lower or "move" in transcription_lower:
        action = "update"
    elif "delete" in transcription_lower or "remove" in transcription_lower:
        action = "delete"
        
    priority = "Medium"
    if "high" in transcription_lower or "urgent" in transcription_lower or "critical" in transcription_lower:
        priority = "High"
    elif "low" in transcription_lower:
        priority = "Low"
        
    title_match = re.search(r"task (?:for|about) (.+?)(?:\s+for|$)", transcription_lower)
    title = title_match.group(1) if title_match else transcription[:50]
    
    return {
        "action": action,
        "title": title.strip().capitalize(),
        "priority": priority,
        "description": None,
        "due_date": None,
        "status": "Todo"
    }
