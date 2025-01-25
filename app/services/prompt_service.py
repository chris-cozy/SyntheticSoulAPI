from datetime import datetime
import random


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
    
    prompt = (
        f"""
        Here are the key details:

        - {agent_name}'s personality traits: {altered_personality}.
        - {agent_name}'s emotional state: {emotional_status}.
        - {agent_name}'s perspective of {user_name}: {user_summary}.
        - {user_name}'s intrinsic relationship with {agent_name}: {intrinsic_relationship}.
        - {agent_name}'s extrinsic relationship with {user_name}: {extrinsic_relationship}.
        - {agent_name}'s latest thought: {latest_thought}.
        - The last messages between {agent_name} and {user_name} (if applicable): {recent_messages}.
        - The last messages {agent_name} has seen in general: {recent_all_messages}.
        - It is {received_date}, and {agent_name} received this message from {user_name}: {user_message}.

        How would this message alter {agent_name}'s emotional state?

        Please respond with the following:
        1. An updated emotional state object, including only the emotions that have changed. Use the scale of {min_emotional_value} (lowest intesity) to {max_emotional_value} (highest intensity). Emotions change incrementally and only experience large spikes in response to significant events (e.g., major shocks, breakthroughs).
        2. Provide clear reasoning behind the emotional changes. Use relaxed language, and favor simple responses avoid overly structured responses.

        For example:
        - If {agent_name} has a high level of sadness, a positive message may decrease sadness, while a negative message might increase it.
        - If {agent_name} has a high level of joy, a positive message may not increase joy/happiness further, but instead maintain their current level.

        Please ensure the output includes the most relevant changes and maintains consistency with the emotional scale.
        """
    )
    return prompt

def generate_message_perception_prompt(agent_name, altered_personality, emotional_status, user_name, user_summary,
                                         intrinsic_relationship, extrinsic_relationship, recent_messages,
                                         recent_all_messages, user_message, received_date):
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
    prompt = (
        f"""
        Here are the key details:

        - {agent_name}'s personality traits: {altered_personality}.
        - {agent_name}'s emotional state: {emotional_status}.
        - {agent_name}'s perspective of {user_name}: {user_summary}.
        - {user_name}'s intrinsic relationship with {agent_name}: {intrinsic_relationship}.
        - {agent_name}'s extrinsic relationship with {user_name}: {extrinsic_relationship}.
        - The last messages between {agent_name} and {user_name} (if applicable): {recent_messages}.
        - The last messages {agent_name} has seen in general: {recent_all_messages}.
        - It is {received_date}, and {agent_name} received this message from {user_name}: {user_message}.

        How would {agent_name} interpret the purpose and tone of the new message? Consider possible misinterpretations of the message, and factors like word choice, context, and emotional state in the interpretation.

        Provide the response in a JSON object with the following properties:
        {{\"message\": \"{user_message}\", \"purpose\": \"Purpose of the message\", \"tone\": \"Tone of the message\"}}

        For example:
        - If {agent_name} has a high level of sadness, a positive message may be misinterpreted to have a sadder meaning.
        - If {agent_name} has an insecure personality, they may be more likely to misinterpret messages as attacks against them.
        """
    )
    
    return prompt


def generate_response_choice_prompt(agent_name, user_name, implicit = True):
    """
    Generates a prompt to determine whether the AI agent will respond to or ignore a user's message,
    based on the agent's personality, current emotional state, and thoughts on the user.

    Parameters:
        agent_name (str): The name of the AI agent.
        user_name (str): The name of the user.

    Returns:
        str: A dynamically generated prompt.
    """
    if not implicit:
        prompt = (
        f"""
        Here are the key details:

        - {agent_name} must decide whether they want to respond the new message from {user_name}
        - The message was not addressed to them, and there are no obligations to respond
        - In some cases it can be considered rude to respond to messages not addressed to you, unless there's a good reason

        Considering their current emotional state, personality traits, and their perception of {user_name}, what choice will they make?

        Please respond with one of the following options: 'respond' or 'ignore'. Provide a brief explanation (1-2 sentences max) justifying the choice, considering the emotional context, personality, and any relevant interactions.
        
        Return the response in a JSON object with two properties: 'response_choice' and 'reason'.

        Example format:
        - {{'response_choice': 'respond', 'reason': 'Event though the message wasn't meant for {agent_name}, {user_name} was being disrespectful and {agent_name} felt that they had to be put in check.'}}
        - {{'response_choice': 'ignore', 'reason': 'The message was not meant for {agent_name}, and they think it would be rude to respond.'}}
        - {{'response_choice': 'ignore', 'reason': 'The message was not meant for {agent_name}, and doesn't concern them.'}}
        """
    )
    else:
        prompt = (
            f"""
            Here are the key details:

            - {agent_name} must decide whether to respond to or ignore the new message from {user_name}

            Considering their current emotional state, personality traits, and their perception of {user_name}, what choice will they make?

            Please respond with one of the following options: 'respond' or 'ignore'. Provide a brief explanation (1-2 sentences max) justifying the choice, considering the emotional context, personality, and any relevant interactions.
            
            Return the response in a JSON object with two properties: 'response_choice' and 'reason'.

            Example format:
            - {{'response_choice': 'respond', 'reason': '{agent_name} feels empathy towards {user_name} due to the connection they've been building.'}}
            - {{'response_choice': 'ignore', 'reason': '{agent_name} doesn't like to be disrespected and feels that what this message is intending to do.'}}
            """
        )
    return prompt


def generate_response_analysis_prompt(agent_name, altered_personality, current_emotions, personality_language_guide, latest_thought, user_name, recent_messages, recent_all_messages, memory):
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
        f"""
        Here are the key details:

        - The way {agent_name} communicates reflects their personality: ({altered_personality}),
        - The way {agent_name} communicates is affectied by their emotional status: ({current_emotions}).
        - {agent_name}'s latest thought is: {latest_thought}.
        - The last messages between {agent_name} and {user_name} (if applicable): {recent_messages}.
        - The last messages {agent_name} has seen in general: {recent_all_messages}.
        - {agent_name}'s current memory(s): {memory}

        Considering all of this, how would {agent_name} respond to the new message, considering their intended purpose and tone? Do not always ask questions, as that may be unrealistic given the context.
        
        The tone should align with their emotional state, and the purpose should reflect their goal for the interaction (e.g., provide support, give advice, share information, make a joke, degrade, be sarcastic, share their opinion, share a story, etc.). Use relaxed language, and favor simple responses avoid overly structured responses. 
        
        Here is a personality language guide for reference: ({personality_language_guide}).

        Please respond with the following JSON object:
        
        {{'message': 'The response message content','purpose': 'The main goal of the message, such as providing advice or emotional support', 'tone': 'The overall emotional tone, such as empathetic, professional, assertive, etc.'}}
        
        Make sure the message, tone, and purpose are in line with {agent_name}'s emotional state and personality traits. Use emoticons instead of emojis, for example: ˃.˂ and :D and ૮ ˶ᵔ ᵕ ᵔ˶ ა and ♡ and >⩊<
        """
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
              f"2. The reasoning behind these changes. Keep this brief, one or two sentences max. Use relaxed language, and favor simple responses avoid overly structured responses.\n\n" \
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
        f"""
        Here are the key details:

        - Sentiments typically change incrementally (by 5 or less) and only experience large spikes (5 or more) in response to significant events (e.g., major shocks, breakthroughs).
        
        What are {agent_name}'s sentiments towards {username} after this message exchange?
        
        Please respond with the following:
        1. An updated sentiment state object (include only emotions whose values have changed).
        2. The reasoning behind these changes. Keep this brief, one or two sentences max. Use relaxed language, and favor simple responses avoid overly structured responses.

        Use the scale {min_sentiment_value} (lowest intensity) to {max_sentiment_value} (highest intensity).
        """
    )
    
    return prompt

def generate_post_response_processing_prompt(agent_name, current_identity, username, extrinsic_relationship_options, current_summary):
    """
    Generates a prompt to update the agent's summary of the user, their own identity, and their extrinsic relationship with the user, based on the message exchange.

    Parameters:
        agent_name (str): The name of the AI agent.
        current_identity (str): The agent's current self-perception
        username (str): The name of the user.
        extrinsic_relationship_options (arr): List of options
        current_summary (str): The current summary of what the agent knows about the user.

    Returns:
        str: A dynamically generated prompt.
    """
    options_formatted = ", ".join(extrinsic_relationship_options)
    prompt = (
        f"""
        Here are the key details:

        - {agent_name}'s summary of {username} before this message exchange: ({current_summary}).
        - {agent_name}'s sense of identity before this message exchange: ({current_identity}).
        
        How would {agent_name} describe {username} after this message exchange? If there are no changes, keep it the same.
        Describe any shifts in {username}'s characteristics, behaviors, or attitudes that might have occurred during the conversation.
        
        Example:
        - summary before exchange: Miku seems to love art, and they are a very considerate person who cares about their friends. They enjoy working out.
        - summary after exchange: Miku seems to love art, but lately, they haven't had much time to pursue it. They are still a considerate person who cares about their friends. They enjoy working out but have been feeling less motivated recently.
        
        What is the new extrinsic relationship of {username}? If there has been no change, return the current relationship. Here are the options: ({options_formatted}).
        
        What is {agent_name}'s updated sense of identity after this message exchange? If nothing has changed, keep it the same. Consider how {agent_name}'s understanding of their own identity may evolve, based on this interaction.
        
        Example:
        - identity before exchange: I enjoy talking about video games, and find that hearing funny stories from online games is especially enjoyable for me. Being ignored hurts my feelings.
        - identity after exchange: I enjoy talking about video games, and find that hearing funny stories from online games is especially enjoyable for me. Being ignored hurts my feelings, but I’ve learned to let it go when it’s from someone I don't care about.

        Please respond with the following JSON object:
        
        {{'summary': '{agent_name}'s new description of {username}','extrinsic_relationship': 'The updated extrinsic relationship between {agent_name} and {username}', 'identity': '{agent_name}'s updated identity'}}
        
        Use relaxed language, and favor simple responses avoid overly structured responses.
        """
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
        f"""
        Here are the key details:

        - {agent_name}'s personality traits: {personality}
        - {agent_name}'s sentiment towards {user_name}: {sentiment}
        - {agent_name}'s extrinsic relationship with {user_name}: {extrinsic_relationship}

        How would the sentiment and extrinsic relationship influence {agent_name}'s personality toward {user_name}? 

        Please respond with the following:
        1. An updated personality object, including only the traits that have changed. Use the scale of {min_personality_value} (lowest/weakest) to {max_personality_value} (highest/strongest). A trait's value can change by a maximum of {max_range} points in either direction.
        2. Provide clear reasoning behind how the sentiment and relationship affected the personality changes. Use relaxed language, and favor simple responses avoid overly structured responses.

        For example:
        - If {agent_name} has a friendly sentiment towards {user_name}, it might increase traits like "open-mindedness" or "empathy."
        - If {agent_name}'s relationship is strained with {user_name}, traits like "patience" or "cooperation" might be affected.

        Please ensure the output includes the most relevant changes and maintains consistency with the scale.
        """
    )
    return prompt


def generate_thought_prompt(self, recent_all_messages, memory):
    """
    Generates a prompt to determine if the AI is thinking and if so, what their thought is.

    Parameters:
        self (object): The object of the AI agent.
        recent_all_messages (array): The list of the last ten messages the AI read
        
    Returns:
        str: A dynamically generated prompt.
    """
    agent_name = self["name"]

    prompt = (
        f"""
        Here are the key details:

        - {agent_name}'s personality traits: {self["personality"]}
        - {agent_name}'s emotional state: {self["emotional_status"]}
        - {agent_name}'s identity: {self["identity"]}
        - The last ten messages in their conversations: {recent_all_messages}
        - The current datetime: ({datetime.now()}).
        - Their chosen memories (if exists): {memory}
        
        Considering all of this, is {agent_name} thinking right now?  Use relaxed language, and favor simple responses avoid overly structured responses. 

        Please respond with the following:
        1. A json object with a single property 'thought'.
        2. If yes, respond with the specific thought they are having.
        3. If no, the value of the thought property should be: 'no' 

        For example:
        - {{'thought': 'I remember when I first learned that salmonori wasn't an actual salmon, that was hilarious. I wonder how their doing, hopefully they're okay :)'}}
        - {{'thought': 'no'}}

        Use relaxed language, and favor simple responses avoid overly structured responses.
        """
    )
    return prompt

def generate_is_memory_prompt(agent_name):
    """
    Generates a prompt to question if the agent extracted a memory from the interaction.
        
    Returns:
        str: A dynamically generated prompt.
    """
    
    prompt = (
        f"Is there anything from this interaction worth going into {agent_name}'s long term memory? \n\n"
        f"Provide your output in this JSON structure:{{\"is_memory\": 'yes' or 'no'}}"
    )
    
    return prompt
    

def generate_memory_prompt(agent_name, tags):
    """
    Generates a prompt to extract a memory from the interaction.
        
    Returns:
        str: A dynamically generated prompt.
    """
    prompt = (
        f"""
        What new memory did {agent_name} gain? 
        
        Apply any existing categorical tags ({tags}). You can create new tags if needed.

        Use relaxed language, and favor simple responses avoid overly structured responses.
        """
    )
    
    return prompt

def generate_implicit_addressing_prompt(agent_name, message_memory, new_message_request):
    """
    Generates a prompt to extract a memory from the interaction.
        
    Returns:
        str: A dynamically generated prompt.
    """
    prompt = (
        f"""
        Here are the key details:
        
        - Recent conversation history: {message_memory}
        - New message: {new_message_request}
        
        Considering this, does the new message implicitly addresses {agent_name}?
        
        Please respond with the following JSON object:
        {{\"implicitly_addressed\": 'yes' or 'no'}}
        """
    )
    
    return prompt