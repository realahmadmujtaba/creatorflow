"""Auto-schedules a batch of content pieces across platforms using published
best-posting-time research, spreading items out so nothing collides and
higher-priority items (by SEO score) land on the strongest slots.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

# Illustrative "best time to post" heuristics (local time, 24h), commonly cited
# creator-economy benchmarks. Swap with a platform analytics API for real accounts.
BEST_SLOTS = {
    "youtube": [(14, 0), (17, 0), (20, 0)],
    "tiktok": [(9, 0), (12, 0), (19, 0)],
    "instagram": [(11, 0), (13, 0), (19, 30)],
    "x": [(8, 0), (12, 30), (17, 0)],
    "linkedin": [(8, 30), (10, 0), (12, 0)],
}
DEFAULT_SLOTS = [(9, 0), (13, 0), (18, 0)]


@dataclass
class ScheduledItem:
    title: str
    platform: str
    publish_at: datetime
    priority_score: int


def build_schedule(
    items: list[dict],
    platforms: list[str],
    start_date: datetime,
    days: int = 7,
) -> list[ScheduledItem]:
    """items: [{"title": str, "score": int}, ...] sorted best-first by caller
    or here by score descending, so the strongest content claims prime slots."""
    ranked = sorted(items, key=lambda i: i.get("score", 0), reverse=True)
    scheduled: list[ScheduledItem] = []

    slot_cursor = {p: 0 for p in platforms}
    day_cursor = 0

    for item in ranked:
        for platform in platforms:
            slots = BEST_SLOTS.get(platform.lower(), DEFAULT_SLOTS)
            slot_idx = slot_cursor[platform] % len(slots)
            day_offset = day_cursor + slot_cursor[platform] // len(slots)
            if day_offset >= days:
                day_offset = day_offset % days  # wrap into a repeating weekly cadence
            hour, minute = slots[slot_idx]
            publish_at = start_date + timedelta(days=day_offset)
            publish_at = publish_at.replace(hour=hour, minute=minute, second=0, microsecond=0)

            scheduled.append(
                ScheduledItem(
                    title=item["title"],
                    platform=platform,
                    publish_at=publish_at,
                    priority_score=item.get("score", 0),
                )
            )
            slot_cursor[platform] += 1
        day_cursor += 1

    return sorted(scheduled, key=lambda s: s.publish_at)


def schedule_to_dicts(schedule: list[ScheduledItem]) -> list[dict]:
    return [
        {
            "title": s.title,
            "platform": s.platform,
            "publish_at": s.publish_at.isoformat(),
            "priority_score": s.priority_score,
        }
        for s in schedule
    ]
