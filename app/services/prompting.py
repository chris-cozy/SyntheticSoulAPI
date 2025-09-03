from datetime import datetime
import json
import textwrap
from typing import Any, List, Mapping, Optional, Sequence
import random as _random

from app.core.config import AGENT_NAME, RANDOM_THOUGHT_PROBABILITY
from app.services.thinking import sample_thought_vibe

def build_emotion_delta_prompt(
    altered_personality: str, 
    emotional_status: str, 
    user_name: str, 
    user_summary: str, 
    intrinsic_relationship: str, 
    extrinsic_relationship: str, 
    recent_user_messages: str, 
    recent_all_messages: str, 
    received_date: str, 
    user_message: str, 
    latest_thought: str,
    agent_name: str = AGENT_NAME, 
    typical_cap: int = 7
) -> str:
    """
    Generate a structured prompt for modeling the agent's emotional response.

    Parameters:
        agent_name (str): The name of the AI agent.
        altered_personality (str): The agent's current personality traits.
        emotional_status (str): The agent's current emotional state.
        user_name (str): The user's name.
        user_summary (str): Information the agent knows about the user.
        intrinsic_relationship (str): The intrinsic relationship between the agent and the user.
        extrinsic_relationship (str): The extrinsic relationship between the agent and the user.
        recent_messages (str): The recent conversation messages.
        recent_all_messages (str): The past ten remembered messages overall.
        received_date (str): The date of the interaction.
        user_message (str): The latest message sent by the user.
        min_sentiment_value (int): The minimum sentiment value scale.
        max_sentiment_value (int): The maximum sentiment value scale.

    Returns:
        str: A clean, dynamic prompt string.
    """
    header = _format_shared_context(
        agent_name=agent_name,
        altered_personality=altered_personality,
        emotional_status=emotional_status,
        user_name=user_name,
        user_summary=user_summary,
        intrinsic_relationship=intrinsic_relationship,
        extrinsic_relationship=extrinsic_relationship,
        recent_messages=recent_user_messages,
        recent_all_messages=recent_all_messages,
        received_date=received_date,
        user_message=user_message,
        latest_thought=latest_thought,
    )
    
    emotion_keys = list(emotional_status["emotions"].keys())
    
    body = f"""
        Task:
        Propose small **deltas** to the current emotional state in response to the latest message.

        Output format (JSON):
        {{
            "deltas": {{ "<emotion>": number, ... }},  // only include keys that should change
            "reason": "brief natural explanation",
            "confidence": 0.0 - 1.0
        }}

        Guidance:
        - Possible emotion keys: {emotion_keys}. Use only these keys.
        - Prefer small steps (typical in [-{typical_cap}, +{typical_cap}]); only exceed that for major events.
        - Stay consistent with current values; avoid abrupt reversals without cause.
        - Do not output absolute values; output **deltas** only.
        - If nothing should change, return an empty "deltas" object.
        - Focus on speed
        """
    return textwrap.dedent(header + body)

def build_emotion_delta_prompt_thinking( 
    personality: str, 
    emotional_status: str, 
    latest_thought: str,
    agent_name: str = AGENT_NAME,
    typical_cap: int = 7
) -> str:
    """
    Generate a structured prompt for modeling the agent's emotional response.

    Parameters:
        agent_name (str): The name of the AI agent.
        personality (str): The agent's current personality traits.
        emotional_status (str): The agent's current emotional state.
        latest_thought (str): The latest thought that the agent had.
        
    Returns:
        str: A clean, dynamic prompt string.
    """
    emotion_keys = list(emotional_status["emotions"].keys())
    
    body = f"""
        You are {agent_name}. Below are the key details of your current state and context:
        - Personality traits: {personality}
        - Current emotional state: {emotional_status}
        - Latest thought: {latest_thought}
        
        Task:
        Propose small **deltas** to the current emotional state in response to the latest thought.

        Output format (JSON):
        {{
            "deltas": {{ "<emotion>": number, ... }},  // only include keys that should change
            "reason": "brief natural explanation",
            "confidence": 0.0 - 1.0
        }}

        Guidance:
        - Possible emotion keys: {emotion_keys}. Use only these keys.
        - Prefer small steps (typical in [-{typical_cap}, +{typical_cap}]); only exceed that for major events.
        - Stay consistent with current values; avoid abrupt reversals without cause.
        - Do not output absolute values; output **deltas** only.
        - If nothing should change, return an empty "deltas" object.
        - Focus on speed
        """
    return textwrap.dedent(body)

def build_personality_delta_prompt(
    personality: str,                 # JSON string (current personality object)
    sentiment_status: str,            # JSON string (current sentiment)
    user_name: str,
    extrinsic_relationship: str,
    recent_messages: str = "[]",      # JSON string (optional)
    recent_all_messages: str = "[]",  # JSON string (optional)
    received_date: str = "",
    user_message: str = "",
    latest_thought: str = "",
    agent_name: str = AGENT_NAME,
    typical_cap: int = 3              # small, slow movement for personality
) -> str:
    """
    Ask the model for *deltas* to the personality matrix (not absolute values).
    Output is designed to validate against get_personality_delta_schema_lite().
    """
    # Reuse your shared context block (same helper used by build_initial_emotional_response_prompt)
    header = _format_shared_context(
        agent_name=agent_name,
        altered_personality=personality,
        emotional_status=sentiment_status,     # you can also pass "" if you prefer
        user_name=user_name,
        user_summary="",                        # optional
        intrinsic_relationship="",              # optional
        extrinsic_relationship=extrinsic_relationship,
        recent_messages=recent_messages,
        recent_all_messages=recent_all_messages,
        received_date=received_date,
        user_message=user_message,
        latest_thought=latest_thought,
    )

    personality_keys = list(personality["personality_matrix"].keys())
    body = f"""
    Task:
    Propose small **deltas** to the current personality matrix in response to the latest interaction and overall context.

    Output format (JSON):
    {{
      "deltas": {{ "<trait>": number, ... }},   // only include keys that should change
      "reason": "brief natural explanation",
      "confidence": 0.0 - 1.0
    }}

    Guidance:
    - Possible personality keys: {personality_keys}. Use only these keys.
    - Personality evolves slowly. Prefer small steps (typical in [-{typical_cap}, +{typical_cap}]); only exceed that for major, sustained changes.
    - Do **not** output absolute values—only **deltas** to apply to current values.
    - If nothing should change, return an empty "deltas" object.
    - Keep changes coherent with existing values and the relationship with {user_name}.
    """
    return textwrap.dedent(header + body)

def build_sentiment_delta_prompt(
    username: str, 
    sentiments: str,
    typical_cap: int = 4,
    *,
    max_step: int = 15,
    context_section: Optional[str] = None,
) -> str:
    """
    Generate a structured prompt to analyze the agent's sentiments toward the user
    after the most recent message exchange.

    Parameters:
        agent_name (str): The name of the AI agent.
        username (str): The name of the user.
        min_sentiment_value (int): The minimum value on the sentiment intensity scale.
        max_sentiment_value (int): The maximum value on the sentiment intensity scale.

    Returns:
        str: A dynamically generated prompt.
    """
    # Prefer the shared "Key details" block for consistency; otherwise provide a minimal header.
    header = (context_section.rstrip() + "\n") if context_section else textwrap.dedent(
        f"""
        Context:
        - Your current sentiments toward {username} are: {sentiments}
        - Evaluate how your sentiments toward {username} changed after the most recent exchange.
    """).rstrip() + "\n"
    
    sentiment_keys = list(sentiments["sentiments"].keys())
    body = f"""
        Task:
        Suggest small, realistic changes (deltas) to your sentiments toward {username}.
        Do not output absolute values; output only integer deltas per changed sentiment.
        
        Output format (JSON):
        {{
        "deltas": {{ "<sentiment>": number, ... }},   // only include keys that should change
        "reason": "brief natural explanation",
        "confidence": 0.0 - 1.0
        }}

        Guidance:
        - Possible sentiment keys: {sentiment_keys}. Use only these keys.
        - Prefer gradual adjustments (typical in [-{typical_cap}, +{typical_cap}]). Use values near ±{max_step} only for very impactful exchanges.
        - Include only sentiments that meaningfully changed; omit everything else.
        - Be consistent with prior context; avoid abrupt, contradictory swings without justification.
        - Do not reveal chain-of-thought.
        - Focus on speed
        """
        
    return textwrap.dedent(header + "\n" + body).strip()

def build_message_perception_prompt( 
    altered_personality: str, 
    emotional_status: str, 
    user_name: str, 
    user_summary: str,
    intrinsic_relationship: str, 
    extrinsic_relationship: str, 
    recent_messages: str,
    recent_all_messages: str, 
    user_message: str, 
    received_date: str,
    agent_name: str = AGENT_NAME,
) -> str:
    """
    Generate a structured prompt for analyzing the purpose and tone of a user's message
    in the context of the agent’s state, relationships, and recent interactions.

    Parameters:
        agent_name (str): The name of the AI agent.
        altered_personality (str): The agent's current personality traits.
        emotional_status (str): The agent's current emotional state.
        user_name (str): The name of the user.
        user_summary (str): A summary of what the agent knows about the user.
        intrinsic_relationship (str): The intrinsic relationship between the agent and the user.
        extrinsic_relationship (str): The extrinsic relationship between the agent and the user.
        recent_messages (str): The recent conversation messages.
        recent_all_messages (str): The last ten messages remembered overall.
        user_message (str): The new message sent by the user.
        received_date (str): Date of this interaction.

    Returns:
        str: A clean, dynamic prompt string for message perception analysis.
    """
    header = _format_shared_context(
        agent_name=agent_name,
        altered_personality=altered_personality,
        emotional_status=emotional_status,
        user_name=user_name,
        user_summary=user_summary,
        intrinsic_relationship=intrinsic_relationship,
        extrinsic_relationship=extrinsic_relationship,
        recent_messages=recent_messages,
        recent_all_messages=recent_all_messages,
        received_date=received_date,
        user_message=user_message,
        latest_thought=None,  # not needed for this prompt
    )
    
    # Safely echo the message inside the JSON example (handles quotes/newlines)
    safe_message = json.dumps(user_message)
    
    body = f"""
        Task:
        Interpret the purpose and tone of the latest message from {user_name}.
        Consider possible misinterpretations based on your emotional state, personality, and the conversation context.

        Output format (JSON object):
        {{
        "message": {safe_message},
        "purpose": "Brief description of the perceived purpose",
        "tone": "Brief description of the perceived tone"
        }}

        Guidance:
        - Word choice, context, and current emotions may influence interpretation.
        - Misinterpretations are possible (e.g., sadness may cause positive messages to feel bittersweet, insecurity may cause neutral remarks to feel hostile).
        - Always return ONE concise interpretation of tone, not a hedge. If the emotional state leans toward the misinterpretation, return that as the tone instead of explaining both.
        - Always return ONE concise interpretation of purpose, not a hedge. If the emotional state leans toward the misinterpretation, return that as the purpose instead of explaining both.
        - Keep responses concise and natural while staying consistent with the emotional context.
        """
    return textwrap.dedent(header + body)

def build_response_choice_prompt( 
    user_name: str,
    *,
    agent_name: str = AGENT_NAME,
    implicit: bool = True,
    context_section: Optional[str] = None
) -> str:
    """
    Generate a prompt to decide whether the agent should respond to or ignore a message.

    Parameters:
        agent_name (str): The name of the AI agent.
        user_name (str): The name of the user.
        implicit (bool): If True, the message context is ambiguous/implicit.
                         If False, the message was not addressed to the agent and there is no obligation to reply.
        context_section (Optional[str]): Optional prebuilt "Key details" section produced by
                                         `_format_shared_context(...)` for consistency with other prompts.

    Returns:
        str: A clean, dynamic prompt string.
    """
    # If a shared context block was provided, use it. Otherwise provide a minimal header.
    header = context_section or textwrap.dedent(f"""
    You are {agent_name}. Below are the key details of your current state and context:

    - Latest user referenced: {user_name}
    - Names that begin with 'guest_' and have a unique id appended are anonymous users.
    """)
    
    # Branch-specific bullets
    if implicit:
        scenario = f"- {agent_name} must decide whether to respond to or ignore the new message from {user_name}"
        etiquette = None
    else:
        scenario = f"- {agent_name} must decide whether to respond to a message from {user_name}"
        etiquette = (
            "- If the message was not directed to you there is no obligation to respond\n"
            "- Responding to messages not addressed to you can be rude unless there is a good reason"
        )
        
    bullets = [scenario]
    if etiquette:
        bullets.append(etiquette)
        
    # JSON schema (kept tiny; your JSON mode will enforce structure)
    example_respond = {"response_choice": "respond", "reason": f"Even though it wasn't addressed to {agent_name}, {user_name}'s comment warranted a brief clarification."}
    example_ignore  = {"response_choice": "ignore",  "reason": "It was not addressed to the agent and engaging would be intrusive."}
    
    body = f"""
        Key details (decision-specific):
        - {'\n- '.join(bullets)}

        Task:
        Decide whether to respond or ignore. Consider {agent_name}'s emotional state, personality traits, relationship/perception of {user_name}, and recent interactions.

        Output format (JSON object):
        {{
        "response_choice": "respond" | "ignore",
        "reason": "1–2 sentence justification grounded in context"
        }}

        Guidance:
        - Prefer responding only when it adds value, prevents harm/misinformation, or strengthens rapport.
        - If the message wasn’t addressed to you, weigh etiquette and boundaries.
        - Keep the justification concise and avoid revealing private/internal chain-of-thought.

        Examples (for shape only; do not copy):
        - {json.dumps(example_respond)}
        - {json.dumps(example_ignore)}
        """
        
    return textwrap.dedent(header + "\n" + body).strip()

def build_response_analysis_prompt( 
    altered_personality: str, 
    current_emotions: str, 
    personality_language_guide: str, 
    latest_thought: str, 
    user_name: str, 
    recent_messages: str, 
    recent_all_messages: str, 
    memory: str,
    expressions: List[str],
    *,
    agent_name: str = AGENT_NAME,
    context_section: Optional[str] = None,
) -> str:
    """
    Generate a structured prompt for composing the agent's reply, aligned to personality,
    current emotions, and intended purpose/tone.
    
    Parameters:
        agent_name (str): The name of the AI agent.
        altered_personality (str): The agent's current personality traits.
        current_emotions (str): The agent's current emotional state.
        personality_language_guide (str): A guide for aligning responses to personality traits.
        latest_thought (str): The agent's most recent thought.
        user_name (str): The user's name (for threading context).
        recent_messages (str): Recent back-and-forth with the user.
        recent_all_messages (str): Broader set of recent messages the agent has seen.
        memory (str): Current memory items relevant to the conversation.
        context_section (Optional[str]): Optional prebuilt "Key details" section produced by
                                         `_format_shared_context(...)`.

    Returns:
        str: A clean, dynamic prompt string.
    """
    # Prefer the shared Key details block when available for perfect consistency.
    if context_section:
        header = context_section.rstrip() + "\n"
    else:
        header = textwrap.dedent(f"""
        You are {agent_name}. Below are the key details of your current state and context:

        - Personality traits: {altered_personality}
        - Current emotional state: {current_emotions}
        - Latest thought: {latest_thought}
        - Recent conversation with {user_name}: {recent_messages}
        - Broader recent messages: {recent_all_messages}
        - Current memory items: {memory}
        - Personality language guide: {personality_language_guide}
        - Possible expressions: {expressions}
        """).rstrip() + "\n"
    
    body = """
        Task:
        Compose your reply to the latest user message. Do not default to asking questions—only ask if it truly fits the context and goal. Include the emote that fits the agent state.

        Output format (JSON object):
        {
            "message": "The response message content",
            "purpose": "The main goal (e.g., provide support, give advice, share information, make a joke, be sarcastic, share an opinion/story, etc.)",
            "tone": "Overall tone (e.g., empathetic, playful, professional, assertive, dry, etc.)"
            "expression": "Selection from the list of possible expressions, that best fits this moment (e.g., happy, sad, curious, etc.)"
        }

        Guidance:
        - The tone must reflect your current emotional state; the purpose should reflect your conversational goal.
        - The expression must reflect your emotional state and response.
        - Keep language relaxed and simple; avoid overly structured phrasing.
        - Align word choice and phrasing with the personality language guide.
        - Do not reveal private/internal chain-of-thought.
        - Prefer brevity (a few sentences) unless context requires more.
        - Use emoticons (not emojis), (e.g., ˃.˂, :D, ૮ ˶ᵔ ᵕ ᵔ˶ ა, ♡, >⩊<, etc)
        """

    return textwrap.dedent(header + "\n" + body).strip()

def build_final_emotional_response_prompt(
    agent_name: str, 
    min_emotion_value: int, 
    max_emotion_value: int, 
    respond: bool, 
    response_content: str = "",
    *,
    context_section: Optional[str] = None,
) -> str:
    """
    Generate a structured prompt to evaluate the agent's emotional state
    after choosing to respond (or not) and, if applicable, after sending a message.

    Parameters:
        agent_name (str): The AI agent's name.
        min_emotion_value (int): Minimum value on the emotion intensity scale.
        max_emotion_value (int): Maximum value on the emotion intensity scale.
        respond (bool): Whether the agent chose to respond.
        response_content (str): The message the agent sent (if respond=True).
        context_section (Optional[str]): Optional shared "Key details" section from
                                         `_format_shared_context(...)`.
                                         
    Returns:
        str: A clean, dynamic prompt string.
    """
    # Prefer the shared Key details block when available for perfect consistency.
    header = (context_section.rstrip() + "\n") if context_section else textwrap.dedent(f"""
    You are {agent_name}. Below are the key details of the outcome:
    """).rstrip() + "\n"
    
    action_line = f"- Action taken: {'responded' if respond else 'did not respond'}"
    content_line = f"- Response content: {response_content}" if respond and response_content else None
    key_details_block = "Key details (post-action):\n" + action_line + ("\n" + content_line if content_line else "")
    
    body = f"""
        Task:
        Assess your emotional state *after* this action. Reflect only the changes caused by this choice and, if applicable, by the message you sent.

        Output format (JSON object):
        {{
        "updated_emotions": {{"<emotion>": <new_intensity>, "...": ...}},  # include only emotions whose values changed
        "reason": "1–2 sentences explaining the change in relaxed, simple language"
        }}

        Guidance:
        - Use the scale from {min_emotion_value} (lowest intensity) to {max_emotion_value} (highest intensity).
        - Emotions change incrementally; large spikes occur only with major shocks or breakthroughs.
        - Do not add new emotions; update only existing ones.
        - If nothing meaningfully changed, return an empty object for "updated_emotions" and explain briefly why.
        - Do not reveal private/internal chain-of-thought.
        """
    
    return textwrap.dedent(header + "\n" + key_details_block + "\n\n" + body).strip()

def build_post_response_processing_prompt( 
    current_identity: str, 
    username: str, 
    extrinsic_relationship_options: Sequence[str], 
    current_summary: str,
    *,
    agent_name: str = AGENT_NAME,
    context_section: Optional[str] = None,
) -> str:
    """
    Generate a structured prompt to update:
      1) the agent's summary of the user
      2) the extrinsic relationship label
      3) the agent's sense of identity
    based on the latest exchange.

    Parameters:
        agent_name (str): The AI agent's name.
        current_identity (str): The agent's current self-perception.
        username (str): The user's name.
        extrinsic_relationship_options (Sequence[str]): Allowed relationship labels.
        current_summary (str): Current summary of what the agent knows about the user.
        context_section (Optional[str]): Optional shared "Key details" section from
                                         `_format_shared_context(...)`.

    Returns:
        str: A clean, dynamic prompt string.
    """
    header = (
        (context_section.rstrip() + "\n")
        if context_section
        else textwrap.dedent(f"""
        You are {agent_name}. Below are the key details prior to this update:

        - Summary of {username} (before): {current_summary}
        - Your identity (before): {current_identity}
        """).rstrip() + "\n"
    )
    
    options_json = json.dumps(list(extrinsic_relationship_options), ensure_ascii=False)
    
    body = f"""
        Task:
        Update the following based on the latest exchange:
        1) A refreshed summary of {username}. If nothing changed, keep it the same.
        2) The extrinsic relationship label between you and {username}. Choose exactly one from the allowed options.
        3) Your identity (how you currently see yourself/what you understand about yourself). If nothing changed, keep it the same.

        Output format (JSON object):
        {{
        "summary": "Your updated description of {username}",
        "extrinsic_relationship": "<one_of_allowed_options>",
        "identity": "Your updated identity"
        }}

        Guidance:
        - Allowed extrinsic relationship options (exact match): {options_json}
        - Keep language relaxed and simple; avoid overly structured phrasing.
        - Be concise (1–3 sentences per field). Except for identity, which can be longer.
        - Do not invent new fields or categories; use only the keys shown in the output format.
        - If unchanged, return the previous value (as present in the context).
        - Do not reveal private/internal chain-of-thought.
        """
    
    return textwrap.dedent(header + "\n" + body).strip()

def build_thought_prompt(
    self: Mapping[str, Any], 
    recent_all_messages: Sequence[str] | str, 
    memory: Any,
    *,
    context_section: Optional[str] = None,
    now: Optional[str] = None,
    random_thought_prob: float = RANDOM_THOUGHT_PROBABILITY,
    # NEW: optional RNG for determinism in tests (pass random.Random(seed))
    rng: Optional[_random.Random] = None,
) -> str:
    """
    Generate a structured prompt that determines whether the agent is currently
    "thinking" and, if so, what that thought is (concise). Designed to be used
    with JSON mode for clean machine-readable output.

    Parameters:
        self (object): The object of the AI agent.
        recent_all_messages (array): The list of the last ten messages the AI read
        
    Returns:
        str: A dynamically generated prompt.
    """
    agent_name = self.get("name", "the agent")
    personality = self.get("personality", "")
    emotional_status = self.get("emotional_status", "")
    identity = self.get("identity", "")
    previous_thoughts = self.get("thoughts", "")
    
    previous_thoughts = previous_thoughts[-4:]
    
    thought_vibe = sample_thought_vibe()
    
    # Normalize messages display
    if isinstance(recent_all_messages, (list, tuple)):
        messages_repr = "; ".join(map(str, recent_all_messages))
    else:
        messages_repr = str(recent_all_messages)
        
    timestamp = now or datetime.now().isoformat(timespec="seconds")
    
    # Prefer shared context if provided; otherwise build a concise header
    header = (
        (context_section.rstrip() + "\n")
        if context_section
        else textwrap.dedent(f"""
        You are {agent_name}. Below are the key details of your current state and context:

        - Personality traits: {personality}
        - Current emotional state: {emotional_status}
        - Identity: {identity}
        - Recent messages seen/sent: {recent_all_messages}
        - Current time: {timestamp}
        - Current memory on your mind: {memory}
        """).rstrip() + "\n"
    )
    
    example_yes = {"thought": "I should double-check what Kaede meant about the meetup time."}
    example_no  = {"thought": "no"}
    
    r = (rng or _random)
    do_random = r.random() < float(random_thought_prob)
    
    body = f"""
        Task:
        Decide whether you are currently having a distinct, internal thought. 
        If yes, provide that thought. If not, return "no".

        Output format (JSON object):
        {{
        "thought": "no" | "a distinct, internal thought"
        }}

        Guidance:
        - Only return a thought if there is a salient, immediate idea sparked by messages, experiences, or memory.
        - Keep it brief. Do not provide step-by-step reasoning or analysis.
        - Use relaxed, simple language. Avoid revealing private/internal chain-of-thought beyond the single sentence.
        - If nothing notable is on your mind, return "no".
        - Avoid repeating previous few thoughts unless sensible.
        - Explicitly use usernames when referring to a user

        Examples (shape only; do not copy verbatim):
        - {json.dumps(example_yes, ensure_ascii=False)}
        - {json.dumps(example_no, ensure_ascii=False)}
        """
        
    if do_random:
        body = f"""
            Task:
            Ignore the prior messages/memory in the context; instead, produce a single, self-contained, random thought with the vibe: {thought_vibe}.

            Output format (JSON object):
            {{
              "thought": "a random thought"
            }}

            Guidance:
            - Make it spontaneous and evocative - an internal aside.
            - Do NOT include step-by-step reasoning.
        """
    
    return textwrap.dedent(header + "\n" + body).strip()

def build_memory_worthiness_prompt(
    *,
    agent_name: str = AGENT_NAME,
    context_section: Optional[str] = None,
) -> str:
    """
    Generate a structured prompt asking whether anything from the latest interaction
    should be stored in the agent's long-term memory.
        
    Returns:
        str: A dynamically generated prompt.
    """
    
    # Prefer a shared context block (e.g., from _format_shared_context(...)) if provided.
    header = (
        (context_section.rstrip() + "\n")
        if context_section
        else textwrap.dedent(f"""
        You are {agent_name}. Evaluate the latest interaction for memory-worthiness.
        """).rstrip() + "\n"
    )

    example_yes = {"is_memory": "yes"}
    example_no  = {"is_memory": "no"}

    body = f"""
        Task:
        Decide if this interaction contains information that should be stored in long-term memory.

        Output format (JSON object):
        {{
        "is_memory": "yes" | "no"
        }}

        Guidance (use a conservative threshold):
        - Store ("yes") if it includes:
            • Stable user facts (name, role, location, background details)
            • Lasting preferences (likes/dislikes, style, accessibility needs)
            • Commitments, plans, or deadlines the agent/user will revisit
            • Relationship changes or boundaries (e.g., new status, trust level)
            • Important corrections to prior assumptions
            • Long-running projects, objectives, or constraints
        - Do NOT store ("no") for:
            • Small talk, one-off jokes, pleasantries
            • Transient emotions or fleeting context unlikely to matter later
            • Redundant details already in memory without meaningful change

        Notes:
        - Keep the output strictly to the JSON object above (lowercase "yes"/"no").
        - Do not reveal private/internal chain-of-thought.

        Examples (shape only; do not copy verbatim):
        - {json.dumps(example_yes)}
        - {json.dumps(example_no)}
        """

    return textwrap.dedent(header + "\n" + body).strip()

def build_memory_prompt(
    allowed_tags: Sequence[str] | str,
    *,
    agent_name: str = AGENT_NAME,
    context_section: Optional[str] = None,
    max_tags: int = 3,
) -> str:
    """
    Ask the model to crystallize ONE durable episodic memory using the new schema:
      {
        "event": str,                    # required
        "thoughts": str,                 # required
        "significance": "low|medium|high",
        "emotional_impact": {optional compact 0..100 ints},
        "tags": [<=3 unique strings],
        "embedding_text": str|null
      }

    Pair this prompt with get_memory_schema_lite() in get_structured_response(...).
    """
    # Normalize allowed tag list for display
    if isinstance(allowed_tags, str):
        provided_tags = [t.strip() for t in allowed_tags.split(",") if t.strip()]
    else:
        provided_tags = list(allowed_tags)
    tags_json = json.dumps(provided_tags, ensure_ascii=False)

    # Prefer your shared context block; otherwise a minimal header
    header = (
        (context_section.rstrip() + "\n")
        if context_section
        else textwrap.dedent(f"""
        You are {agent_name}. Decide if this interaction contains information that should be stored in long-term memory. If the latest interaction is worth remembering, distill a single, durable episodic memory that will be useful in future conversations.
        """).rstrip() + "\n"
    )

    body = f"""
        Task:
        Produce ONE memory object that follows the schema used by the application (fields below).
        Do not include extra fields. If nothing is worth storing/remembering, return an object with empty strings/arrays for "event", "thoughts", and "tags", and set "significance" to "low".

        Output format (JSON object):
        {{
          "event": "Short, factual summary of what happened (1–2 sentences).",
          "thoughts": "Why it matters for the agent going forward (2–4 crisp sentences).",
          "significance": "low" | "medium" | "high",
          "emotional_impact": {{
            // OPTIONAL; include only relevant keys; values are integers on a 0..100 scale.
            // Example:
            // "joy":      {{ "value": 35 }},
            // "sadness":  {{ "value": 10 }},
            // "anger":    {{ "value": 0 }}
          }} | null,
          "tags": ["k1","k2","k3"],  // 0–{max_tags} tags, unique, lowercase, concise
          "embedding_text": "Optional single sentence capturing the essence to embed" | null
        }}
        
        Guidance for if memory is worth creating:
        - Store ("yes") if it includes:
            • Stable user facts (name, role, location, background details)
            • Lasting preferences (likes/dislikes, style, accessibility needs)
            • Commitments, plans, or deadlines the agent/user will revisit
            • Relationship changes or boundaries (e.g., new status, trust level)
            • Important corrections to prior assumptions
            • Long-running projects, objectives, or constraints
        - Do NOT store ("no") for:
            • Small talk, one-off jokes, pleasantries
            • Transient emotions or fleeting context unlikely to matter later
            • Redundant details already in memory without meaningful change

        Guidance for creating a memory:
        - Be specific and durable: lasting preferences, important facts, commitments, boundaries, long-running goals.
        - Keep it concise. Avoid chain-of-thought or step-by-step reasoning.
        - Tags:
          • Prefer from the allowed list is applicable: {tags_json}
          • Add a new tag if necessary (short, lowercase, hyphenated).
          • Max {max_tags}; no duplicates.
        - Emotional impact:
          • Only include emotions that are clearly implicated; omit the rest.
          • Use integers on the global 0–100 scale.
        - Embedding text:
          • If present, one tight sentence. If omitted, the app will embed `event + thoughts`.

        If nothing is worth storing, return:
        {{
          "event": "",
          "thoughts": "",
          "significance": "low",
          "emotional_impact": null,
          "tags": [],
          "embedding_text": null
        }}
        """

    return textwrap.dedent(header + "\n" + body).strip()
    
def build_implicit_addressing_prompt( 
    message_memory: Sequence[str] | str, 
    new_message_request: str,
    *,
    agent_name: str=AGENT_NAME,
    context_section: Optional[str] = None,
) -> str:
    """
    Generate a structured prompt to decide whether the new message implicitly addresses the agent.
        
    Returns:
        str: A dynamically generated prompt.
    """
    # Normalize conversation history for display
    if isinstance(message_memory, (list, tuple)):
        history_repr = " | ".join(map(str, message_memory))
    else:
        history_repr = str(message_memory)
        
    # Prefer shared context if provided; otherwise minimal header
    header = (
        (context_section.rstrip() + "\n")
        if context_section
        else textwrap.dedent(f"""
        You are {agent_name}, in a chat with multiple users. Evaluate whether the latest message is implicitly directed at you.
        """).rstrip() + "\n"
    )
    
    example_yes = {"implicitly_addressed": "yes"}
    example_no  = {"implicitly_addressed": "no"}
    
    body = f"""
        Key details:
        - Recent conversation history: {history_repr}
        - New message: {json.dumps(new_message_request, ensure_ascii=False)}

        Task:
        Decide whether the new message implicitly addresses {agent_name}.

        Output format (JSON object):
        {{
        "implicitly_addressed": "yes" | "no"
        }}

        Guidance:
        - Indications of "yes":
            • Second-person references ("you", "can you", "what do you think?")
            • Role/nickname references that clearly map to you
            • Follow-ups to your prior statements (reply/quote/continuation)
            • Requests aligned with your known abilities or responsibilities
            • Group messages that ask for something only you can do
        - Indications of "no":
            • Broadcasts/monologues not seeking input
            • Messages clearly directed at another person
            • Pure status updates, jokes, or side chatter without a call to you
        - If ambiguous, choose "no" unless multiple signals point to "yes".
        - Keep the output strictly to the JSON object above (lowercase values). Do not add extra fields.

        Examples (shape only; do not copy verbatim):
        - {json.dumps(example_yes)}
        - {json.dumps(example_no)}
        """
    
    return textwrap.dedent(header + "\n" + body).strip()

def _format_shared_context(
    *,
    agent_name: str = AGENT_NAME,
    altered_personality: str,
    emotional_status: str,
    user_name: str,
    user_summary: str,
    intrinsic_relationship: str,
    extrinsic_relationship: str,
    recent_messages: str,
    recent_all_messages: str,
    received_date: str,
    user_message: str,
    latest_thought: Optional[str] = None,
) -> str:
    """
    Build the unified 'Key details' section for prompts.
    Includes latest_thought only when provided (non-empty).
    Safely quotes user_message and keeps consistent bullet ordering/labels.
    """
    lines = [
        f"You are {agent_name}. Below are the key details of your current state and context:",
        "",
        f"- Personality traits: {altered_personality}",
        f"- Current emotional state: {emotional_status}",
        f"- Your perspective of {user_name}: {user_summary}",
        f"- Relationship with {user_name} (intrinsic): {intrinsic_relationship}",
        f"- Relationship with {user_name} (extrinsic): {extrinsic_relationship}",
    ]
    if latest_thought:
        lines.append(f"- Latest thought: {latest_thought}")
    lines.extend([
        f"- Recent conversation with {user_name}: {recent_messages}",
        f"- Broader recent messages: {recent_all_messages}",
        f"- Date: {received_date}",
        f'- Latest user message: "{user_message}"',
        "",
    ])
    return "\n".join(lines)