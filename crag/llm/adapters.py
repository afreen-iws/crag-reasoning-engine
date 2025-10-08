"""
CRAG LLM adapters — Anthropic (Claude) and Google (Gemini) ONLY.
Set env vars in Colab before use:
  os.environ["ANTHROPIC_API_KEY"] = "..."
  os.environ["GOOGLE_API_KEY"]   = "..."
"""

import os, json, re
from typing import Dict, List

BASE_SYS = (
  "You are a biomedical evidence analyst. Read abstracts and produce: "
  "(1) a 2-4 sentence summary focused on quality-of-life outcomes, "
  "(2) a label: pro/contra/mixed/unclear with a brief justification, "
  "(3) a short bullet list of concrete outcomes (sleep, fatigue, depression, global QoL). "
  "Be cautious and avoid overclaiming."
)

PROMPT = """QUESTION: {question}

STUDY SNIPPETS (title + abstract):
{snippets}

TASK:
1) Summary (2–4 sentences) focused on QoL outcomes only.
2) Label (one of: pro, contra, mixed, unclear) with a brief justification.
3) 2–4 bullets with concrete outcome mentions (sleep, fatigue, depression, global QoL, etc.).
Answer in JSON with keys: summary, label, bullets.
"""

def _render_snippets(rows: List[Dict], max_chars: int = 6000) -> str:
    parts, total = [], 0
    for r in rows:
        title = (r.get("title") or "").strip()
        abstract = (r.get("abstract") or "").strip()
        block = f"- {title}\n  {abstract}\n"
        total += len(block)
        if total > max_chars: break
        parts.append(block)
    return "\n".join(parts)

def _extract_json(text: str) -> Dict:
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        return {"raw": text}
    try:
        return json.loads(m.group(0))
    except Exception:
        return {"raw": text}

# ---------- Anthropic (Claude) ----------
def run_anthropic_snippet(question: str, rows: List[Dict], model: str = "claude-3-5-sonnet-latest") -> Dict:
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return {"error": "ANTHROPIC_API_KEY not set"}
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key)
        content = PROMPT.format(question=question, snippets=_render_snippets(rows))
        resp = client.messages.create(
            model=model,
            max_tokens=1000,
            temperature=0.2,
            system=BASE_SYS,
            messages=[{"role": "user", "content": content}],
        )
        text = "".join(getattr(b, "text", "") for b in resp.content)
        return _extract_json(text)
    except Exception as e:
        return {"error": str(e)}

# ---------- Google (Gemini) ----------
def run_gemini_snippet(question: str, rows: List[Dict], model: str = "gemini-1.5-flash") -> Dict:
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        return {"error": "GOOGLE_API_KEY not set"}
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        m = genai.GenerativeModel(model_name=model, system_instruction=BASE_SYS)
        prompt = PROMPT.format(question=question, snippets=_render_snippets(rows))
        resp = m.generate_content(prompt)
        text = getattr(resp, "text", "") or ""
        return _extract_json(text)
    except Exception as e:
        return {"error": str(e)}
