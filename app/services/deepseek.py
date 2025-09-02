import openai
import json

from app.core.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

client = openai.OpenAI(base_url= DEEPSEEK_BASE_URL, api_key= DEEPSEEK_API_KEY)

async def get_structured_query_reasoning_response(messages, schema):
    """
    Queries the DeepSeek API to receive a structured response.

    :param messages: List of message objects for the query
    :param schema: Schema for structuring the result (as JSON)
    :return: Parsed response as a Python dictionary, or None on error
    """
    try:
        response = client.chat.completions.create(
            model= DEEPSEEK_MODEL,
            messages=messages
        )

        content_json = response.choices[0].message.content
        parsed_content = json.loads(content_json)
        print(parsed_content) 
               
        return parsed_content
    except Exception as error:
        print(f"Error - get_structured_query_reasoning_response: {error}")
        return None
