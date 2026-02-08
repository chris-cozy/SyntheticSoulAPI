import asyncio
import json
from typing import Any, Dict, List

import openai

from app.core.config import (
    DEBUG_MODE,
    GPT_FAST,
    GPT_QUALITY,
    LLM_MODE,
    OLLAMA_API_KEY,
    OLLAMA_BASE_URL,
    OLLAMA_FAST_MODEL,
    OLLAMA_QUALITY_MODEL,
    OPENAI_KEY,
)

LOCAL_MAX_SCHEMA_RETRIES = 2
MAX_SCHEMA_ERRORS = 12


def _get_client() -> openai.OpenAI:
    if LLM_MODE == "local":
        return openai.OpenAI(base_url=OLLAMA_BASE_URL, api_key=OLLAMA_API_KEY)

    if not OPENAI_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return openai.OpenAI(api_key=OPENAI_KEY)


def _get_model(quality: bool) -> str:
    if LLM_MODE == "local":
        local_model = OLLAMA_QUALITY_MODEL if quality else OLLAMA_FAST_MODEL
        if not local_model:
            key = "OLLAMA_QUALITY_MODEL" if quality else "OLLAMA_FAST_MODEL"
            raise RuntimeError(f"{key} is not set while LLM_MODE=local.")
        return local_model

    hosted_model = GPT_QUALITY if quality else GPT_FAST
    if not hosted_model:
        key = "GPT_QUALITY_MODEL" if quality else "GPT_FAST_MODEL"
        raise RuntimeError(f"{key} is not set while LLM_MODE=hosted.")
    return hosted_model


def _normalize_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        # Some providers return segmented parts; join text-like parts.
        parts: List[str] = []
        for part in content:
            if isinstance(part, dict):
                parts.append(str(part.get("text", "")))
            else:
                parts.append(str(part))
        return "".join(parts)
    return str(content)


def _extract_json_object(text: str) -> str:
    content = text.strip()

    if content.startswith("```"):
        lines = content.splitlines()
        if len(lines) >= 3:
            content = "\n".join(lines[1:-1]).strip()

    try:
        json.loads(content)
        return content
    except Exception:
        pass

    start = content.find("{")
    while start != -1:
        depth = 0
        in_string = False
        escaped = False
        for idx in range(start, len(content)):
            ch = content[idx]
            if escaped:
                escaped = False
                continue
            if ch == "\\":
                escaped = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    candidate = content[start : idx + 1]
                    try:
                        json.loads(candidate)
                        return candidate
                    except Exception:
                        break
        start = content.find("{", start + 1)

    raise ValueError("No JSON object found in model response.")


def _parse_response_content(content: Any) -> Any:
    normalized = _normalize_content(content)
    parsed = _extract_json_object(normalized)
    return json.loads(parsed)


def _messages_with_schema_guard(messages: List[Dict[str, Any]], schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    json_schema = schema.get("json_schema", {})
    schema_name = json_schema.get("name", "response")
    schema_body = json_schema.get("schema", schema)

    guard_message = {
        "role": "system",
        "content": (
            f"Return only valid JSON for schema '{schema_name}'. "
            f"Do not include markdown or explanatory text.\nSchema:\n{json.dumps(schema_body)}"
        ),
    }
    return [guard_message, *messages]


def _schema_root(schema: Dict[str, Any]) -> Dict[str, Any]:
    if schema.get("type") == "json_schema":
        return schema.get("json_schema", {}).get("schema", {})
    return schema


def _matches_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def _validate_json_value(value: Any, schema_node: Dict[str, Any], path: str, errors: List[str]) -> None:
    if len(errors) >= MAX_SCHEMA_ERRORS or not isinstance(schema_node, dict):
        return

    type_spec = schema_node.get("type")
    if type_spec is not None:
        allowed_types = type_spec if isinstance(type_spec, list) else [type_spec]
        if not any(_matches_type(value, t) for t in allowed_types):
            errors.append(f"{path}: expected type {allowed_types}, got {type(value).__name__}")
            return
        if value is None:
            return

    if "enum" in schema_node and value not in schema_node["enum"]:
        errors.append(f"{path}: value {value!r} is not in enum {schema_node['enum']}")

    if isinstance(value, str):
        min_length = schema_node.get("minLength")
        max_length = schema_node.get("maxLength")
        if isinstance(min_length, int) and len(value) < min_length:
            errors.append(f"{path}: string shorter than minLength {min_length}")
        if isinstance(max_length, int) and len(value) > max_length:
            errors.append(f"{path}: string longer than maxLength {max_length}")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema_node.get("minimum")
        maximum = schema_node.get("maximum")
        if minimum is not None and value < minimum:
            errors.append(f"{path}: value {value} below minimum {minimum}")
        if maximum is not None and value > maximum:
            errors.append(f"{path}: value {value} above maximum {maximum}")

    if isinstance(value, list):
        min_items = schema_node.get("minItems")
        max_items = schema_node.get("maxItems")
        if isinstance(min_items, int) and len(value) < min_items:
            errors.append(f"{path}: array smaller than minItems {min_items}")
        if isinstance(max_items, int) and len(value) > max_items:
            errors.append(f"{path}: array larger than maxItems {max_items}")
        if schema_node.get("uniqueItems"):
            serialized = [json.dumps(item, sort_keys=True, default=str) for item in value]
            if len(set(serialized)) != len(serialized):
                errors.append(f"{path}: array contains duplicate items but uniqueItems=true")

        item_schema = schema_node.get("items")
        if isinstance(item_schema, dict):
            for idx, item in enumerate(value):
                _validate_json_value(item, item_schema, f"{path}[{idx}]", errors)
                if len(errors) >= MAX_SCHEMA_ERRORS:
                    return

    if isinstance(value, dict):
        properties = schema_node.get("properties", {})
        required = schema_node.get("required", [])

        for req_key in required:
            if req_key not in value:
                errors.append(f"{path}.{req_key}: missing required field")
                if len(errors) >= MAX_SCHEMA_ERRORS:
                    return

        additional = schema_node.get("additionalProperties", True)
        for key, item_value in value.items():
            if key in properties:
                _validate_json_value(item_value, properties[key], f"{path}.{key}", errors)
            elif additional is False:
                errors.append(f"{path}.{key}: additional property not allowed")
            elif isinstance(additional, dict):
                _validate_json_value(item_value, additional, f"{path}.{key}", errors)
            if len(errors) >= MAX_SCHEMA_ERRORS:
                return


def _validate_structured_payload(payload: Any, schema: Dict[str, Any]) -> List[str]:
    root = _schema_root(schema)
    if not root:
        return []
    errors: List[str] = []
    _validate_json_value(payload, root, "$", errors)
    return errors


def _build_retry_prompt(schema: Dict[str, Any], errors: List[str]) -> str:
    root = _schema_root(schema)
    issue_lines = "\n".join(f"- {error}" for error in errors[:8])
    return (
        "Your previous JSON output failed schema validation.\n"
        f"Issues:\n{issue_lines}\n\n"
        "Return ONLY corrected JSON. Do not include markdown, comments, or prose.\n"
        f"Schema:\n{json.dumps(root)}"
    )


async def _create_local_structured_response(
    client: openai.OpenAI,
    model: str,
    messages: List[Dict[str, Any]],
    schema: Dict[str, Any],
    force_json_mode: bool = False,
) -> Any:
    if not force_json_mode:
        try:
            return await asyncio.to_thread(
                client.chat.completions.create,
                model=model,
                messages=messages,
                response_format=schema,
                temperature=0,
            )
        except Exception:
            pass

    # Ollama models commonly support JSON mode even when full json_schema mode is unsupported.
    return await asyncio.to_thread(
        client.chat.completions.create,
        model=model,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0,
    )


async def structured_query(messages, schema, quality=True):
    """
    Queries the OpenAI API to receive a structured response.

    :param messages: List of message objects for the query
    :param schema: Schema for structuring the result (as JSON)
    :return: Parsed response as a Python dictionary, or None on error
    """
    try:
        client = _get_client()
        selected_model = _get_model(quality)

        if LLM_MODE == "local":
            base_messages = _messages_with_schema_guard(messages, schema)
            working_messages = list(base_messages)
            parsed_content = None
            response = None
            validation_errors: List[str] = []

            for attempt in range(LOCAL_MAX_SCHEMA_RETRIES + 1):
                response = await _create_local_structured_response(
                    client,
                    selected_model,
                    working_messages,
                    schema,
                    force_json_mode=attempt > 0,
                )

                raw_content = _normalize_content(response.choices[0].message.content)
                try:
                    parsed_content = _parse_response_content(raw_content)
                    validation_errors = _validate_structured_payload(parsed_content, schema)
                    if not validation_errors:
                        break
                except Exception as parse_error:
                    validation_errors = [f"$: could not parse JSON output ({parse_error})"]

                if attempt >= LOCAL_MAX_SCHEMA_RETRIES:
                    raise ValueError(
                        "Local model failed schema validation after retries: "
                        + "; ".join(validation_errors[:8])
                    )

                correction_prompt = _build_retry_prompt(schema, validation_errors)
                working_messages = base_messages + [
                    {"role": "assistant", "content": raw_content[:6000]},
                    {"role": "user", "content": correction_prompt},
                ]
        else:
            response = await asyncio.to_thread(
                client.beta.chat.completions.parse,
                model=selected_model,
                messages=messages,
                response_format=schema,
            )
            parsed_content = _parse_response_content(response.choices[0].message.content)
            validation_errors = _validate_structured_payload(parsed_content, schema)
            if validation_errors:
                raise ValueError(
                    "Hosted model returned schema-invalid output: "
                    + "; ".join(validation_errors[:8])
                )

        if DEBUG_MODE:
            print(f"LLM mode: {LLM_MODE}, model: {selected_model}")
            print(parsed_content)
            print(response.usage)

        return parsed_content
    except Exception as error:
        print(f"Error - structured_query: {error}")
        return None
