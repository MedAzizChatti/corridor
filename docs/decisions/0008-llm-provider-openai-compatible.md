# 0008. LLM access through one OpenAI-compatible adapter

- **Date:** 2026-11-16
- **Status:** Accepted

## Context
The LLM budget is zero. Free tiers have rate limits, weaker tool calling, and terms that change without notice. OpenRouter, Groq, Gemini and Ollama all expose an OpenAI-compatible chat and tool-calling API.

## Decision
- A single adapter built on the official `openai` SDK. The provider is chosen by config (`LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY`).
- **Default gateway: OpenRouter.** One key gives many models, and free `:free` models for development and demos. If money is ever added, spend it on one-off eval benchmark runs against stronger models (a "ceiling score"), never on development.
- **Groq** is a direct alternative where latency matters (live demo). **Ollama** is for offline development.
- A `ScriptedModel` fake returns pre-written responses, so harness tests run with no network, no cost and no flakiness.
- Production models are chosen by eval results, not by opinion.

## Alternatives considered
- **One adapter per provider** — duplicated code for an identical API.
- **LiteLLM** — a large dependency supporting 100+ providers, when we need 2–3 that all speak the same API.
- **Hugging Face Inference as the main LLM** — the free credits are small. Hugging Face is used for other things instead (see Consequences).

## Consequences
- Switching models is a config change, so comparing models with evals is cheap.
- Free models can disappear or change. Pin model IDs in config and record changes in the journal.
- Free endpoints may log prompts or use them for training: **fictional demo data only, never real client data.**
- Hugging Face roles: possible free hosting (Docker Space), publishing the eval dataset publicly, and local embedding models if we ever need them.
- To verify on day 1: current OpenRouter free-model limits, Gemini availability from Tunisia, Groq rate limits. Write the real numbers in the journal.
