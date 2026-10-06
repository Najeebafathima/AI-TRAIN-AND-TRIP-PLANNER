import json
import ollama
from tools import search_trains, find_places

MODEL = "llama3.2"
LAST_PLACE = ""

SYSTEM = """You are a friendly travel assistant for trips in India and worldwide.
Rules:
- You can answer for ANY city, state or country.
- If REFERENCE DATA is given, use it first.
- If there is no reference data, use your general knowledge and say clearly
  that it is general information and may need checking.
- Never invent exact train numbers or timings. If no train data is given,
  say exact trains are not in your data and suggest checking IRCTC/NTES.
- For trip plans use Day 1, Day 2, ... with estimated costs in INR,
  best time to visit, and travel tips.
- If the user only typed a place name, give a short overview: top places,
  best time to visit, how to reach, then ask how many days and the budget."""


def extract_intent(text):
    """Ask the model only to pull out place names as JSON."""
    prompt = (
        "From the user message, extract JSON with keys "
        '"from_city", "to_city", "destination". '
        "Use an empty string if not mentioned. If only one place is "
        'mentioned, put it in "destination". Reply with JSON only.\n\n'
        f"Message: {text}"
    )
    try:
        r = ollama.chat(model=MODEL,
                        messages=[{"role": "user", "content": prompt}],
                        format="json")
        data = json.loads(r.message.content)
        return {k: str(data.get(k, "") or "").strip()
                for k in ("from_city", "to_city", "destination")}
    except Exception:
        return {"from_city": "", "to_city": "", "destination": ""}


def build_context(user_text):
    global LAST_PLACE
    info = extract_intent(user_text)
    parts = []

    if info["from_city"] and info["to_city"]:
        trains = search_trains(info["from_city"], info["to_city"])
        if isinstance(trains, str):
            parts.append(f"TRAINS {info['from_city']} to {info['to_city']}: "
                         "none found in the dataset.")
        else:
            parts.append(f"TRAINS {info['from_city']} to {info['to_city']}: "
                         + json.dumps(trains))

    dest = info["destination"] or info["to_city"]
    LAST_PLACE = dest
    if dest:
        places = find_places("tourist places", dest)
        if places:
            parts.append(f"PLACES in {dest} (from dataset):\n" + "\n".join(places))
        else:
            parts.append(f"PLACES in {dest}: not in the dataset, "
                         "use general knowledge.")

    return "\n\n".join(parts)


def chat(messages):
    """messages: list of {'role','content'} dicts; last one is the new user message."""
    if not messages or messages[0]["role"] != "system":
        messages.insert(0, {"role": "system", "content": SYSTEM})

    user_text = messages[-1]["content"]
    context = build_context(user_text)

    # temporary copy: reference data is added only for this one answer
    temp = [dict(m) for m in messages]
    if context:
        temp[-1]["content"] = f"{user_text}\n\nREFERENCE DATA:\n{context}"

    resp = ollama.chat(model=MODEL, messages=temp)
    reply = resp.message.content
    messages.append({"role": "assistant", "content": reply})
    return reply