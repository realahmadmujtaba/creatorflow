"""Optional LLM enhancement layer. Every feature in CreatorFlow already works
with zero API keys (heuristic mode) so the tool is demoable offline for judges.
If ANTHROPIC_API_KEY is set, titles/descriptions get sharpened by Claude.
Never raises: any failure (missing key, no package, network error) silently
falls back to the heuristic output so the demo never breaks.
"""
from __future__ import annotations

import os


def is_available() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def sharpen_titles(transcript: str, draft_titles: list[str]) -> list[str]:
    if not is_available():
        return draft_titles
    try:
        import anthropic  # type: ignore

        client = anthropic.Anthropic()
        prompt = (
            "Rewrite these video title drafts to be punchier and more clickable, "
            "keeping them accurate to the transcript. Return exactly "
            f"{len(draft_titles)} lines, one title per line, no numbering.\n\n"
            f"Transcript excerpt:\n{transcript[:1500]}\n\n"
            f"Draft titles:\n" + "\n".join(draft_titles)
        )
        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        lines = [line.strip("- ").strip() for line in text.splitlines() if line.strip()]
        return lines[: len(draft_titles)] or draft_titles
    except Exception:
        return draft_titles


def sharpen_description(transcript: str, draft_description: str) -> str:
    if not is_available():
        return draft_description
    try:
        import anthropic  # type: ignore

        client = anthropic.Anthropic()
        prompt = (
            "Rewrite this video description to be more engaging and SEO-friendly "
            "in 2-3 short paragraphs, staying accurate to the transcript.\n\n"
            f"Transcript excerpt:\n{transcript[:1500]}\n\n"
            f"Draft description:\n{draft_description}"
        )
        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip() or draft_description
    except Exception:
        return draft_description
