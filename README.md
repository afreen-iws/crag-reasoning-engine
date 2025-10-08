# CRAG Reasoning Engine

A Counterfactual Retrieval-Augmented Reasoning system for biomedical questions.

**What’s new / why it matters**
- Live PubMed retrieval (no static dataset)
- Per-study summarization + polarity (pro/contra/mixed/unclear)
- Counterfactual reasoning (remove studies → recompute)
- **Evidence Stability Metric (ESM)** to quantify robustness
- Cross-model comparison (**Anthropic Claude** and **Google Gemini** only)

**Starter question:**  
> Does melatonin improve quality of life of cancer patients?

## Quick start (Colab)
1. Clone repo, install `requirements.txt`
2. Set `NCBI_EMAIL` and provider API keys (Anthropic/Gemini)
3. Run pipeline: retrieval → summarize/classify → synthesize → ESM → Trust Card

> Impact: This project turns AI from a summarizer into a scientific reasoner—testing its own conclusions for stability and reporting transparent, citation-grounded answers.
