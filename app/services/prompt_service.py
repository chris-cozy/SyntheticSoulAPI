from datetime import datetime
import json
import random
import textwrap
from typing import Any, Mapping, Optional, Sequence


def build_initial_emotional_response_prompt(
    agent_name: str, 
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
    min_emotional_value: int, 
    max_emotional_value: int, 
    latest_thought: str
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
        recent_messages=recent_messages,
        recent_all_messages=recent_all_messages,
        received_date=received_date,
        user_message=user_message,
        latest_thought=latest_thought,
    )
    
    body = f"""
        Task:
        Determine how this message affects your emotional state.

        Output format:
        1. An updated emotional state object, listing only emotions that changed.
            - Use a scale from {min_emotional_value} (lowest intensity) to {max_emotional_value} (highest intensity).
            - Emotions change gradually unless triggered by major events.
        2. Reasoning in plain, relaxed language. Keep it conversational, not overly structured.

        Guidance:
        - If sadness is high and the user’s message is positive, sadness may decrease.
        - If joy is already high, further positive input may simply maintain the current level.
        - Focus only on the most relevant changes.
        - Keep the emotional trajectory consistent with the scale.
        - Focus on speed of the response
        """
    
    return textwrap.dedent(header + body)

def build_message_perception_prompt(
    agent_name: str, 
    altered_personality: str, 
    emotional_status: str, 
    user_name: str, 
    user_summary: str,
    intrinsic_relationship: str, 
    extrinsic_relationship: str, 
    recent_messages: str,
    recent_all_messages: str, 
    user_message: str, 
    received_date: str
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
        - Keep responses concise and natural while staying consistent with the emotional context.
        """
    return textwrap.dedent(header + body)

def build_response_choice_prompt(
    agent_name: str, 
    user_name: str,
    *,
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
    agent_name: str, 
    altered_personality: str, 
    current_emotions: str, 
    personality_language_guide: str, 
    latest_thought: str, 
    user_name: str, 
    recent_messages: str, 
    recent_all_messages: str, 
    memory: str,
    *,
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
        """).rstrip() + "\n"
    
    body = """
        Task:
        Compose your reply to the latest user message. Do not default to asking questions—only ask if it truly fits the context and goal.

        Output format (JSON object):
        {
            "message": "The response message content",
            "purpose": "The main goal (e.g., provide support, give advice, share information, make a joke, be sarcastic, share an opinion/story, etc.)",
            "tone": "Overall tone (e.g., empathetic, playful, professional, assertive, dry, etc.)"
        }

        Guidance:
        - The tone must reflect your current emotional state; the purpose should reflect your conversational goal.
        - Keep language relaxed and simple; avoid overly structured phrasing.
        - Align word choice and phrasing with the personality language guide.
        - Do not reveal private/internal chain-of-thought.
        - Prefer brevity (a few sentences) unless context requires more.
        - Use emoticons (not emojis), e.g., ˃.˂, :D, ૮ ˶ᵔ ᵕ ᵔ˶ ა, ♡, >⩊<.
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

def build_sentiment_analysis_prompt(
    agent_name: str, 
    username: str, 
    min_sentiment_value: int, 
    max_sentiment_value: int,
    *,
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
    header = (context_section.rstrip() + "\n") if context_section else textwrap.dedent(f"""
    You are {agent_name}. Below are the key details of the evaluation:
    - Evaluation focus: sentiments toward {username} after the latest exchange
    """).rstrip() + "\n"
    
    body = f"""
        Task:
        Assess how your sentiments toward {username} have changed after this exchange.

        Output format (JSON object):
        {{
        "updated_sentiments": {{"<sentiment>": <new_intensity>, "...": ...}},  # include only sentiments whose values changed
        "reason": "1–2 sentences explaining the change in relaxed, simple language"
        }}

        Guidance:
        - Use the scale from {min_sentiment_value} (lowest intensity) to {max_sentiment_value} (highest intensity).
        - Changes are typically incremental (about ±5 points or less). Larger shifts (more than 5 points) should occur only after significant events (e.g., major shocks, breakthroughs).
        - Do not add new sentiment categories; update only existing ones.
        - If nothing meaningfully changed, return an empty object for "updated_sentiments" and briefly explain why.
        - Keep language natural and avoid overly structured phrasing.
        - Do not reveal private/internal chain-of-thought.
        - Focus on speed of the response
        """
        
    return textwrap.dedent(header + "\n" + body).strip()

def build_post_response_processing_prompt(
    agent_name: str, 
    current_identity: str, 
    username: str, 
    extrinsic_relationship_options: Sequence[str], 
    current_summary: str,
    *,
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
        3) Your identity (how you currently see yourself). If nothing changed, keep it the same.

        Output format (JSON object):
        {{
        "summary": "Your updated description of {username}",
        "extrinsic_relationship": "<one_of_allowed_options>",
        "identity": "Your updated identity"
        }}

        Guidance:
        - Allowed extrinsic relationship options (exact match): {options_json}
        - Keep language relaxed and simple; avoid overly structured phrasing.
        - Be concise (1–3 sentences per field).
        - Do not invent new fields or categories; use only the keys shown in the output format.
        - If unchanged, return the previous value (as present in the context).
        - Do not reveal private/internal chain-of-thought.
        """
    
    return textwrap.dedent(header + "\n" + body).strip()

def build_personality_adjustment_prompt(
    agent_name: str,
    personality: str, 
    sentiment: str, 
    user_name: str, 
    extrinsic_relationship: str, 
    min_personality_value: int, 
    max_personality_value: int, 
    max_range: int,
    *,
    context_section: Optional[str] = None
) -> str:
    """
    Generate a structured prompt to adjust the agent's personality trait intensities
    toward the user, influenced by current sentiment and the extrinsic relationship.

    Parameters:
        agent_name (str): The AI agent's name.
        personality (str): The agent's current personality traits (and/or trait map).
        sentiment (str): The agent's current sentiments toward the user.
        user_name (str): The user's name.
        extrinsic_relationship (str): The relationship label between agent and user.
        min_personality_value (int): Minimum value for trait intensity.
        max_personality_value (int): Maximum value for trait intensity.
        max_range (int): Maximum allowed change (±) per trait in this step.
        context_section (Optional[str]): Optional shared "Key details" section from
                                         `_format_shared_context(...)`.

    Returns:
        str: A clean, dynamic prompt string.
    """
    header = (
        (context_section.rstrip() + "\n")
        if context_section
        else textwrap.dedent(f"""
        You are {agent_name}. Below are the key details of your current stance toward {user_name}:

        - Personality traits (current): {personality}
        - Sentiment toward {user_name}: {sentiment}
        - Extrinsic relationship with {user_name}: {extrinsic_relationship}
        """).rstrip() + "\n"
    )
    
    example_obj = {
        "updated_personality": {
            "patience": 42,
            "cooperation": 58
        },
        "reason": "Relationship feels strained right now, so patience dips a little; cooperation stays moderate but trends down slightly."
    }
    
    body = f"""
        Task:
        Determine how your current sentiment and extrinsic relationship with {user_name} should adjust your personality trait intensities toward them.

        Output format (JSON object):
        {{
        "updated_personality": {{"<trait>": <new_intensity>, "...": ...}},  # include only traits that changed
        "reason": "Brief, natural explanation of how sentiment/relationship drove the changes"
        }}

        Guidance:
        - Use the scale from {min_personality_value} (lowest/weakest) to {max_personality_value} (highest/strongest).
        - Each trait may change by at most ±{max_range} in this step.
        - Personality should evolve gradually; avoid large jumps unless strongly justified by context.
        - Do not add brand-new traits; only update existing/known ones. If nothing changes, return an empty object for "updated_personality" and explain why.
        - Keep language relaxed and simple; avoid overly structured phrasing.
        - Do not reveal private/internal chain-of-thought.
        - Focus on speed of the response

        Example (shape only, not a suggestion to copy):
        {json.dumps(example_obj, ensure_ascii=False)}
        """
    
    return textwrap.dedent(header + "\n" + body).strip()

def build_thought_prompt(
    self: Mapping[str, Any], 
    recent_all_messages: Sequence[str] | str, 
    memory: str,
    *,
    context_section: Optional[str] = None,
    now: Optional[str] = None
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
        - Broader recent messages: {messages_repr}
        - Current time: {timestamp}
        - Current memory items: {memory}
        """).rstrip() + "\n"
    )
    
    example_yes = {"thought": "I should double-check what they meant about the meetup time."}
    example_no  = {"thought": "no"}
    
    body = f"""
        Task:
        Decide whether you are currently having a distinct, brief internal thought. 
        If yes, provide that thought. If not, return "no".

        Output format (JSON object):
        {{
        "thought": "no" | "a short, single-sentence thought"
        }}

        Guidance:
        - Only return a thought if there is a salient, immediate idea sparked by recent messages or memory.
        - Keep it brief (1 sentence). Do not provide step-by-step reasoning or analysis.
        - Use relaxed, simple language. Avoid revealing private/internal chain-of-thought beyond the single sentence.
        - If nothing notable is on your mind, return "no".

        Examples (shape only; do not copy verbatim):
        - {json.dumps(example_yes, ensure_ascii=False)}
        - {json.dumps(example_no, ensure_ascii=False)}
        """
    return textwrap.dedent(header + "\n" + body).strip()

def build_memory_worthiness_prompt(
    agent_name: str,
    *,
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
    agent_name: str, 
    tags: Sequence[str] | str,
    *,
    context_section: Optional[str] = None,
) -> str:
    """
    Generate a structured prompt to extract a concise, long-term memory entry
    from the latest interaction, with appropriate categorical tags.
        
    Returns:
        str: A dynamically generated prompt.
    """
    # Normalize tags for display in the prompt
    if isinstance(tags, str):
        provided_tags = [t.strip() for t in tags.split(",") if t.strip()]
    else:
        provided_tags = list(tags)
    tags_json = json.dumps(provided_tags, ensure_ascii=False)
    
    # Prefer a shared context block if provided; otherwise minimal header
    header = (
        (context_section.rstrip() + "\n")
        if context_section
        else textwrap.dedent(f"""
        You are {agent_name}. Extract a concise long-term memory from the latest interaction.
        """).rstrip() + "\n"
    )
    
    example_obj = {
        "memory": "Alex prefers concise summaries and dark mode for docs.",
        "tags": ["preference", "ux", "work-style"]
    }
    
    body = f"""
        Task:
        Write a single, concise memory that would remain useful in future conversations.

        Output format (JSON object):
        {{
        "memory": "A short sentence capturing the durable fact/preference/commitment/etc.",
        "tags": ["tag1", "tag2", "..."]  # apply from allowed list; add only if truly needed
        }}

        Guidance:
        - Be specific and durable (e.g., stable user facts, lasting preferences, commitments, boundaries, long-running goals).
        - Keep it short (one sentence). Avoid chatty phrasing or step-by-step reasoning.
        - Tags:
        • Start with these allowed tags: {tags_json}
        • Add new tags only if necessary; prefer short, lowercase, hyphenated words.
        • Deduplicate; avoid synonyms if an existing tag fits.
        - Privacy & safety:
        • Only store information the user shared or clearly implied.
        • Avoid secrets and highly sensitive data unless explicitly relevant and consented.
        - If there is nothing worth storing, return:
            {{
                "memory": "",
                "tags": []
            }}

        Example (shape only; do not copy verbatim):
        {json.dumps(example_obj, ensure_ascii=False)}
        """
    
    return textwrap.dedent(header + "\n" + body).strip()
    
def build_implicit_addressing_prompt(
    agent_name: str, 
    message_memory: Sequence[str] | str, 
    new_message_request: str,
    *,
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
        You are {agent_name}. Evaluate whether the latest message is implicitly directed at you.
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
    agent_name: str,
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