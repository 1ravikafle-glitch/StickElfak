# ARCHITECTURE.md

Read this before writing or changing any code. Its job is to stop the build
from drifting — every module below has ONE responsibility and a fixed
interface; if a change doesn't fit within one module's contract, that's a
signal to stop and update this doc first, not to quietly spread logic across
files.

## 1. Data flow (pipeline)

```
topic (str) + script.txt
        │
        ▼
script_parser.py  ──►  list[Beat]
        │
        ▼
tts_engine.py  ──►  AudioResult (voiceover + per-beat word timestamps)
        │
        ├──► caption_sync.py     ──► list[CaptionFrame]
        ├──► visual_selector.py  ──► list[VisualAssignment]   (inset boxes)
        └──► avatar_renderer.py  ──► list[AvatarClip]         (character layer)
                        │
                        ▼
                compositor.py  ──►  final .mp4
                        │
                        ▼  (if --publish yes)
                publish_manager.py
                   ├──► youtube_publisher.py
                   ├──► facebook_publisher.py
                   └──► tiktok_publisher.py
```

`job_runner.py` is the only module that calls more than one pipeline
sibling. Every arrow above is a plain-data handoff (dataclasses / paths /
primitives) — no module reaches backward into an earlier stage's internals.

## 2. Module responsibility table

| Module | Owns | Never touches |
|---|---|---|
| `script_parser.py` | Splitting raw script text into `Beat`s | audio, visuals, rendering |
| `tts_engine.py` | Voiceover synthesis + word timestamps | captions, visuals, rendering |
| `caption_sync.py` | Caption timing/highlight data | drawing pixels, audio |
| `visual_selector.py` | Which inset image/clip per beat | the character layer, rendering |
| `avatar_renderer.py` | The character/avatar layer (static or talking) | inset visuals, captions |
| `compositor.py` | All FFmpeg/rendering, the only place layers are drawn | any decision-making about content |
| `job_runner.py` | Orchestration + stage sequencing + resumability calls | doing the work itself |
| `publish_manager.py` | Fan-out to platform publishers, isolating failures | rendering, credentials storage format |
| `youtube_publisher.py` / `facebook_publisher.py` / `tiktok_publisher.py` | One platform's upload API only | any other platform |
| `utils/job_state.py` | Per-job stage checkpointing (JSON) | pipeline logic |
| `utils/logger.py` | Shared logging config | pipeline logic |

## 3. Style constants (v1 pins these — change here, not ad hoc in code)

- Resolution: 1080×1920 (9:16), 30 fps, target ≤ 60s.
- Background: looping crumpled-paper texture (`assets/backgrounds/`).
- Caption: bold display font, white text, one emphasis word per beat in
  accent color `#2FD9E8` (cyan), black outline.
- Inset visuals: top of frame, labeled boxes (rounded corners, white bold
  label), one or two per beat max.
- Character: bottom-anchored, default static pose; talking/lip-synced mode
  is opt-in per beat only (`Beat.visual_hint == "[AVATAR]"`), not global.

## 4. Resumability

Every stage writes its output under `jobs/<job_id>/` and calls
`utils.job_state.mark_stage_done(job_id, stage, data)` immediately after
finishing. `job_runner.run_job` checks `get_job_status(job_id)` at the top
of each stage and skips stages already marked done — so a crash after
rendering doesn't force re-synthesizing the voiceover.

Stage order: `parsed → tts → captions → visuals → avatar → rendered → published`

## 5. Scope lock — v1

**In scope:**
- Single-topic, single-script, single-video-per-run CLI tool.
- The six pipeline modules + three publishers, exactly as tabled above.
- CPU-only rendering path as the default.

**Explicitly out of scope for v1 (do not add without updating this file first):**
- Automatic script/topic generation, trend research, or scheduling/queueing.
- Multi-language batch runs or multi-account fan-out.
- Any paid generation API as a *required* dependency — paid options may be
  added later as an optional fallback, never as the only path.
- Talking/lip-synced avatar mode (still a stub — v1 ships static-character
  mode only; see `avatar_renderer.py`).

**Scope amendment (post-v1-draft):** a local web frontend was added on
purpose — `app.py` (Flask) + `static/index.html`, serving one job API
(`/api/generate`, `/api/status/<id>`, `/api/download/<id>`) backed by an
in-memory job registry. This is intentionally NOT a dashboard/scheduler —
it's a thin single-user local UI over the same `job_runner.run_job()` the
CLI calls. If it grows multi-user auth, a database, or a queue, that's
drift — come back to this file first.

If a task during the build seems to require crossing one of these lines,
that's the cue to pause and revisit this document with the person, not to
extend a module's contract quietly.

## 6. What's actually implemented (v1, shipped)

- `script_parser.py`: parses `A:`/`B:`-prefixed script lines into Beats.
- `tts_engine.py`: pyttsx3/espeak-ng offline TTS, per-beat wav + duration.
- `caption_sync.py`: beat timing + highlight word, driven off TTS durations.
- `visual_selector.py`: generates the two comparison inset cards with PIL,
  tracks which are visible (cumulative) per beat.
- `avatar_renderer.py`: static-mode only — one PIL-drawn character reused
  across all beats. Talking mode is still `NotImplementedError`.
- `compositor.py`: renders one full PNG frame per beat, then ffmpeg
  concat-demuxes the frames + audio into the final mp4.
- `app.py` + `static/index.html`: local Flask UI, tested end-to-end at
  `http://127.0.0.1:5000`.

## 7. Known open decisions (next iteration)

- Swap pyttsx3 for a better-sounding TTS (e.g. IndexTTS-2-CPU) — contract
  in `tts_engine.py` shouldn't need to change.
- Real stock/AI imagery for inset cards instead of the plain PIL cards.
- Talking-avatar (lip-sync) mode, if wanted — `avatar_renderer.py` has the
  contract stubbed for it already.
- Word-level caption timing is currently approximated by even split within
  each beat's audio duration, not true phoneme-level timestamps.
