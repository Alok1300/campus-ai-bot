import json
from app.ai.groq_client import get_groq_client
from app.ai.prompts import INTENT_PARSING_SYSTEM_PROMPT

def parse_navigation_intent(user_message: str) -> dict:
    client = get_groq_client()
    
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": INTENT_PARSING_SYSTEM_PROMPT},
                # /no_think suppresses Qwen3's chain-of-thought so we get raw JSON directly
                {"role": "user", "content": f"/no_think {user_message}"}
            ],
            model="qwen/qwen3.8-27b",
            temperature=0,
            max_tokens=512
        )
        
        content = response.choices[0].message.content.strip()
        # Strip Qwen3 thinking blocks if present (<think>...</think>)
        if "<think>" in content:
            think_end = content.find("</think>")
            if think_end != -1:
                content = content[think_end + 8:].strip()
        # Clean up any potential markdown code blocks
        if content.startswith("```json"):
            content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
        elif content.startswith("```"):
            content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
        return json.loads(content.strip())
    except Exception as e:
        return {
            "error": "Failed to parse intent",
            "details": str(e)
        }
