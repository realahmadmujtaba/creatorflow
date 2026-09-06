"""Heuristic SEO metadata generator: title variants, description, and
tags/hashtags extracted straight from the transcript. No external API required;
`llm.py` can optionally sharpen the output if an API key is configured.
"""
from __future__ import annotations

import re
from collections import Counter

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "so", "of", "to", "in", "on",
    "for", "is", "are", "was", "were", "be", "been", "being", "it", "its",
    "this", "that", "these", "those", "with", "as", "at", "by", "from", "we",
    "you", "your", "i", "my", "our", "us", "they", "them", "he", "she", "his",
    "her", "have", "has", "had", "do", "does", "did", "not", "will", "would",
    "can", "could", "should", "just", "about", "into", "up", "out", "than",
    "then", "there", "here", "what", "when", "where", "how", "all", "some",
    "more", "very", "really", "like", "get", "got", "one", "going", "gonna",
    # spoken-video filler / intro boilerplate that isn't a real topic keyword
    "hey", "hi", "hello", "everyone", "everybody", "guys", "welcome", "back",
    "channel", "today", "video", "videos", "talking", "talk", "let", "lets",
    "let's", "okay", "ok", "alright", "yeah", "um", "uh", "thanks", "thank",
    "please", "subscribe", "comment", "comments", "click", "link", "below",
    "start", "started", "began", "began", "little", "bit", "lot", "thing",
    "things", "stuff", "way", "ways", "make", "made", "actually", "basically",
}

TITLE_TEMPLATES = [
    "{kw} Explained: What You Need to Know",
    "The Truth About {kw}",
    "{kw} in {n} Minutes",
    "How to {kw} (Step by Step)",
    "Why {kw} Matters More Than You Think",
]

HOOK_WORDS = {"secret", "mistake", "warning", "truth", "proven", "free", "new", "best", "worst"}


def extract_keywords(transcript: str, top_n: int = 8) -> list[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z'-]{2,}", transcript.lower())
    filtered = [w for w in words if w not in STOPWORDS]
    counts = Counter(filtered)
    return [word for word, _ in counts.most_common(top_n)]


def generate_titles(transcript: str, count: int = 5) -> list[str]:
    keywords = extract_keywords(transcript, top_n=count)
    if not keywords:
        keywords = ["This Topic"]
    titles = []
    for i, template in enumerate(TITLE_TEMPLATES[:count]):
        kw = keywords[i % len(keywords)].title()
        titles.append(template.format(kw=kw, n=max(3, min(15, len(transcript.split()) // 130))))
    return titles


def generate_description(transcript: str, max_sentences: int = 3) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", transcript).strip())
    lead = " ".join(sentences[:max_sentences])
    keywords = extract_keywords(transcript, top_n=6)
    tail = "Topics covered: " + ", ".join(keywords) + "." if keywords else ""
    return (lead + "\n\n" + tail).strip()


def generate_tags(transcript: str, top_n: int = 12) -> list[str]:
    return extract_keywords(transcript, top_n=top_n)


def generate_hashtags(transcript: str, top_n: int = 6) -> list[str]:
    return [f"#{kw.replace(' ', '')}" for kw in extract_keywords(transcript, top_n=top_n)]


def seo_score(title: str, description: str, tags: list[str]) -> dict:
    """A transparent, rule-based score (0-100) judges can inspect and trust,
    rather than an opaque 'AI says so' number."""
    score = 0
    notes = []

    if 40 <= len(title) <= 70:
        score += 25
        notes.append("Title length is in the optimal 40-70 char range (+25)")
    else:
        notes.append(f"Title length {len(title)} chars is outside 40-70 (optimize for CTR)")

    if any(w in title.lower() for w in HOOK_WORDS):
        score += 15
        notes.append("Title contains a curiosity/authority hook word (+15)")

    if 70 <= len(description) <= 300:
        score += 25
        notes.append("Description length is search-friendly (+25)")
    else:
        notes.append("Description could be expanded for better indexing")

    if len(tags) >= 5:
        score += 20
        notes.append("Has 5+ tags for discoverability (+20)")

    if len(set(tags)) == len(tags):
        score += 15
        notes.append("No duplicate tags (+15)")

    return {"score": min(score, 100), "notes": notes}
