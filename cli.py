#!/usr/bin/env python3
"""CreatorFlow CLI.

Usage:
    python cli.py --transcript sample_transcript.txt --platforms youtube,tiktok,instagram

Reads a plain-text transcript and writes, into --out-dir (default: output/):
    captions.srt, captions.vtt, seo_metadata.json, schedule.json,
    thumbnails.json, report.html

No API key required. Set ANTHROPIC_API_KEY to sharpen titles/description with Claude.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime

from creatorflow import captions, llm, report, scheduler, seo, thumbnails


def main() -> None:
    parser = argparse.ArgumentParser(description="Automate captions, SEO, schedule, and thumbnails.")
    parser.add_argument("--transcript", required=True, help="Path to a plain-text transcript file")
    parser.add_argument("--platforms", default="youtube,tiktok,instagram",
                         help="Comma-separated platforms to schedule for")
    parser.add_argument("--wpm", type=int, default=150, help="Speaking rate for caption timing")
    parser.add_argument("--out-dir", default="output", help="Directory to write output files")
    args = parser.parse_args()

    with open(args.transcript, "r", encoding="utf-8") as f:
        transcript = f.read()

    os.makedirs(args.out_dir, exist_ok=True)
    platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]

    # 1. Captions
    cues = captions.generate_cues(transcript, wpm=args.wpm)
    srt_text = captions.to_srt(cues)
    vtt_text = captions.to_vtt(cues)
    with open(os.path.join(args.out_dir, "captions.srt"), "w", encoding="utf-8") as f:
        f.write(srt_text)
    with open(os.path.join(args.out_dir, "captions.vtt"), "w", encoding="utf-8") as f:
        f.write(vtt_text)

    # 2. SEO metadata (heuristic, then optionally LLM-sharpened)
    titles = seo.generate_titles(transcript)
    titles = llm.sharpen_titles(transcript, titles)
    description = seo.generate_description(transcript)
    description = llm.sharpen_description(transcript, description)
    tags = seo.generate_tags(transcript)
    hashtags = seo.generate_hashtags(transcript)
    seo_meta = {"titles": titles, "description": description, "tags": tags, "hashtags": hashtags}
    seo_eval = seo.seo_score(titles[0] if titles else "", description, tags)
    with open(os.path.join(args.out_dir, "seo_metadata.json"), "w", encoding="utf-8") as f:
        json.dump({**seo_meta, "score": seo_eval}, f, indent=2)

    # 3. Thumbnails
    thumb_ideas = thumbnails.generate_thumbnail_ideas(transcript)
    with open(os.path.join(args.out_dir, "thumbnails.json"), "w", encoding="utf-8") as f:
        json.dump(thumb_ideas, f, indent=2)

    # 4. Schedule (one "content item" per platform-worthy title, ranked by SEO score)
    items = [{"title": t, "score": seo_eval["score"]} for t in titles]
    schedule = scheduler.build_schedule(items, platforms, start_date=datetime.now())
    schedule_dicts = scheduler.schedule_to_dicts(schedule)
    with open(os.path.join(args.out_dir, "schedule.json"), "w", encoding="utf-8") as f:
        json.dump(schedule_dicts, f, indent=2)

    # 5. HTML report
    html_report = report.render(
        titles=titles,
        seo_meta=seo_meta,
        description=description,
        seo=seo_eval,
        cues=cues,
        srt_text=srt_text,
        thumbnails=thumb_ideas,
        schedule=schedule_dicts,
    )
    report_path = os.path.join(args.out_dir, "report.html")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_report)

    print(f"Done. {len(cues)} caption cues, {len(titles)} title options, "
          f"{len(schedule_dicts)} scheduled posts.")
    print(f"Open the full report: {os.path.abspath(report_path)}")


if __name__ == "__main__":
    main()
