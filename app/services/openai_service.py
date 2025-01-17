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
        # Query OpenAI API
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",  # Adjust to your model name
            messages=messages,
            response_format = schema
        )

        # Parse and validate the response
        content_json = response.choices[0].message.content
        parsed_content = json.loads(content_json)

        #print("---------------")
        #print(parsed_content)
        #print("---------------")
        
        return parsed_content
    except Exception as error:
        print(f"System Error: {error}")
        return None