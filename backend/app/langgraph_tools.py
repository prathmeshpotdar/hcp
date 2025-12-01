"""
Defensive LangGraph Tools (Groq LLM Powered)
- Writes debug log to app/langgraph_debug.log
- Non-fatal: groq_call returns None on failure
- Best-effort parsing; never raises to the FastAPI caller
- Includes self_test() to validate environment and connectivity
"""

import os
import re
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GROQ_API_URL = os.getenv("GROQ_API_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
DEBUG_LOG_PATH = os.path.join(os.path.dirname(__file__), "langgraph_debug.log")

def _log(msg):
    try:
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()}   {msg}\n")
    except Exception:
        pass  # never crash for logging

if not GROQ_API_KEY or not GROQ_API_URL:
    _log("ERROR: GROQ_API_URL or GROQ_API_KEY missing from environment")
    # don't raise here — we return graceful errors later

# ---------------------------
# Groq API wrapper (defensive)
# ---------------------------
def groq_call(messages, max_tokens=400, temperature=0.0, timeout=30):
    """
    Safe wrapper around Groq endpoint.
    Returns: assistant text on success (string) or None on failure.
    Logs request+response to langgraph_debug.log
    """
    if not GROQ_API_KEY or not GROQ_API_URL:
        _log("groq_call aborted: missing API_URL or API_KEY")
        return None

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    try:
        _log("GROQ REQUEST -> " + json.dumps({"url": GROQ_API_URL, "payload_preview": payload}, default=str))
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=timeout)
    except Exception as e:
        _log(f"GROQ CALL EXCEPTION: {repr(e)}")
        return None

    try:
        body = resp.json()
    except Exception as e:
        _log(f"GROQ NON-JSON RESPONSE STATUS {resp.status_code}: {resp.text[:1000]!s}")
        return None

    _log(f"GROQ RESPONSE STATUS {resp.status_code} -> {json.dumps(body)[:4000]}")
    # Try to read choices[0].message.content
    try:
        return body["choices"][0]["message"]["content"]
    except Exception as e:
        # If groq returns plain text at top-level
        if isinstance(body, dict) and "content" in body:
            return body.get("content")
        _log(f"GROQ PARSE ERROR: {repr(e)} -- body keys: {list(body.keys())}")
        return None

# ---------------------------
# Normalizers
# ---------------------------
def normalize_date(date_text):
    if not date_text:
        return None
    dt = str(date_text).strip().lower()
    dt = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", dt)
    dt = dt.replace("/", "-").replace(",", "")
    formats = [
        "%d-%b-%Y", "%d-%B-%Y", "%d-%m-%Y",
        "%Y-%m-%d", "%d-%m-%y", "%d %b %Y", "%b %d %Y", "%B %d %Y"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(dt, fmt).strftime("%Y-%m-%d")
        except:
            continue
    m = re.search(r"(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{4})", dt)
    if m:
        try:
            return datetime.strptime(f"{m.group(1)} {m.group(2)} {m.group(3)}", "%d %b %Y").strftime("%Y-%m-%d")
        except:
            pass
    return None

def normalize_time(time_text):
    if not time_text:
        return None
    t = str(time_text).strip().lower().replace(".", "")
    m = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", t)
    if m:
        return f"{int(m.group(1)):02d}:{int(m.group(2)):02d}"
    m = re.search(r"\b([1-9]|1[0-2])\s*(am|pm)\b", t)
    if m:
        h = int(m.group(1)); ampm = m.group(2)
        if ampm == "pm" and h != 12: h += 12
        if ampm == "am" and h == 12: h = 0
        return f"{h:02d}:00"
    m = re.search(r"\b([1-9]|1[0-2]):([0-5]\d)\s*(am|pm)\b", t)
    if m:
        h = int(m.group(1)); mm = int(m.group(2)); ampm = m.group(3)
        if ampm == "pm" and h != 12: h += 12
        if ampm == "am" and h == 12: h = 0
        return f"{h:02d}:{mm:02d}"
    return None

# ---------------------------
# Tools - defensive parsing
# ---------------------------
def _safe_json_load(text):
    """Try to parse text as JSON; if it contains extra text, attempt to extract JSON object substring."""
    if not text or not isinstance(text, str):
        return None
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        # try to find first JSON object in text
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except:
                pass
    return None
#Extract “Dr. Smith”, “Prof. Rao”, etc.
def extract_hcp_name(text):
    prompt = [
        {"role": "system", "content": "Extract HCP name. Return ONLY JSON with key 'hcp_name'."},
        {"role": "user", "content": text}
    ]
    resp = groq_call(prompt)
    if resp:
        parsed = _safe_json_load(resp)
        if parsed and "hcp_name" in parsed:
            return {"hcp_name": parsed.get("hcp_name")}
    # fallback regex
    m = re.search(r"\b(dr\.?\s+[A-Z][a-zA-Z\-\']+|prof\.?\s+[A-Z][a-zA-Z\-\']+)\b", text, re.IGNORECASE)
    return {"hcp_name": m.group(0).strip() if m else None}
#Find and normalize dates into YYYY-MM-DD
def extract_date(text):
    prompt = [
        {"role": "system", "content": "Extract the date and return ONLY JSON {\"date\":\"...\"} or {\"date\": null}."},
        {"role": "user", "content": text}
    ]
    resp = groq_call(prompt)
    if resp:
        parsed = _safe_json_load(resp)
        if parsed and "date" in parsed:
            return {"date": normalize_date(parsed.get("date"))}
    # fallback regex
    m = re.search(r"\b(\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4})\b", text, re.IGNORECASE)
    if m:
        return {"date": normalize_date(m.group(0))}
    m2 = re.search(r"\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b", text)
    if m2:
        return {"date": normalize_date(m2.group(0))}
    return {"date": None}
#Detect times and convert into HH:MM
def extract_time(text):
    prompt = [
        {"role": "system", "content": "Extract time, return ONLY JSON {\"time\":\"...\"} or null."},
        {"role": "user", "content": text}
    ]
    resp = groq_call(prompt)
    if resp:
        parsed = _safe_json_load(resp)
        if parsed and "time" in parsed:
            return {"time": normalize_time(parsed.get("time"))}
    # fallback regex
    m = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", text)
    if m:
        return {"time": normalize_time(m.group(0))}
    m2 = re.search(r"\b([1-9]|1[0-2])\s*(am|pm)\b", text, re.IGNORECASE)
    if m2:
        return {"time": normalize_time(m2.group(0))}
    return {"time": None}
#Detect sentiment (Positive, Neutral, Negative).
def extract_sentiment(text):
    # quick keyword rules
    if re.search(r"\b(observed\/inferred\s+hcp\s+sentiment\s*[:\-]?\s*(positive|negative|neutral))", text, re.IGNORECASE):
        m = re.search(r"(positive|negative|neutral)", text, re.IGNORECASE)
        if m:
            val = m.group(1).capitalize()
            return {"sentiment": val, "sentiment_source": "observed"}
    if re.search(r"\b(positive|liked|interested|good|favourable|favorable)\b", text, re.IGNORECASE):
        return {"sentiment": "Positive", "sentiment_source": "inferred"}
    if re.search(r"\b(negative|not interested|did not|disliked|no interest)\b", text, re.IGNORECASE):
        return {"sentiment": "Negative", "sentiment_source": "inferred"}
    if re.search(r"\bneutral\b", text, re.IGNORECASE):
        return {"sentiment": "Neutral", "sentiment_source": "inferred"}

    # LLM fallback
    prompt = [
        {"role": "system", "content": "Classify as Positive, Neutral or Negative. Return ONLY JSON {\"sentiment\":\"...\"}."},
        {"role": "user", "content": text}
    ]
    resp = groq_call(prompt)
    if resp:
        parsed = _safe_json_load(resp)
        if parsed and "sentiment" in parsed:
            s = parsed.get("sentiment")
            if s:
                ss = s.strip().lower()
                if "pos" in ss: return {"sentiment": "Positive", "sentiment_source": "inferred"}
                if "neg" in ss: return {"sentiment": "Negative", "sentiment_source": "inferred"}
                if "neu" in ss: return {"sentiment": "Neutral", "sentiment_source": "inferred"}
    return {"sentiment": None, "sentiment_source": None}
#Extract brochures, samples, topics discussed.
def extract_materials_and_topics(text):
    prompt = [
        {"role": "system", "content": "Return JSON with keys: materials_shared (array), samples_distributed (array), topics_discussed (string|null)."},
        {"role": "user", "content": text}
    ]
    resp = groq_call(prompt)
    if resp:
        parsed = _safe_json_load(resp)
        if parsed:
            return {
                "materials_shared": parsed.get("materials_shared") or [],
                "samples_distributed": parsed.get("samples_distributed") or [],
                "topics_discussed": parsed.get("topics_discussed")
            }
    # fallback simple heuristics
    mats = []
    if re.search(r"\bbrochure\b", text, re.IGNORECASE): mats.append("Brochure")
    if re.search(r"\bleaflet\b", text, re.IGNORECASE): mats.append("Leaflet")
    qtys = re.findall(r"(\d+)\s*(?:samples|sample|vials|packs)", text, re.IGNORECASE)
    samples = [f"{q} sample(s)" for q in qtys] if qtys else []
    topics = None
    m = re.search(r"(discussed|about|regarding)\s+([A-Za-z0-9 \-,.&]+?)(?:\.|,|$)", text, re.IGNORECASE)
    if m:
        topics = m.group(2).strip()
    return {"materials_shared": mats, "samples_distributed": samples, "topics_discussed": topics}
#Generate a 1–2 line structured summary.
def summarize_interaction(text):
    prompt = [
        {"role": "system", "content": "Summarize interaction in 1-2 sentences. Return JSON {\"summary\":\"...\"} only."},
        {"role": "user", "content": text}
    ]
    resp = groq_call(prompt)
    if resp:
        parsed = _safe_json_load(resp)
        if parsed and "summary" in parsed:
            return {"summary": parsed.get("summary")}
    # fallback: first sentence
    s = re.split(r"[.\n]", text.strip())
    return {"summary": s[0].strip() if s and s[0].strip() else text[:200]}

# ---------------------------
# Combined extraction pipeline (never raises)
# ---------------------------
def run_extraction(text):
    try:
        out = {
            "hcp_name": None, "date": None, "time": None,
            "topics_discussed": None, "materials_shared": [], "samples_distributed": [],
            "sentiment": None, "sentiment_source": None, "summary": None
        }

        try:
            out.update(extract_hcp_name(text))
        except Exception as e:
            _log(f"extract_hcp_name error: {repr(e)}")

        try:
            out.update(extract_date(text))
        except Exception as e:
            _log(f"extract_date error: {repr(e)}")

        try:
            out.update(extract_time(text))
        except Exception as e:
            _log(f"extract_time error: {repr(e)}")

        try:
            s = extract_sentiment(text)
            out["sentiment"] = s.get("sentiment")
            out["sentiment_source"] = s.get("sentiment_source")
        except Exception as e:
            _log(f"extract_sentiment error: {repr(e)}")

        try:
            m = extract_materials_and_topics(text)
            out["materials_shared"] = m.get("materials_shared") or []
            out["samples_distributed"] = m.get("samples_distributed") or []
            out["topics_discussed"] = m.get("topics_discussed")
        except Exception as e:
            _log(f"extract_materials_and_topics error: {repr(e)}")

        try:
            out["summary"] = summarize_interaction(text).get("summary")
        except Exception as e:
            _log(f"summarize_interaction error: {repr(e)}")
            out["summary"] = text[:200]

        _log("DEBUG extracted: " + json.dumps(out, default=str))
        return out
    except Exception as e:
        _log(f"run_extraction FATAL (shouldn't happen): {repr(e)}")
        # return minimal fallback
        return {
            "hcp_name": None, "date": None, "time": None,
            "topics_discussed": None, "materials_shared": [], "samples_distributed": [],
            "sentiment": None, "sentiment_source": None, "summary": text[:200]
        }

# ---------------------------
# Dispatcher
# ---------------------------
def dispatch_tool(tool_name, *args, **kwargs):
    mapping = {
        "hcp_name": extract_hcp_name,
        "date": extract_date,
        "time": extract_time,
        "sentiment": extract_sentiment,
        "materials": extract_materials_and_topics,
        "materials_and_topics": extract_materials_and_topics,
        "summary": summarize_interaction,
    }
    fn = mapping.get(tool_name)
    if not fn:
        raise ValueError(f"Unknown tool: {tool_name}")
    return fn(*args, **kwargs)

# ---------------------------
# Self-test helper (call from python -m)
# ---------------------------
def self_test(sample_text=None):
    sample = sample_text or "Met Dr. Smith on 12th Jan 2025 at 2 pm, discussed Product-X efficacy, positive sentiment, shared brochure and 5 samples."
    _log("Running self_test")
    _log("ENV: GROQ_API_URL present: " + str(bool(GROQ_API_URL)) + ", KEY present: " + str(bool(GROQ_API_KEY)))
    resp = groq_call([{"role":"system","content":"Ping"},{"role":"user","content":"Hello"}])
    _log("groq_call ping result: " + str(resp)[:1000])
    extracted = run_extraction(sample)
    _log("self_test extracted: " + json.dumps(extracted, default=str))
    return {"groq_ping": bool(resp), "extracted": extracted}
