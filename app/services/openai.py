import openai
import json
import asyncio

from app.core.config import DEBUG_MODE, OPENAI_KEY, GPT_FAST, GPT_QUALITY

def _get_client() -> openai.OpenAI:
    if not OPENAI_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return openai.OpenAI(api_key=OPENAI_KEY)

async def structured_query(messages, schema, quality = True):
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
        client = _get_client()
        response = await asyncio.to_thread(
            client.beta.chat.completions.parse,
            model=gpt_model,
            messages=messages,
            response_format=schema,
        )

        content_json = response.choices[0].message.content
        parsed_content = json.loads(content_json)
        
        if DEBUG_MODE:
            print(parsed_content) 
            print (response.usage)
               
        return parsed_content
    except Exception as error:
        print(f"Error - structured_query: {error}")
        return None
