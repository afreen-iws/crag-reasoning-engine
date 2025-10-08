"""
Open-source LLM adapter (no paid API).
Default model: Qwen/Qwen2.5-1.5B-Instruct
Requires: transformers, accelerate, bitsandbytes (installed already).
"""

from typing import Dict, List
import re, json, torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

BASE_INSTRUCTION = (
  "You are a biomedical evidence analyst. Read abstracts and produce: "
  "(1) a 2-4 sentence summary focused on quality-of-life outcomes, "
  "(2) a label: pro/contra/mixed/unclear with a brief justification, "
  "(3) 2–4 bullets with concrete outcomes (sleep, fatigue, depression, global QoL). "
  "Be cautious and avoid overclaiming. Respond in JSON with keys: summary, label, bullets."
)

PROMPT_TEMPLATE = """QUESTION: {question}

STUDY SNIPPETS (title + abstract):
{snippets}

TASK:
1) Summary (2–4 sentences) focused on QoL outcomes only.
2) Label (one of: pro, contra, mixed, unclear) with a brief justification.
3) 2–4 bullets with concrete outcome mentions (sleep, fatigue, depression, global QoL, etc.).
Return only JSON with keys: summary, label, bullets.
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

def _load_pipeline(model_id: str):
    has_cuda = torch.cuda.is_available()
    kwargs = {}
    if has_cuda:
        # Prefer 4-bit quant for speed/memory
        try:
            kwargs.update(dict(
                device_map="auto",
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
            ))
        except Exception:
            kwargs.update(dict(device_map="auto", torch_dtype=torch.bfloat16))
    else:
        # CPU fallback (may be slow)
        kwargs.update(dict(torch_dtype=torch.float32))
    tok = AutoTokenizer.from_pretrained(model_id, use_fast=True)
    mdl = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True, **kwargs)
    return pipeline(
        "text-generation",
        model=mdl,
        tokenizer=tok,
    )

def run_hf_snippet(
    question: str,
    rows: List[Dict],
    model_id: str = "Qwen/Qwen2.5-1.5B-Instruct",
    max_new_tokens: int = 512,
    temperature: float = 0.2,
) -> Dict:
    try:
        pipe = _load_pipeline(model_id)
        prompt = PROMPT_TEMPLATE.format(question=question, snippets=_render_snippets(rows))

        # Try to use chat template if available (Qwen supports chat format)
        try:
            tokenizer = pipe.tokenizer
            if hasattr(tokenizer, "apply_chat_template"):
                messages = [
                    {"role": "system", "content": BASE_INSTRUCTION},
                    {"role": "user", "content": prompt},
                ]
                full_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            else:
                full_prompt = BASE_INSTRUCTION + "\n\n" + prompt
        except Exception:
            full_prompt = BASE_INSTRUCTION + "\n\n" + prompt

        out = pipe(
            full_prompt,
            do_sample=False if temperature == 0 else True,
            temperature=temperature,
            max_new_tokens=max_new_tokens,
            truncation=True,
            eos_token_id=pipe.tokenizer.eos_token_id,
        )[0]["generated_text"]

        # Extract only the assistant continuation if chat template duplicated prompt
        if out.startswith(full_prompt):
            out = out[len(full_prompt):].strip()

        parsed = _extract_json(out)
        parsed["_model"] = model_id
        return parsed
    except Exception as e:
        return {"error": str(e), "_model": model_id}
