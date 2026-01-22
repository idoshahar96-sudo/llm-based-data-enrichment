import json

# a function to extract the first JSON array from a string and parse it
def extract_json_array(text):
    if not text or not text.strip():
        raise ValueError("Empty LLM response")
    text = text.strip()
    # Defensive: handle markdown fences if they appear
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 2:
            text = parts[1].strip()
        if text.lower().startswith("json"):
            text = text[4:].strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON array found in response:\n{text}")
    return json.loads(text[start:end + 1])
