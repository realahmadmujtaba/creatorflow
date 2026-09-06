"""Turn a plain-text transcript into timed captions (SRT/VTT) without needing
audio, a forced-aligner, or any paid API. Timing is estimated from a configurable
speaking rate, which is the same approach creators use when they don't have
word-level timestamps from their editor yet.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

DEFAULT_WPM = 150  # average spoken words-per-minute
MAX_CHARS_PER_LINE = 42  # standard subtitle readability guideline


@dataclass
class CaptionCue:
    index: int
    start: float  # seconds
    end: float  # seconds
    text: str


def _split_into_sentences(transcript: str) -> list[str]:
    text = re.sub(r"\s+", " ", transcript).strip()
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s for s in sentences if s]


def _chunk_sentence(sentence: str, max_chars: int = MAX_CHARS_PER_LINE) -> list[str]:
    words = sentence.split()
    chunks, current = [], []
    for word in words:
        candidate = " ".join(current + [word])
        if len(candidate) > max_chars and current:
            chunks.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        chunks.append(" ".join(current))
    return chunks


def generate_cues(transcript: str, wpm: int = DEFAULT_WPM) -> list[CaptionCue]:
    """Build timed caption cues from raw transcript text."""
    seconds_per_word = 60.0 / wpm
    cues: list[CaptionCue] = []
    clock = 0.0
    index = 1
    for sentence in _split_into_sentences(transcript):
        for chunk in _chunk_sentence(sentence):
            word_count = max(len(chunk.split()), 1)
            duration = max(word_count * seconds_per_word, 1.2)  # min 1.2s/line
            cues.append(CaptionCue(index=index, start=clock, end=clock + duration, text=chunk))
            clock += duration
            index += 1
    return cues


def _format_timestamp_srt(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _format_timestamp_vtt(seconds: float) -> str:
    return _format_timestamp_srt(seconds).replace(",", ".")


def to_srt(cues: list[CaptionCue]) -> str:
    lines = []
    for cue in cues:
        lines.append(str(cue.index))
        lines.append(f"{_format_timestamp_srt(cue.start)} --> {_format_timestamp_srt(cue.end)}")
        lines.append(cue.text)
        lines.append("")
    return "\n".join(lines)


def to_vtt(cues: list[CaptionCue]) -> str:
    lines = ["WEBVTT", ""]
    for cue in cues:
        lines.append(f"{_format_timestamp_vtt(cue.start)} --> {_format_timestamp_vtt(cue.end)}")
        lines.append(cue.text)
        lines.append("")
    return "\n".join(lines)
