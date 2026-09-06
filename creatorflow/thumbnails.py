"""Generates thumbnail headline/on-image-text variants from the transcript's
strongest keywords, using proven short-copy patterns (numbers, contrast,
curiosity gaps) rather than a text-to-image model — cheap, fast, and the actual
bottleneck for most creators is words, not pixels.
"""
from __future__ import annotations

from .seo import extract_keywords

PATTERNS = [
    "I Was WRONG About {kw}",
    "{kw}: The Untold Story",
    "STOP Doing {kw} Like This",
    "{kw} Changed Everything",
    "The {kw} Nobody Talks About",
    "{kw} in 60 Seconds",
]


def generate_thumbnail_ideas(transcript: str, count: int = 6) -> list[dict]:
    keywords = extract_keywords(transcript, top_n=count) or ["This"]
    ideas = []
    for i in range(count):
        kw = keywords[i % len(keywords)].title()
        pattern = PATTERNS[i % len(PATTERNS)]
        headline = pattern.format(kw=kw)
        ideas.append(
            {
                "headline": headline,
                "on_image_text": headline.upper()[:24],
                "suggested_focus_keyword": kw,
            }
        )
    return ideas
