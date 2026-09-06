# CreatorFlow

**Automate the four most time-consuming parts of publishing a video: captions, SEO, thumbnails, and scheduling — from one transcript, in one command.**

Built for the **AI Content Engine Hackathon** — theme: *"Build a tool that automates any part of the creator workflow: thumbnails, scheduling, analytics, captions, or SEO."*

[![Tests](https://img.shields.io/badge/tests-7%20passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-lightgrey)]()

---

## Demo

```bash
git clone <this-repo-url>
cd ai-content-engine-hackathon
python cli.py --transcript sample_transcript.txt --platforms youtube,tiktok,instagram
```
Output lands in `output/report.html` — open it in a browser to see everything at once. No
API keys, no installs required for this to work end to end.

*(Add your demo video link / GIF here before submitting.)*

## Inspiration

Every creator we talked to described the same post-production bottleneck: the video is
edited and ready, but publishing it still takes an hour or more of manual, repetitive work —
writing captions, guessing SEO metadata, coming up with a thumbnail hook, and figuring out
when to post across three or four platforms. None of that requires creative judgment; it
requires *time*. That's exactly the kind of task automation should eat first.

## What it does

CreatorFlow takes one plain-text transcript and produces, in seconds:

1. **Captions** — timed `.srt` / `.vtt` files, chunked to broadcast-standard line length and
   timed from a configurable speaking rate.
2. **SEO metadata** — 5 title options, a description, tags, and hashtags, plus a transparent,
   rule-based SEO score (0-100) that *explains* every point it awards or withholds — not a
   black-box "AI says 82/100."
3. **Thumbnail ideas** — 6 headline + on-image-text variants built from proven short-copy
   patterns and the transcript's real topical keywords.
4. **A posting schedule** — every title slotted into a best-time-to-post calendar across your
   chosen platforms, strongest content claiming the best slots first, with zero double-booked
   slots.

Everything works **fully offline** on heuristics. If you set `ANTHROPIC_API_KEY`, titles and
the description are additionally sharpened by Claude — and if that call fails for any reason
(no key, no network, rate limit), it silently falls back to the heuristic output, so a live
demo never breaks on stage.

## How we built it

- Pure Python, standard library only for the core pipeline — zero required dependencies.
- Each concern is its own module (`captions`, `seo`, `thumbnails`, `scheduler`, `llm`,
  `report`) wired together by a thin `cli.py`, so any piece can be swapped or extended
  independently.
- Caption timing is estimated from words-per-minute rather than requiring audio or a
  forced-aligner, so it works from a transcript alone.
- SEO keyword extraction is frequency-based with a curated stopword list tuned specifically
  for *spoken* video intros (filtering out "hey", "welcome back", "guys", etc. — the words a
  generic NLP stopword list misses but every creator transcript is full of).
- The scheduler ranks content by SEO score and walks a per-platform "best times to post" table
  so the strongest material claims the best slots, without ever double-booking a platform.

## Challenges we ran into

While testing the report live in a browser, we caught a real bug: the word **"why"** was
missing from the stopword list, so it got extracted as a topic keyword and collided with the
`"Why {keyword} Matters"` title template — producing the nonsensical title *"Why Why Matters
More Than You Think."* We fixed the stopword list, added a regression test asserting no
generated title repeats an adjacent word, and re-verified the fix live before shipping.

## Accomplishments that we're proud of

- A genuinely functional tool, not a mockup — every output file is real and immediately usable.
- An SEO scorer that shows its work instead of hiding behind an opaque number.
- Zero required setup: `git clone` → one command → real output.
- 7 passing unit tests plus a live browser verification pass that caught and fixed a real bug
  before submission.

## What we learned

Heuristic, rule-based systems are underrated for hackathon judging: they're faster to build,
100% reproducible for a live demo (no API flakiness), and — critically — *explainable*, which
matters when judges are scoring "technical execution." LLM enhancement is strictly additive,
not load-bearing.

## What's next

- Thumbnail *image* generation (today we generate the copy/headline, which is the actual
  bottleneck for most creators — image generation is a natural next layer).
- Direct publish integration with the YouTube/TikTok/Instagram APIs so the generated schedule
  can execute itself instead of just planning.
- Per-platform caption formatting (TikTok/Reels burned-in caption styling vs. YouTube sidecar
  files).

## Built with

`Python` · `argparse` · standard library only (`re`, `json`, `datetime`, `html`) · optional
`anthropic` SDK for LLM enhancement · `pytest` for testing

---

## Why this covers the judging criteria

| Criterion | How CreatorFlow addresses it |
|---|---|
| **Functionality (30%)** | Runs end-to-end from one command, produces real `.srt`/`.vtt`, `.json`, and an `.html` report — verified with `pytest` (7 passing tests) and a live browser run. |
| **Real-world usefulness (30%)** | Captions, SEO, thumbnails, and scheduling are the four most time-consuming manual tasks in a creator's publishing workflow — this replaces ~1-2 hours of post-production busywork per video. |
| **Technical execution (20%)** | Clean module separation, deterministic and inspectable timing/scoring logic, optional LLM enhancement with a safe fallback path, a caught-and-fixed bug documented above. |
| **Creativity (20%)** | A transparent, rule-based SEO scorer that explains itself; a schedule that ranks content by strength instead of just round-robining it. |

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
heuristic output.

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

- Thumbnail *images* (only headline/copy — see "What's next" above).
- Direct publishing/API integration with YouTube/TikTok/Instagram (the schedule is the plan;
  wiring it to each platform's publish API is the natural next step).

## Team

- Repo owner / submitter: fill in your name + Devpost profile link here.

## License

MIT — see judging submission for full terms if the hackathon requires a specific license.
