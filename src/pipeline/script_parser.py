"""
script_parser.py — turns (topic, item_a, item_b, script_text) into ordered Beats.

Script line format (plain text, one beat per non-empty line):
    A: Cookies remember who you are on a site.
    B: Cache remembers what a page looked like.
    A: That's why you stay logged in.
    (no prefix) -> a general beat, no inset box change.
"""

from dataclasses import dataclass, field


@dataclass
class Beat:
    index: int
    text: str
    caption: str
    item: str | None = None          # "A" | "B" | None
    highlight_word: str = ""
    emphasis_words: list = field(default_factory=list)


def _pick_highlight(text: str, item_label: str | None) -> str:
    if item_label:
        return item_label.upper()
    words = [w.strip(".,!?").upper() for w in text.split()]
    words = [w for w in words if len(w) > 3]
    return words[-1] if words else (text.split()[-1].upper() if text.split() else "")


def parse_script(topic: str, script_text: str, item_a: str = "", item_b: str = "") -> list:
    beats = []
    idx = 0
    for raw_line in script_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        item = None
        label = None
        if line[:2].upper() == "A:":
            item, label, line = "A", item_a or "A", line[2:].strip()
        elif line[:2].upper() == "B:":
            item, label, line = "B", item_b or "B", line[2:].strip()

        caption = line.upper()
        highlight = _pick_highlight(line, label)
        beats.append(Beat(index=idx, text=line, caption=caption,
                           item=item, highlight_word=highlight))
        idx += 1
    return beats
