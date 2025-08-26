import openai
import json
import os
from dotenv import load_dotenv

from app.constants.constants import FUNCTION_DESCRIPTIONS

load_dotenv()
client = openai.OpenAI()

openai.api_key = os.getenv('OPENAI_API_KEY')

async def get_structured_response(messages, schema):
    """
    Queries the OpenAI API to receive a structured response.

    :param messages: List of message objects for the query
    :param schema: Schema for structuring the result (as JSON)
    :return: Parsed response as a Python dictionary, or None on error
    """
    try:
        response = client.beta.chat.completions.parse(
            model= os.getenv('GPT_MODEL'),
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
    

async def check_for_memory(message_queries):
    """
    Queries the OpenAI API to call a function for adding a memory to the database.

    :param message_queries: message query list
    :return: Parsed response as a Python dictionary, or None on error
    """
    try:
        response = client.beta.chat.completions.parse(
            model = os.getenv('GPT_MODEL'),
            messages=message_queries,
            functions=FUNCTION_DESCRIPTIONS,
            function_call='auto'
        )

        content_json = response.choices[0].message
               
        return content_json
    except Exception as error:
        print(f"Error - check_for_memory: {error}")
        return None
