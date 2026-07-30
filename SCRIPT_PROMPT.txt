AICOS — SCRIPT FORMAT PROMPT
=============================

Use this prompt (paste it into any LLM, or follow it yourself) to write a
script that AICOS can render directly, no editing needed.

-----------------------------------------------------------------------
PROMPT TO USE:

Write a short-form video script comparing two things: [ITEM A] and [ITEM B].
Topic: [YOUR TOPIC HERE]

Rules:
- Output plain text, one line per beat. No numbering, no headers, no extra
  commentary — just the lines.
- Prefix every line with "A:" or "B:" to say which item that line is about.
  Use a line with no prefix only for a general intro/outro line that isn't
  about either item specifically.
- Each line should be short — 3 to 8 words, one idea per line, written the
  way it would actually be spoken out loud (not written prose).
- Introduce item A fully first (2-4 lines), then item B (2-4 lines), so the
  comparison builds one side at a time.
- End with one short line that states the actual difference or takeaway.
- Total: 6 to 10 lines. Don't add blank lines between them.

-----------------------------------------------------------------------
EXAMPLE OUTPUT (topic: Cookie vs Cache, A=Cookie, B=Cache):

A: Cookie this is
A: to remember who
A: you are on a site
B: Cache this is
B: to remember what a
B: website looked like
B: so it just loads pages faster

-----------------------------------------------------------------------
HOW THIS MAPS TO THE APP:

- Each line becomes one "beat": one TTS audio clip + one caption on screen.
- The first time an "A:" or "B:" line appears, that item's labeled card
  appears at the top of frame and stays visible for the rest of the video.
- Paste the topic into "Topic", the two item names into "Item A" / "Item B",
  and the whole script block into the "Script" box at http://127.0.0.1:5000
