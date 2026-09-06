import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from creatorflow import captions, scheduler, seo, thumbnails
from datetime import datetime

SAMPLE = (
    "Automation saves time. Automation saves money. This video explains automation "
    "for creators who want to scale content without burning out."
)


def test_generate_cues_produces_ordered_nonoverlapping_timing():
    cues = captions.generate_cues(SAMPLE, wpm=150)
    assert len(cues) > 0
    for a, b in zip(cues, cues[1:]):
        assert a.end <= b.start + 1e-6
        assert a.index < b.index


def test_srt_and_vtt_render():
    cues = captions.generate_cues(SAMPLE)
    srt = captions.to_srt(cues)
    vtt = captions.to_vtt(cues)
    assert "-->" in srt and "," in srt  # SRT uses comma for ms
    assert vtt.startswith("WEBVTT")
    assert "." in vtt.split("\n")[2]  # VTT uses dot for ms


def test_extract_keywords_ignores_stopwords():
    keywords = seo.extract_keywords("the the the automation automation creators")
    assert "the" not in keywords
    assert "automation" in keywords


def test_seo_score_is_bounded():
    result = seo.seo_score("A Reasonably Sized Title About Automation Tools", "x" * 150, ["a", "b", "c", "d", "e"])
    assert 0 <= result["score"] <= 100


def test_generate_thumbnail_ideas_count():
    ideas = thumbnails.generate_thumbnail_ideas(SAMPLE, count=4)
    assert len(ideas) == 4
    assert all("headline" in i for i in ideas)


def test_schedule_spreads_across_platforms_without_duplicate_slots():
    items = [{"title": f"Post {i}", "score": 100 - i} for i in range(3)]
    schedule = scheduler.build_schedule(items, ["youtube", "tiktok"], start_date=datetime(2026, 9, 7))
    slots = [(s.platform, s.publish_at) for s in schedule]
    assert len(slots) == len(set(slots))  # no two posts on same platform at same time
