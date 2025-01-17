import openai
import json
import os
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI()

openai.api_key = os.getenv('OPENAI_API_KEY')

async def get_structured_query_response(messages, schema):
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
        
        return parsed_content
    except Exception as error:
        print(f"Error - get_structured_query_response: {error}")
        return None