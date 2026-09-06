"""Renders the full CreatorFlow output (captions, SEO, schedule, thumbnails)
as a single self-contained HTML report so judges can open one file and see
real, usable output without running anything.
"""
from __future__ import annotations

import html

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CreatorFlow Report</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Arial, sans-serif; max-width: 900px;
         margin: 40px auto; padding: 0 20px; color: #1a1a1a; background: #fafafa; }}
  h1 {{ font-size: 1.8rem; }}
  h2 {{ margin-top: 2.5rem; border-bottom: 2px solid #eee; padding-bottom: 6px; }}
  .card {{ background: white; border: 1px solid #e5e5e5; border-radius: 8px;
           padding: 16px 20px; margin: 10px 0; }}
  .score {{ display: inline-block; background: #16a34a; color: white; font-weight: 700;
            padding: 2px 10px; border-radius: 999px; font-size: 0.85rem; }}
  .tag {{ display: inline-block; background: #eef2ff; color: #3730a3; padding: 2px 8px;
          border-radius: 6px; margin: 2px; font-size: 0.85rem; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ text-align: left; padding: 6px 10px; border-bottom: 1px solid #eee; font-size: 0.9rem; }}
  pre {{ white-space: pre-wrap; background: #111; color: #d1fae5; padding: 12px;
         border-radius: 6px; font-size: 0.8rem; max-height: 300px; overflow: auto; }}
  .notes {{ color: #555; font-size: 0.85rem; }}
</style>
</head>
<body>
  <h1>CreatorFlow &mdash; Automated Creator Workflow Report</h1>
  <p class="notes">Generated for the AI Content Engine Hackathon. Every section below is
  real output from the transcript you provided &mdash; nothing here is a mockup.</p>

  <h2>1. SEO Metadata</h2>
  <div class="card">
    <p><strong>Recommended title:</strong> {best_title} <span class="score">SEO score: {seo_score}/100</span></p>
    <p><strong>Alternate titles:</strong></p>
    <ul>{title_alts}</ul>
    <p><strong>Description:</strong><br>{description}</p>
    <p><strong>Tags:</strong> {tags}</p>
    <p><strong>Hashtags:</strong> {hashtags}</p>
    <p class="notes">Scoring rationale: {seo_notes}</p>
  </div>

  <h2>2. Captions ({cue_count} cues, {duration_min} min estimated)</h2>
  <div class="card">
    <pre>{srt_preview}</pre>
    <p class="notes">Full .srt and .vtt files written alongside this report.</p>
  </div>

  <h2>3. Thumbnail Ideas</h2>
  <div class="card">
    <table><tr><th>Headline</th><th>On-image text</th><th>Focus keyword</th></tr>
    {thumbnail_rows}
    </table>
  </div>

  <h2>4. Posting Schedule</h2>
  <div class="card">
    <table><tr><th>When</th><th>Platform</th><th>Content</th><th>Priority</th></tr>
    {schedule_rows}
    </table>
  </div>
</body>
</html>
"""


def render(*, titles, seo_meta, description, seo, cues, srt_text, thumbnails, schedule) -> str:
    title_alts = "".join(f"<li>{html.escape(t)}</li>" for t in titles[1:])
    tags = "".join(f'<span class="tag">{html.escape(t)}</span>' for t in seo_meta["tags"])
    hashtags = " ".join(seo_meta["hashtags"])
    seo_notes = "; ".join(seo["notes"])

    duration_min = round((cues[-1].end / 60) if cues else 0, 1)
    srt_preview = "\n".join(srt_text.splitlines()[:20])

    thumb_rows = "".join(
        f"<tr><td>{html.escape(t['headline'])}</td><td>{html.escape(t['on_image_text'])}</td>"
        f"<td>{html.escape(t['suggested_focus_keyword'])}</td></tr>"
        for t in thumbnails
    )

    sched_rows = "".join(
        f"<tr><td>{s['publish_at']}</td><td>{html.escape(s['platform'])}</td>"
        f"<td>{html.escape(s['title'])}</td><td>{s['priority_score']}</td></tr>"
        for s in schedule
    )

    return TEMPLATE.format(
        best_title=html.escape(titles[0]) if titles else "",
        seo_score=seo["score"],
        title_alts=title_alts,
        description=html.escape(description).replace("\n", "<br>"),
        tags=tags,
        hashtags=html.escape(hashtags),
        seo_notes=html.escape(seo_notes),
        cue_count=len(cues),
        duration_min=duration_min,
        srt_preview=html.escape(srt_preview),
        thumbnail_rows=thumb_rows,
        schedule_rows=sched_rows,
    )
