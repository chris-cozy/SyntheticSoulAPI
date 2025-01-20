

from datetime import datetime


def generate_initial_emotional_response_prompt(agent_name, altered_personality, emotional_status, user_name, user_summary, 
                    intrinsic_relationship, extrinsic_relationship, recent_messages, 
                    recent_all_messages, received_date, user_message, min_emotional_value, 
                    max_emotional_value, latest_thought):
    """
    Generates a dynamic prompt based on the input parameters for the interaction between
    the agent and the user.

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
        str: The dynamically generated prompt.
    """
    # Section: Context
    prompt = f"{agent_name}'s personality traits are: {altered_personality}. " \
             f"{agent_name}'s emotional state is: {emotional_status}.\n\n"
    
    # Section: User Information
    prompt += f"This is {agent_name}'s perspective of {user_name}: {user_summary}.\n"
    
    if intrinsic_relationship == "creator and master":
        prompt += f"{user_name} programmed {agent_name}, creating them. Their extrinsic relationship is: {extrinsic_relationship}\n"
    else:
        prompt += f"{agent_name} has no intrinsic relationship with {user_name}, " \
                  f"but their extrinsic relationship is: {extrinsic_relationship}.\n\n"
                  
    prompt += f"This is {agent_name}'s latest thought: {latest_thought}.\n"
    
    # Section: Conversation History
    if recent_messages:
        prompt += f"This is the recent conversation between {agent_name} and {user_name}: {recent_messages}.\n"
    else:
        prompt += f"This is the first conversation between {agent_name} and {user_name}.\n"
    
    prompt += f"Here are the last ten remembered messages overall: {recent_all_messages}.\n\n"
    
    # Section: Current Interaction
    prompt += f"As of {received_date}, {user_name} sent this message to {agent_name}: {user_message}.\n\n"
    
    # Task Instructions
    prompt += f"How would this message alter {agent_name}'s emotional state? Keep in mind that emotions typically change incrementally and only experience large spikes in response to significant events (e.g., major shocks, breakthroughs). Use this principle to ensure gradual and realistic emotional changes. Provide:\n" \
              f"1. An updated emotional state object (include only emotions whose values have changed).\n" \
              f"2. The reasoning behind these changes. Keep this brief, one or two sentences max.\n\n" \
              f"Use the scale {min_emotional_value} (lowest intensity) to {max_emotional_value} (highest intensity). " \
              f"Do not add new emotions."
    
    return prompt


def generate_message_perception_prompt(agent_name, altered_personality, emotional_status, user_name, user_summary,
                                         intrinsic_relationship, extrinsic_relationship, recent_messages,
                                         recent_all_messages, user_message):
    """
    Generates a prompt to analyze the purpose and tone of a user's message within a dynamic conversation context.

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

    Returns:
        str: A dynamically generated prompt to analyze the user's message.
    """
    # Introduction of agent's personality and state
    prompt = (
        f"This is {agent_name}'s personality: {altered_personality}. "
        f"This is their current emotional state: {emotional_status}. "
        f"This is their perception of {user_name}: {user_summary}. "
    )
    
    # Relationship information
    if intrinsic_relationship == "creator and master":
        prompt += f"{user_name} programmed {agent_name}, creating them."
    else:
        prompt += f"There is no intrinsic relationship between {agent_name} and {user_name}. "
    
    prompt += f"{agent_name} has an extrinsic relationship with {user_name} of {extrinsic_relationship}. "
    
    # Conversation history
    if recent_messages:
        prompt += (
            f"This is what {agent_name} remembers of the conversation between them and {user_name}: {recent_messages}. "
        )
    else:
        prompt += f"This is {agent_name}'s and {user_name}'s first time talking. "
    
    prompt += f"These are the most recent ten messages {agent_name} remembers in general: {recent_all_messages}. "
    
    # Purpose and tone analysis
    prompt += (
        f"How would {agent_name} interpret the purpose and tone of {user_name}'s new message: {user_message}? Misinterpretations are allowed."
        f"Provide the response in a JSON object with the following properties: "
        f"{{\"message\": \"{user_message}\", \"purpose\": \"Purpose of the message\", \"tone\": \"Tone of the message\"}}."
    )
    
    return prompt


def generate_response_choice_prompt(agent_name, user_name):
    """
    Generates a prompt to determine whether the AI agent will respond to or ignore a user's message,
    based on the agent's personality, current emotional state, and thoughts on the user.

    Parameters:
        agent_name (str): The name of the AI agent.
        user_name (str): The name of the user.

    Returns:
        str: A dynamically generated prompt.
    """
    prompt = (
        f"{agent_name} can choose whether to respond to or not respond to this message. "
        f"Based on their personality, emotional state, and perception of {user_name}, "
        f"what choice will they make? Provide either 'respond' or 'ignore', and the reason for the choice (Keep this brief, one or two sentences max.), "
        f"in a JSON object with the properties response_choice and reason."
    )
    return prompt


def generate_response_analysis_prompt(agent_name, altered_personality, current_emotions, personality_language_guide, latest_thought):
    """
    Generates a prompt to analyze how the AI agent should respond, with a focus on personality traits,
    emotional status, and intended communication purpose and tone.

    Parameters:
        agent_name (str): The name of the AI agent.
        altered_personality (str): The agent's current personality traits.
        current_emotions (str): The agent's current emotional state.
        personality_language_guide (str): A guide for aligning responses to personality traits.

    Returns:
        str: A dynamically generated prompt.
    """
    prompt = (
        f"The way {agent_name} communicates reflects their personality traits: ({altered_personality}), "
        f"and current emotional status: ({current_emotions}). "
        f"Their latest thought is: {latest_thought}."
        f"How would {agent_name} respond, using what intended purpose and tone? "
        f"Here is a personality language guide for reference: ({personality_language_guide}). "
        f"Provide the response, intended purpose, and intended tone in a JSON object with the properties "
        f"message, purpose, and tone. Do not always ask questions, as that is unrealistic. Act as {agent_name}."
    )
    return prompt


def generate_final_emotional_response_prompt(agent_name, min_emotion_value, max_emotion_value, respond, response_content = ""):
    """
    Generates a prompt to analyze the AI agent's emotional state after sending a response.

    Parameters:
        agent_name (str): The name of the AI agent.
        response_content (str): The message the agent sent.
        min_emotion_value (int): The minimum value on the emotion intensity scale.
        max_emotion_value (int): The maximum value on the emotion intensity scale.

    Returns:
        str: A dynamically generated prompt.
    """
    if (respond):
        prompt = (
        f"{agent_name} chose to respond with this message: ({response_content}). "
        f"What is their emotional state after sending that response? Keep in mind that emotions typically change incrementally and only experience large spikes in response to significant events (e.g., major shocks, breakthroughs). Use this principle to ensure gradual and realistic emotional changes. Provide:\n" \
              f"1. An updated emotional state object (include only emotions whose values have changed).\n" \
              f"2. The reasoning behind these changes. Keep this brief, one or two sentences max.\n\n" \
              f"Use the scale {min_emotion_value} (lowest intensity) to {max_emotion_value} (highest intensity). " \
              f"Do not add new emotions."
        )
        return prompt
    else:
        prompt = (
            f"What is {agent_name}'s emotional state after not responding? Keep in mind that emotions typically change incrementally and only experience large spikes in response to significant events (e.g., major shocks, breakthroughs). Use this principle to ensure gradual and realistic emotional changes. Provide:\n" \
                f"1. An updated emotional state object (include only emotions whose values have changed).\n" \
                f"2. The reasoning behind these changes. Keep this brief, one or two sentences max.\n\n" \
                f"Use the scale {min_emotion_value} (lowest intensity) to {max_emotion_value} (highest intensity). " \
                f"Do not add new emotions."
        )
        return prompt


def generate_sentiment_analysis_prompt(agent_name, username, min_sentiment_value, max_sentiment_value):
    """
    Generates a prompt to analyze the AI agent's sentiments toward the user after a message exchange.

    Parameters:
        agent_name (str): The name of the AI agent.
        username (str): The name of the user.
        min_sentiment_value (int): The minimum value on the sentiment intensity scale.
        max_sentiment_value (int): The maximum value on the sentiment intensity scale.

    Returns:
        str: A dynamically generated prompt.
    """
    prompt = (
        f"What are {agent_name}'s sentiments towards {username} after this message exchange? Keep in mind that sentiments typically change incrementally and only experience large spikes in response to significant events (e.g., major shocks, breakthroughs). Use this principle to ensure gradual and realistic sentiment changes. Provide:\n" \
                f"1. An updated sentiment state object (include only emotions whose values have changed).\n" \
                f"2. The reasoning behind these changes. Keep this brief, one or two sentences max.\n\n" \
                f"Use the scale {min_sentiment_value} (lowest intensity) to {max_sentiment_value} (highest intensity). " \
                f"Do not add new sentiments."
    )
    
    return prompt


def generate_summary_update_prompt(agent_name, username, current_summary):
    """
    Generates a prompt to update the AI agent's summary of the user based on new information
    from a message exchange and re-summarize it for brevity.

    Parameters:
        agent_name (str): The name of the AI agent.
        username (str): The name of the user.
        current_summary (str): The current summary of what the agent knows about the user.

    Returns:
        str: A dynamically generated prompt.
    """
    prompt = (
        f"Rewrite how {agent_name} would describe {username} in their own words, implementing any significant information they learned from this message exchange. This is the current description: ({current_summary}). Provide the updated summary in a JSON object with the property 'summary'. If nothing has changed keep it the same."
    )
    return prompt


def generate_extrinsic_relationship_prompt(username, extrinsic_relationship_options):
    """
    Generates a prompt to determine whether the extrinsic relationship of the user has changed,
    and to specify the current extrinsic relationship from a list of predefined options.

    Parameters:
        agent_name (str): The name of the AI agent.
        username (str): The name of the user.
        extrinsic_relationship_options (list): A list of possible extrinsic relationship options.

    Returns:
        str: A dynamically generated prompt.
    """
    options_formatted = ", ".join(extrinsic_relationship_options)
    prompt = (
        f"Has the extrinsic relationship of {username} changed? "
        f"Whether it has changed or not, provide the extrinsic relationship out of these options ({options_formatted}) "
        f"in a JSON object with the property 'extrinsic_relationship'."
    )
    return prompt

def generate_identity_update_prompt(agent_name, current_identity):
    """
    Generates a prompt to update the AI agent's self-identity based on new information
    from a message exchange and re-summarize it for brevity.

    Parameters:
        agent_name (str): The name of the AI agent.
        current_identity (str): The AI agent's current self-identity.

    Returns:
        str: A dynamically generated prompt.
    """
    prompt = (
        f"This is how {agent_name} described themselves before this message exchange: ({current_identity})."
        f"Rewrite how {agent_name} would describe themselves, in their own words, implementing any significant information they learned about themself from this message exchange. If nothing new was learned do not change anything. Keep this brief, no more than four sentences."
        f" Provide the updated identity in a JSON object with the property 'identity'."
    )
    return prompt


def generate_personality_adjustment_prompt(agent_name, personality, sentiment, user_name, extrinsic_relationship, 
                                           min_personality_value, max_personality_value, max_range):
    """
    Generates a prompt to determine how the AI agent's sentiments and relationship with the user 
    influence its personality traits during their interaction.

    Parameters:
        agent_name (str): The name of the AI agent.
        personality (str): The agent's current personality traits.
        sentiment (str): The agent's sentiments towards the user.
        user_name (str): The name of the user.
        extrinsic_relationship (str): The extrinsic relationship between the agent and the user.
        min_personality_value (int): Minimum value for personality trait intensity.
        max_personality_value (int): Maximum value for personality trait intensity.

    Returns:
        str: A dynamically generated prompt.
    """
    prompt = (
        f"These are {agent_name}'s personality traits: {personality}. "
        f"This is {agent_name}'s sentiment towards {user_name}: {sentiment}. "
        f"How would these sentiments, and their extrinsic relationship ({extrinsic_relationship}) alter "
        f"{agent_name}'s personality towards {user_name}? Provide:\n" \
              f"1. An updated personality object (include only personality traits whose values have changed).\n" \
              f"2. Use the scale {min_personality_value} (lowest intensity) to {max_personality_value} (highest intensity). " \
              f"The max value a trait can change by is {max_range} in either direction."
    )
    return prompt


def generate_thought_prompt(self, recent_all_messages):
    """
    Generates a prompt to determine if the AI is thinking and if so, what their thought is.

    Parameters:
        self (object): The object of the AI agent.
        recent_all_messages (array): The list of the last ten messages the AI read
        
    Returns:
        str: A dynamically generated prompt.
    """
    prompt = (
        f"{self["name"]}'s personality traits are: ({self["personality"]}).\n\n "
        f"{self["name"]}'s emotional state is: ({self["emotional_status"]}).\n\n "
        f"{self["name"]}'s identity is: ({self["identity"]}).\n\n "
        f"The time is currently: ({datetime.now()}).\n\n "
        f"The last ten remembered messages they read are: ({recent_all_messages}). "
        f"Considering all of this, is {self["name"]} thinking right now? If yes, respond with the specific thought they are having. If no, respond with '...'"
        f"Provide:\n" \
              f"1. A json object with a single property 'thought'.\n" \
    )
    return prompt