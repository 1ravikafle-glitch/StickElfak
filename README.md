# AICOS — AI Content Operating System

Give it a **topic + a script**. It generates a vertical (9:16) short-form
video — voiceover, animated captions, inset visuals, and a character overlay,
styled after the reference video — then auto-posts it to **YouTube Shorts**,
a **Facebook Page**, and **TikTok**.

This is a fresh v1 rebuild. See `ARCHITECTURE.md` for the module map and the
scope-lock rules that keep the build from drifting.

## What v1 does (and doesn't)

**Does:**
- Takes a topic (string) + a script (plain `.txt` file) as input — no
  auto-script-generation in v1.
- Renders one 9:16 video per run: TTS voiceover, word-synced animated
  captions, small labeled inset images/clips, and a character overlay that
  can be either a static pose or (per-beat, opt-in) a lip-synced talking clip.
- Publishes to YouTube Shorts, a Facebook Page, and TikTok via each
  platform's **official** API.
- Runs on CPU / resource-constrained hardware — no step requires a GPU or a
  paid API by default.
- Resumable: if a run crashes mid-pipeline, it picks up from the last
  completed stage instead of re-rendering everything.

**Doesn't (yet — deliberately out of scope for v1):**
- No trend research or automatic script writing.
- No scheduling/queueing system — v1 is "run it, it does one video."
- No talking/lip-synced avatar — static character overlay only for now.
- No multi-account or multi-language batch runs.
- No auth/multi-user support on the local web UI — it's a single-user local tool.

If you want any of those, that's a v2 conversation — adding them mid-build
is exactly the "drift" this structure is meant to prevent.

## Folder structure

```
aicos/
├── README.md              you are here
├── ARCHITECTURE.md         module map, data flow, scope lock — read before coding
├── requirements.txt
├── config/
│   ├── config.example.yaml   copy to config.yaml and fill in
│   └── credentials/           OAuth tokens / API keys live here (gitignored)
├── input/                     drop topic/script files here, or pass paths via CLI
├── assets/
│   ├── characters/            avatar sprite(s) — static poses
│   ├── backgrounds/            looping background texture (e.g. paper texture)
│   ├── music/                  royalty-free background tracks
│   └── fonts/                  bold caption font
├── src/
│   ├── main.py                 CLI entrypoint
│   ├── pipeline/                script → render, one module per stage
│   ├── publishing/              one module per platform + a fan-out manager
│   └── utils/                   logging, job-state/resumability
├── jobs/                       per-run working dirs (gitignored)
├── logs/
└── tests/
```

## Setup

1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. `cp config/config.example.yaml config/config.yaml` and fill in paths/IDs.
4. Drop assets into `assets/characters`, `assets/backgrounds`, `assets/music`,
   `assets/fonts` (each folder has a README noting what goes there).
5. Get platform API credentials — see below — and place them under
   `config/credentials/` as `config.yaml` expects.

## Running it — local web UI (recommended)

```bash
python app.py
```
Then open **http://127.0.0.1:5000**. Fill in Topic, Item A, Item B, and a
script (one line per beat, prefixed `A:` or `B:` to show that item's
comparison card), click **Generate video**, wait for it to render, then
preview/download the mp4 right in the page.

This has been tested end-to-end (script → TTS → captions → comparison
cards → character overlay → final mp4, served back through the browser) —
it produces a real playable 1080×1920 video with audio.

## Running it — CLI

```bash
python -m src.main run --topic "Why cookies exist" --script input/script.txt
python -m src.main run --topic "Why cookies exist" --script input/script.txt --publish yes
python -m src.main run --topic "..." --script input/script.txt --publish yes --platforms youtube facebook
```
Note: the CLI's publishing path (`--publish yes`) is still a stub — the
render pipeline is real and working, but `youtube_publisher.py` /
`facebook_publisher.py` / `tiktok_publisher.py` need the API credentials
below wired in before publishing actually runs.

## Script format (comparison videos)

```
A: Cookie this is
A: to remember who
B: Cache this is
B: to remember what a
B: website like images
B: just makes pages
```
Each line is one beat. `A:`/`B:` prefixes narrate that line and show (and
keep showing, once introduced) that item's labeled card at the top of the
frame — matching the reference video's side-by-side comparison style.
Unprefixed lines narrate with no card change.

## Getting API access (you said you don't have these yet)

None of these are instant — budget a day or two total, mostly waiting on
review queues. Do this once per platform; tokens/keys are then long-lived
or auto-refreshable.

### YouTube (YouTube Data API v3)
1. Create a project in Google Cloud Console → enable "YouTube Data API v3."
2. Create an OAuth 2.0 Client ID (type: Desktop app) → download
   `client_secret.json` into `config/credentials/`.
3. Run the one-time OAuth flow (a helper script for this belongs in
   `src/publishing/youtube_publisher.py` once built) — it opens a browser,
   you log into the YouTube channel's Google account, and it saves a
   refresh token. After that, uploads are unattended.
4. New API projects get a modest daily upload quota — fine for one
   short/day; request a quota increase later if you scale up.

### Facebook Page (Graph API)
1. Create a Meta App at developers.facebook.com (type: Business).
2. Add the Page you manage, request `pages_manage_posts` and
   `pages_read_engagement` permissions.
3. Generate a Page Access Token (via Graph API Explorer or the app's token
   tool), then exchange it for a **long-lived** token (~60 days,
   renewable) — save it to `config/credentials/facebook_page_token.txt`.
4. Personal-use apps stay in dev mode with just your own Page as a tester,
   which is enough for posting to your own Page — no app review needed for
   that use case.

### TikTok (Content Posting API)
1. Register a developer app at developers.tiktok.com, add the Content
   Posting API product.
2. Complete the OAuth flow for the target TikTok account, save the access
   token to `config/credentials/tiktok_token.txt`.
3. **Important:** a new app starts "unaudited," which limits it to posting
   as a private draft (you then tap "Post" inside the TikTok app) rather
   than direct public posting. Submit the app for audit when you're ready
   for fully unattended posting — `tiktok_publisher.py` is written to treat
   the draft outcome as success in the meantime, not an error.

## Style reference

The reference video (30s, 1080x1920, 30fps) uses: a crumpled-paper
background, one or two small labeled "inset" screenshots at the top, bold
white/cyan animated captions with one word highlighted per beat, and a
static blue-hoodie stick-figure character anchored at the bottom holding a
laptop. `ARCHITECTURE.md` pins these as the default style constants so
later work doesn't quietly change the look.
