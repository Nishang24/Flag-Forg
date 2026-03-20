import re
import os
import json
from typing import Dict, Any
from datetime import datetime, timedelta

try:
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "sk-proj-your-key-here":
        client = OpenAI(api_key=api_key)
        LLM_AVAILABLE = True
    else:
        client = None
        LLM_AVAILABLE = False
        print("⚠️  Using regex-based parsing (demo mode)")
except Exception as e:
    client = None
    LLM_AVAILABLE = False
    print(f"⚠️  LLM unavailable: {e}. Using regex parsing")

def parse_intent(transcription: str) -> Dict[str, Any]:
    """Advanced voice parsing for 25+ industrial features"""
    if LLM_AVAILABLE:
        try:
            return call_llm_for_intent(transcription)
        except Exception as e:
            print(f"⚠️  LLM failed: {e}, using regex")
            return parse_intent_regex(transcription)
    else:
        return parse_intent_regex(transcription)

def call_llm_for_intent(text: str) -> Dict[str, Any]:
    """GPT-4o parsing for advanced industrial commands"""
    prompt = f"""
    Extract action information from this kitchenware industry voice command:
    "{text}"
    
    Return ONLY valid JSON:
    {{
        "entity_type": "worker|inventory|task|shift|order|complaint|quality|equipment|safety|training|schedule|report|maintenance|cost|attendance|leave",
        "action": "create|update|delete|list|assign|report|check|complete|approve|reject",
        "primary_input": "extracted name/title",
        "priority": "Low|Medium|High|Critical|null",
        "quantity": "number|null",
        "category": "category if applicable|null",
        "reason": "reason if applicable|null",
        "date": "date if mentioned|null",
        "status": "status if mentioned|null",
        "additional_details": "any other relevant info|null"
    }}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=400
    )
    
    return json.loads(response.choices[0].message.content)

def parse_intent_regex(transcription: str) -> Dict[str, Any]:
    """Regex-based parsing for all 25+ features"""
    text_lower = transcription.lower()
    
    # ===== ENTITY TYPE DETECTION =====
    entity_type = detect_entity_type(text_lower)
    action = detect_action(text_lower)
    
    # ===== EXTRACT COMMON FIELDS =====
    name_match = re.search(r"(?:add|create|for|named|called|worker|employee|item) (?:a |an )?(.+?)(?:\s+(?:to|with|in|as|for)|$)", text_lower)
    primary_input = name_match.group(1).strip().title() if name_match else transcription[:50].title()
    
    # Quantity extraction
    quantity = None
    qty_match = re.search(r"(\d+)\s+(?:kg|liters|pieces|units|items|bottles|boxes|hours|days)", text_lower)
    if qty_match:
        quantity = int(qty_match.group(1))
    
    # Priority
    priority = extract_priority(text_lower)
    
    # Category/Status
    category = extract_category(text_lower, entity_type)
    status = extract_status(text_lower, entity_type)
    
    # Reason
    reason = extract_reason(text_lower, entity_type)
    
    # Date
    date_str = extract_date(text_lower)
    
    return {
        "entity_type": entity_type,
        "action": action,
        "primary_input": primary_input,
        "priority": priority,
        "quantity": quantity,
        "category": category,
        "status": status,
        "reason": reason,
        "date": date_str,
        "additional_details": None,
        "confidence": 0.85
    }

def detect_entity_type(text: str) -> str:
    """Detect what entity the command is about"""
    entity_keywords = {
        "worker": ["worker", "employee", "staff", "chef", "manager", "person", "hire"],
        "inventory": ["inventory", "stock", "item", "ingredient", "material", "equipment", "flour", "oil", "salt"],
        "task": ["task", "job", "work", "production", "create task", "assign task"],
        "shift": ["shift", "morning", "evening", "night", "schedule shift", "assign shift"],
        "order": ["order", "customer", "delivery", "shipment", "purchase"],
        "complaint": ["complaint", "issue", "problem", "defect", "quality issue"],
        "quality": ["quality", "check", "inspect", "test", "pass", "fail", "temperature"],
        "equipment": ["equipment", "oven", "mixer", "fryer", "machine", "device", "maintenance"],
        "safety": ["safety", "incident", "injury", "accident", "hazard", "check"],
        "training": ["training", "course", "certification", "learn", "educate"],
        "schedule": ["schedule", "planning", "production schedule", "plan"],
        "report": ["report", "daily", "summary", "analytics", "statistics"],
        "maintenance": ["maintenance", "repair", "service", "technician"],
        "cost": ["cost", "expense", "price", "budget", "spending"],
        "attendance": ["attendance", "checkin", "checkout", "present", "absent"],
        "leave": ["leave", "vacation", "sick", "absence", "day off"]
    }
    
    for entity, keywords in entity_keywords.items():
        if any(kw in text for kw in keywords):
            return entity
    
    return "task"  # Default

def detect_action(text: str) -> str:
    """Detect the ACTION to perform"""
    if any(w in text for w in ["add", "create", "new", "register", "hire", "record"]):
        return "create"
    elif any(w in text for w in ["update", "modify", "change", "set", "mark", "assign"]):
        return "update"
    elif any(w in text for w in ["delete", "remove", "fire"]):
        return "delete"
    elif any(w in text for w in ["list", "show", "display", "get", "all", "view"]):
        return "list"
    elif any(w in text for w in ["check", "inspect", "verify", "test"]):
        return "check"
    elif any(w in text for w in ["complete", "finish", "done", "mark done"]):
        return "complete"
    elif any(w in text for w in ["approve", "accept", "yes"]):
        return "approve"
    elif any(w in text for w in ["reject", "deny", "no"]):
        return "reject"
    elif any(w in text for w in ["report", "summary", "generate"]):
        return "report"
    else:
        return "create"

def extract_priority(text: str) -> str:
    """Extract priority level"""
    if "critical" in text:
        return "Critical"
    elif "high" in text or "urgent" in text:
        return "High"
    elif "medium" in text or "normal" in text:
        return "Medium"
    elif "low" in text:
        return "Low"
    return None

def extract_category(text: str, entity_type: str) -> str:
    """Extract category based on entity type"""
    if entity_type == "inventory":
        if "ingredient" in text or "raw" in text:
            return "Raw Materials"
        elif "equipment" in text or "machine" in text:
            return "Equipment"
        elif "supply" in text or "packaging" in text:
            return "Supplies"
        elif "product" in text:
            return "Finished Products"
    elif entity_type == "complaint":
        if "quality" in text:
            return "Quality"
        elif "delivery" in text:
            return "Delivery"
        elif "packaging" in text:
            return "Packaging"
        elif "taste" in text:
            return "Taste"
    elif entity_type == "safety":
        if "injury" in text or "incident" in text:
            return "Injury"
        elif "near miss" in text:
            return "Near Miss"
        elif "damage" in text:
            return "Property Damage"
    
    return None

def extract_status(text: str, entity_type: str) -> str:
    """Extract status"""
    if entity_type == "worker":
        if "active" in text or "working" in text:
            return "Active"
        elif "leave" in text or "absence" in text:
            return "On Leave"
        elif "inactive" in text or "off" in text:
            return "Inactive"
    elif entity_type == "task":
        if "complete" in text or "done" in text or "finished" in text:
            return "Done"
        elif "progress" in text or "running" in text or "start" in text:
            return "In Progress"
        else:
            return "Todo"
    elif entity_type == "quality":
        if "pass" in text:
            return "Pass"
        elif "fail" in text:
            return "Fail"
    elif entity_type == "order":
        if "delivered" in text:
            return "Delivered"
        elif "shipped" in text:
            return "Shipped"
        elif "processing" in text:
            return "Processing"
        else:
            return "Pending"
    elif entity_type == "complaint":
        if "resolved" in text or "fixed" in text:
            return "Resolved"
        elif "open" in text:
            return "Open"
        elif "in progress" in text:
            return "In Progress"
    
    return None

def extract_reason(text: str, entity_type: str) -> str:
    """Extract reason for action"""
    if entity_type == "complaint":
        if "defective" in text or "broken" in text:
            return "Defective"
        elif "expired" in text:
            return "Expired"
        elif "wrong" in text:
            return "Wrong Item"
    elif entity_type == "waste":
        if "expired" in text:
            return "Expired"
        elif "damaged" in text:
            return "Damaged"
        elif "spillage" in text:
            return "Spillage"
    elif entity_type == "leave":
        if "sick" in text:
            return "Sick"
        elif "vacation" in text:
            return "Vacation"
        elif "personal" in text:
            return "Personal"
    elif entity_type == "safety":
        if "injury" in text:
            return "Injury"
        elif "near miss" in text:
            return "Near Miss"
    
    return None

def extract_date(text: str) -> str:
    """Extract date references"""
    today = datetime.now().date()
    
    if "today" in text:
        return today.isoformat()
    elif "tomorrow" in text:
        return (today + timedelta(days=1)).isoformat()
    elif "yesterday" in text:
        return (today - timedelta(days=1)).isoformat()
    elif "next week" in text:
        return (today + timedelta(days=7)).isoformat()
    elif "next month" in text:
        return (today + timedelta(days=30)).isoformat()
    
    # Try to extract explicit dates (YYYY-MM-DD or MM-DD)
    date_match = re.search(r"(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?", text)
    if date_match:
        return f"20{date_match.group(3) or today.year}-{date_match.group(1)}-{date_match.group(2)}"
    
    return None

# Additional utility functions for specific features
def extract_department(text: str) -> str:
    """Extract department"""
    if "kitchen" in text:
        return "Kitchen"
    elif "storage" in text:
        return "Storage"
    elif "quality" in text or "quality control" in text:
        return "Quality Control"
    elif "admin" in text or "office" in text:
        return "Admin"
    elif "packaging" in text:
        return "Packaging"
    return None

def extract_severity(text: str) -> str:
    """Extract severity level"""
    if "critical" in text or "major" in text:
        return "Critical"
    elif "high" in text or "severe" in text:
        return "High"
    elif "medium" in text or "moderate" in text:
        return "Medium"
    elif "low" in text or "minor" in text:
        return "Low"
    return "Medium"

def extract_temperature(text: str) -> float:
    """Extract temperature value"""
    temp_match = re.search(r"(\d+)\s*(?:degrees|°|C|F)", text)
    if temp_match:
        return float(temp_match.group(1))
    return None

def extract_cost(text: str) -> float:
    """Extract cost/price value"""
    cost_match = re.search(r"[\$]{0,1}(\d+(?:\.\d{2})?)", text)
    if cost_match:
        return float(cost_match.group(1))
    return None
