import openai
import json

from app.core.config import OPENAI_KEY, GPT_FAST, GPT_QUALITY

client = openai.OpenAI()

openai.api_key = OPENAI_KEY

async def get_structured_response(messages, schema, quality = True):
    """
    Queries the OpenAI API to receive a structured response.

    :param messages: List of message objects for the query
    :param schema: Schema for structuring the result (as JSON)
    :return: Parsed response as a Python dictionary, or None on error
    """
    gpt_model = GPT_FAST
    if quality:
        gpt_model = GPT_QUALITY
    try:
        response = client.beta.chat.completions.parse(
            model= gpt_model,   
            messages=messages,
            response_format = schema
        )

        content_json = response.choices[0].message.content
        parsed_content = json.loads(content_json)
        print(parsed_content) 
               
        return parsed_content
    except Exception as error:
        print(f"Error - get_structured_query_response: {error}")
        return None
