from typing import Dict, Any, Optional
import json
from app.ai.groq_client import get_groq_client
from app.ai.intent_parser import parse_navigation_intent
from app.ai.conversation import conversation_store
from app.ai.prompts import AI_RESPONSE_SYSTEM_PROMPT, GROQ_MODEL
from app.navigation.route_engine import get_route
from app.locations.places_engine import places_engine
from app.locations.resolver import resolver

def process_chat_message(session_id: str, message: str, current_location: Optional[str] = None) -> Dict[str, Any]:
    session = conversation_store.get_or_create(session_id)
    session.add_turn("user", message)
    if current_location:
        session.current_location = current_location
        
    intent = parse_navigation_intent(message)
    
    # Check if we need clarification based on intent
    if intent.get("needs_clarification"):
        response_text = intent.get("clarification_question", "Could you please clarify that?")
        session.add_turn("assistant", response_text)
        return {"response": response_text, "intent": intent}
        
    intent_type = intent.get("intent", "unknown")
    context_data = ""
    route_data = None
    places_data = None
    
    # Fallback to session context if not explicitly mentioned
    source = intent.get("source") or session.current_location or session.last_source
    destination = intent.get("destination") or session.last_destination
    
    if intent_type == "navigate":
        if not source:
            response_text = "Where are you starting from?"
            session.add_turn("assistant", response_text)
            return {"response": response_text, "intent": intent}
        if not destination:
            response_text = "Where would you like to go?"
            session.add_turn("assistant", response_text)
            return {"response": response_text, "intent": intent}
            
        route_data = get_route(source, destination)
        if route_data.get("success"):
            session.last_source = route_data["source"]["name"]
            session.last_destination = route_data["destination"]["name"]
            dist = route_data.get("distance_m", 0)
            time_m = route_data.get("estimated_time_min", 0)
            instructions = "\n".join([f"{i+1}. {step}" for i, step in enumerate(route_data.get("instructions", []))])
            context_data = f"ROUTE FOUND: From {session.last_source} to {session.last_destination}.\nDistance: {dist} metres. Time: {time_m} minutes.\nDirections:\n{instructions}"
        else:
            context_data = f"ERROR FINDING ROUTE: {route_data.get('error', 'Unknown error')}"
            
    elif intent_type in ["nearest_place", "category_search", "service_search", "place_search"]:
        category = intent.get("category")
        service = intent.get("service")
        near = intent.get("near") or source
        
        if intent_type == "nearest_place" and not near:
             response_text = "Where are you currently located to find the nearest one?"
             session.add_turn("assistant", response_text)
             return {"response": response_text, "intent": intent}
             
        if near:
            node_id = near if near.startswith("N_") else f"N_{near}"
            places_data = places_engine.get_nearest_places(node_id, category=category, service=service, limit=3)
            if places_data:
                context_data = f"FOUND NEARBY PLACES near {near}:\n"
                for p in places_data:
                    dist = p.get("walking_distance_m", "unknown")
                    context_data += f"- {p['name']} (Distance: {dist}m)\n"
            else:
                context_data = "NO PLACES FOUND matching that description nearby."
        else:
            query = intent.get("destination") or ""
            places_data = places_engine.search_places(query=query, category=category, service=service)
            if places_data:
                context_data = "FOUND PLACES:\n"
                for p in places_data[:5]:
                    context_data += f"- {p['name']} ({p.get('campus_area', '')})\n"
            else:
                context_data = "NO PLACES FOUND matching that description."
                
    elif intent_type in ["department_search", "block_info"]:
        dept = intent.get("department")
        # Try to resolve to a block
        loc, conf = resolver.resolve(dept or destination or message)
        if loc:
            context_data = f"FOUND LOCATION: {loc['name']}. Type: {loc.get('type')}. Description: {loc.get('description', '')}"
            if loc.get("departments"):
                context_data += f". Departments: {', '.join(loc['departments'])}"
        else:
            context_data = "COULD NOT FIND information about that department or block."
    else:
        context_data = "Could not understand the exact navigation intent. Answer conversationally based on history."

    # Call LLM to generate response
    client = get_groq_client()
    
    messages = [
        {"role": "system", "content": AI_RESPONSE_SYSTEM_PROMPT},
    ]
    
    # Add recent history
    history = session.get_history()
    # take last 4 turns for context window to not overflow
    for turn in history[-4:]:
        messages.append(turn)
        
    # Append the backend context as a system message right before the final generation
    if context_data:
        messages.append({"role": "system", "content": f"BACKEND DATA (Use this to answer the user):\n{context_data}"})
        
    try:
        response = client.chat.completions.create(
            messages=messages,
            model=GROQ_MODEL,
            temperature=0.3,
            max_tokens=256
        )
        ai_text = response.choices[0].message.content.strip()
        
        # Strip Qwen3 thinking blocks if present
        if "<think>" in ai_text:
            think_end = ai_text.find("</think>")
            if think_end != -1:
                ai_text = ai_text[think_end + 8:].strip()
                
        session.add_turn("assistant", ai_text)
        
        return {
            "response": ai_text,
            "intent": intent,
            "route": route_data,
            "places": places_data
        }
    except Exception as e:
        error_msg = f"Sorry, I am having trouble connecting to my brain right now. ({str(e)})"
        session.add_turn("assistant", error_msg)
        return {
            "response": error_msg,
            "error": str(e)
        }
