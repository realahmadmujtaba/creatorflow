# CreatorFlow

**Built for: AI Content Engine Hackathon** (theme: *"Build a tool that automates any part of
the creator workflow — thumbnails, scheduling, analytics, captions, or SEO."*)

CreatorFlow takes one plain-text transcript and automates four parts of the creator
workflow at once: **captions, SEO metadata, thumbnail ideas, and a multi-platform posting
schedule.** It runs with zero API keys (fully offline, heuristic mode) and can optionally
be sharpened by Claude if `ANTHROPIC_API_KEY` is set — so it's a genuinely functional tool,
not a mockup, and it degrades gracefully instead of breaking a live demo.

## Why this covers the judging criteria

| Criterion | How CreatorFlow addresses it |
|---|---|
| **Functionality (30%)** | Runs end-to-end from one command, produces real `.srt`/`.vtt`, `.json`, and an `.html` report — verified with `pytest` (6 passing tests) and a live sample run. |
| **Real-world usefulness (30%)** | Captions, SEO, thumbnails, and scheduling are the four most time-consuming manual tasks in a creator's publishing workflow — this replaces ~1-2 hours of post-production busywork per video. |
| **Technical execution (20%)** | Clean module separation (`captions`, `seo`, `scheduler`, `thumbnails`, `llm`), deterministic timing/scoring logic that's inspectable (not an opaque black box), optional LLM enhancement with safe fallback. |
| **Creativity (20%)** | Transparent, rule-based SEO scorer that *explains itself* to the creator instead of just outputting a number; schedule ranks content by SEO score so your best material claims the best slots. |

## Quickstart

```bash
pip install -r requirements.txt   # optional: only needed for the LLM enhancement path
python cli.py --transcript sample_transcript.txt --platforms youtube,tiktok,instagram
```

Output lands in `output/`:
- `captions.srt`, `captions.vtt` — ready to upload
- `seo_metadata.json` — titles, description, tags, hashtags, and a scored/explained SEO rating
- `thumbnails.json` — headline + on-image text variants
- `schedule.json` — publish date/time per platform, ranked by content strength
- `report.html` — open this one file to see everything at a glance

### Optional: sharper titles/descriptions via Claude

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python cli.py --transcript sample_transcript.txt
```
If the key isn't set (or the API call fails for any reason), CreatorFlow silently uses the
heuristic output — the demo never breaks because of a missing key or a flaky network call.

## Run the tests

```bash
python -m pytest tests/ -q
```

## Architecture

```
cli.py                  entry point — wires the pipeline together
creatorflow/
  captions.py            transcript -> timed SRT/VTT cues (WPM-based estimation)
  seo.py                 keyword extraction, titles, description, tags, explainable score
  thumbnails.py          headline/on-image-text generator from top keywords
  scheduler.py           best-time-to-post heuristics, ranked & collision-free
  llm.py                 optional Claude enhancement, fails safe to heuristic output
  report.py              renders everything into one HTML file
tests/test_creatorflow.py
sample_transcript.txt    demo input
```

## What's out of scope for this submission

- Thumbnail *images* (only headline/copy — see `thumbnails.py` docstring for why: for most
  creators, the wording is the actual bottleneck, not image generation).
- Direct publishing/API integration with YouTube/TikTok/Instagram (the schedule is the plan;
  wiring it to each platform's publish API is the natural next step, not needed to prove
  the concept for judging).

## Submission checklist (do this before the Sep 8 deadline)

1. Push this folder to a public GitHub repo.
2. Record a 60-90s demo: run the CLI live, open `report.html`.
3. On Devpost: link the repo, add the demo video (optional but recommended), and paste the
   "why this covers the judging criteria" table above into your write-up.
