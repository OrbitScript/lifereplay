#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║          L I F E R E P L A Y  🎞️                    ║
║     Your Terminal Time-Capsule Diary                 ║
╚══════════════════════════════════════════════════════╝

A CLI diary that tracks your mood, animates your entries,
draws mood graphs, and surprises you with past memories.
"""

import os
import sys
import json
import time
import math
import random
import shutil
import textwrap
import datetime
import argparse
import re
from pathlib import Path
from collections import defaultdict

# ─── Config ────────────────────────────────────────────
DATA_DIR = Path.home() / ".lifereplay"
ENTRIES_FILE = DATA_DIR / "entries.json"
CONFIG_FILE  = DATA_DIR / "config.json"

# ─── ANSI Colors ───────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    ITALIC  = "\033[3m"
    # Foreground
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"
    GRAY    = "\033[90m"
    # Bright
    BRED    = "\033[91m"
    BGREEN  = "\033[92m"
    BYELLOW = "\033[93m"
    BBLUE   = "\033[94m"
    BMAGENTA= "\033[95m"
    BCYAN   = "\033[96m"
    BWHITE  = "\033[97m"
    # Background
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"

def col(text, *codes):
    return "".join(codes) + str(text) + C.RESET

def supports_color():
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

# ─── Mood Engine ───────────────────────────────────────
MOOD_LEXICON = {
    # Very Positive
    "amazing": 5, "fantastic": 5, "wonderful": 5, "ecstatic": 5, "thrilled": 5,
    "elated": 5, "blissful": 5, "euphoric": 5, "overjoyed": 5, "exhilarated": 5,
    # Positive
    "happy": 4, "great": 4, "good": 4, "love": 4, "excellent": 4, "enjoyed": 4,
    "grateful": 4, "excited": 4, "proud": 4, "hopeful": 4, "joy": 4, "fun": 4,
    "blessed": 4, "cheerful": 4, "delighted": 4, "glad": 4, "laugh": 4,
    "smile": 4, "bright": 4, "success": 4, "won": 4, "achieved": 4,
    # Mild Positive
    "okay": 3, "fine": 3, "nice": 3, "calm": 3, "peaceful": 3, "relaxed": 3,
    "content": 3, "decent": 3, "alright": 3, "pleasant": 3, "comfortable": 3,
    # Mild Negative
    "tired": 2, "bored": 2, "meh": 2, "blah": 2, "dull": 2, "lonely": 2,
    "confused": 2, "lost": 2, "uncertain": 2, "worried": 2, "anxious": 2,
    "nervous": 2, "unsure": 2, "stress": 2, "difficult": 2,
    # Negative
    "sad": 1, "bad": 1, "unhappy": 1, "upset": 1, "angry": 1, "frustrat": 1,
    "disappoint": 1, "regret": 1, "fail": 1, "hurt": 1, "pain": 1, "cry": 1,
    "miss": 1, "fear": 1, "scared": 1, "hate": 1, "terrible": 1, "awful": 1,
    "horrible": 1, "miserable": 1, "depressed": 1, "hopeless": 1,
}

MOOD_EMOJI = {5: "🌟", 4: "😊", 3: "😐", 2: "😔", 1: "😞"}
MOOD_LABEL = {5: "Euphoric", 4: "Happy", 3: "Neutral", 2: "Low", 1: "Struggling"}
MOOD_COLOR = {
    5: C.BGREEN,
    4: C.GREEN,
    3: C.YELLOW,
    2: C.BYELLOW,
    1: C.BRED,
}
MOOD_THEMES = {
    5: ["You're radiating golden energy today.", "The universe is definitely on your side.",
        "Bottle this feeling — it's rare and real."],
    4: ["A genuinely good day. Hold onto it.", "Small joys add up. Today was proof.",
        "Your future self will smile reading this."],
    3: ["Not every day needs to be extraordinary.", "You showed up. That counts.",
        "Still water runs deep."],
    2: ["Heavy days make the light ones shine brighter.", "Be gentle with yourself today.",
        "It's okay to not be okay."],
    1: ["Even the longest storms end.", "You're still here. That matters more than you know.",
        "Tomorrow is a blank page."],
}

def analyze_mood(text: str) -> dict:
    """Pure-Python mood analysis using lexicon matching."""
    words = re.findall(r"[a-zA-Z']+", text.lower())
    total_words = len(words) or 1
    score_sum = 0
    matches = []

    for word in words:
        for keyword, score in MOOD_LEXICON.items():
            if word.startswith(keyword):
                score_sum += score
                matches.append((word, score))
                break

    if not matches:
        mood_score = 3
    else:
        avg = score_sum / len(matches)
        mood_score = round(max(1, min(5, avg)))

    # Detect negations ("not happy" → flip)
    text_lower = text.lower()
    neg_pattern = re.compile(r"\b(not|never|no|hardly|barely|didn't|don't|won't|can't)\b\s+\w+")
    negations = neg_pattern.findall(text_lower)
    if negations:
        mood_score = max(1, mood_score - 1)

    # Word count insight
    wc_insight = ""
    if total_words < 30:
        wc_insight = "A brief entry — sometimes less is more."
    elif total_words < 100:
        wc_insight = "A solid reflection."
    elif total_words < 300:
        wc_insight = "You really opened up today."
    else:
        wc_insight = "A deep dive into your thoughts."

    top_words = sorted(set(w for w in words if len(w) > 4), key=lambda w: -words.count(w))[:5]

    return {
        "score": mood_score,
        "emoji": MOOD_EMOJI[mood_score],
        "label": MOOD_LABEL[mood_score],
        "color": MOOD_COLOR[mood_score],
        "theme": random.choice(MOOD_THEMES[mood_score]),
        "word_count": total_words,
        "wc_insight": wc_insight,
        "top_words": top_words,
        "mood_words": matches[:5],
    }

# ─── Data Layer ────────────────────────────────────────
def load_entries() -> list:
    DATA_DIR.mkdir(exist_ok=True)
    if not ENTRIES_FILE.exists():
        return []
    with open(ENTRIES_FILE) as f:
        return json.load(f)

def save_entries(entries: list):
    DATA_DIR.mkdir(exist_ok=True)
    with open(ENTRIES_FILE, "w") as f:
        json.dump(entries, f, indent=2)

def add_entry(text: str, title: str = "") -> dict:
    entries = load_entries()
    mood = analyze_mood(text)
    now = datetime.datetime.now()
    entry = {
        "id": len(entries) + 1,
        "date": now.isoformat(),
        "title": title or now.strftime("Entry on %B %d, %Y"),
        "text": text,
        "mood": mood["score"],
        "word_count": mood["word_count"],
    }
    entries.append(entry)
    save_entries(entries)
    return entry, mood

# ─── Terminal Utilities ────────────────────────────────
def term_width():
    return shutil.get_terminal_size((80, 24)).columns

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def typewrite(text: str, delay: float = 0.025, color: str = ""):
    for ch in text:
        sys.stdout.write(color + ch + C.RESET)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def pause(msg="Press Enter to continue..."):
    input(col(f"\n  {msg}", C.DIM))

def hr(char="─", color=C.GRAY):
    w = term_width()
    print(col(char * w, color))

def box(lines: list, color=C.CYAN, width=None):
    w = width or min(term_width() - 4, 72)
    border = col("╔" + "═" * (w - 2) + "╗", color)
    bottom = col("╚" + "═" * (w - 2) + "╝", color)
    print(border)
    for line in lines:
        # Strip ANSI for length calculation
        plain = re.sub(r"\033\[[0-9;]*m", "", line)
        padding = w - 2 - len(plain)
        print(col("║", color) + " " + line + " " * max(0, padding - 1) + col("║", color))
    print(bottom)

def center(text: str, width=None, color=""):
    w = width or term_width()
    plain = re.sub(r"\033\[[0-9;]*m", "", text)
    pad = max(0, (w - len(plain)) // 2)
    print(" " * pad + (color + text + C.RESET if color else text))

# ─── Splash Screen ─────────────────────────────────────
SPLASH_FRAMES = [
"""
  ██╗     ██╗███████╗███████╗██████╗ ███████╗██████╗ ██╗      █████╗ ██╗   ██╗
  ██║     ██║██╔════╝██╔════╝██╔══██╗██╔════╝██╔══██╗██║     ██╔══██╗╚██╗ ██╔╝
  ██║     ██║█████╗  █████╗  ██████╔╝█████╗  ██████╔╝██║     ███████║ ╚████╔╝ 
  ██║     ██║██╔══╝  ██╔══╝  ██╔══██╗██╔══╝  ██╔═══╝ ██║     ██╔══██║  ╚██╔╝  
  ███████╗██║██║     ███████╗██║  ██║███████╗██║     ███████╗██║  ██║   ██║   
  ╚══════╝╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝   
"""
]

def splash():
    clear()
    w = term_width()
    colors = [C.BCYAN, C.BBLUE, C.BMAGENTA, C.BCYAN]
    for i, frame in enumerate(SPLASH_FRAMES):
        c = colors[i % len(colors)]
        for line in frame.strip("\n").split("\n"):
            center(line, color=c)
    print()
    center(col("✦  Your Terminal Time-Capsule Diary  ✦", C.DIM + C.CYAN))
    center(col("Write today. Rediscover tomorrow.", C.GRAY))
    print()

# ─── Mood Card ─────────────────────────────────────────
def render_mood_card(entry: dict, mood: dict):
    w = min(term_width() - 4, 68)
    mc = mood["color"]
    print()
    box([
        col(f"  {mood['emoji']}  Mood Analysis", C.BOLD + C.BWHITE),
        "",
        col(f"  Mood Score :  ", C.GRAY) + col(f"{'█' * mood['score']}{'░' * (5 - mood['score'])}  {mood['score']}/5  {mood['label']}", mc + C.BOLD),
        col(f"  Word Count :  ", C.GRAY) + col(str(mood['word_count']), C.BWHITE) + col(f"  — {mood['wc_insight']}", C.DIM),
        "",
        col(f"  ✦  {mood['theme']}", C.ITALIC + C.CYAN),
        "",
    ], color=mc, width=w)

# ─── ASCII Mood Graph ───────────────────────────────────
def render_mood_graph(entries: list, last_n: int = 30):
    if not entries:
        print(col("  No entries yet. Start writing!", C.GRAY))
        return

    recent = entries[-last_n:]
    scores = [e["mood"] for e in recent]
    dates  = [datetime.datetime.fromisoformat(e["date"]).strftime("%m/%d") for e in recent]

    height = 7
    width  = min(len(scores) * 3, term_width() - 12)

    print()
    print(col("  📈  Mood Timeline", C.BOLD + C.BWHITE) + col(f"  (last {len(recent)} entries)", C.GRAY))
    print()

    # Build grid
    grid = [[" " for _ in range(len(scores))] for _ in range(height)]
    for i, score in enumerate(scores):
        row = height - score  # score 5 → row 0, score 1 → row 4
        row = max(0, min(height - 1, row))
        grid[row][i] = "●"
        # Fill bar below
        for r in range(row + 1, height):
            grid[r][i] = "│" if r == row + 1 else "▓"

    # Y-axis labels
    y_labels = ["5 ✦", "4 😊", "3 😐", "2 😔", "1 😞"]
    bar_colors = [C.BGREEN, C.GREEN, C.YELLOW, C.BYELLOW, C.BRED]

    for row_idx, (row, label, barcol) in enumerate(zip(grid, y_labels, bar_colors)):
        line = col(f"  {label}  ", C.GRAY)
        for cell in row:
            if cell == "●":
                line += col("● ", barcol + C.BOLD)
            elif cell in ("│", "▓"):
                line += col("▓ ", barcol)
            else:
                line += col("· ", C.GRAY)
        print(line)

    # X-axis
    print(col("        " + "  ".join(["─"] * len(scores)), C.GRAY))

    # Date labels (every N)
    step = max(1, len(scores) // 6)
    label_line = "         "
    for i, d in enumerate(dates):
        if i % step == 0:
            label_line += col(d[:4], C.GRAY) + " "
        else:
            label_line += "   "
    print(label_line)
    print()

    # Summary stats
    if scores:
        avg = sum(scores) / len(scores)
        trend = scores[-1] - scores[0] if len(scores) > 1 else 0
        trend_str = ("↑ improving" if trend > 0 else "↓ declining" if trend < 0 else "→ stable")
        trend_col = C.BGREEN if trend > 0 else C.BRED if trend < 0 else C.YELLOW

        stats = [
            col(f"  Avg Mood: ", C.GRAY) + col(f"{avg:.1f}/5", C.BWHITE),
            col(f"  Trend: ", C.GRAY) + col(trend_str, trend_col),
            col(f"  Best Day: ", C.GRAY) + col(str(max(scores)) + "/5", C.BGREEN),
            col(f"  Entries: ", C.GRAY) + col(str(len(entries)), C.BWHITE),
        ]
        print("  " + "   ".join(stats))
    print()

# ─── Streak & Habit Tracker ────────────────────────────
def get_streaks(entries: list) -> dict:
    if not entries:
        return {"current": 0, "longest": 0}
    dates = sorted(set(
        datetime.datetime.fromisoformat(e["date"]).date() for e in entries
    ))
    today = datetime.date.today()

    # Current streak
    current = 0
    check = today
    while check in dates:
        current += 1
        check -= datetime.timedelta(days=1)
    if today not in dates:
        yesterday = today - datetime.timedelta(days=1)
        check = yesterday
        current = 0
        while check in dates:
            current += 1
            check -= datetime.timedelta(days=1)

    # Longest streak
    longest = 1
    run = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i-1]).days == 1:
            run += 1
            longest = max(longest, run)
        else:
            run = 1

    return {"current": current, "longest": longest}

# ─── On This Day ───────────────────────────────────────
def on_this_day(entries: list):
    today = datetime.date.today()
    memories = []
    for entry in entries:
        d = datetime.datetime.fromisoformat(entry["date"]).date()
        if d.month == today.month and d.day == today.day and d.year < today.year:
            years_ago = today.year - d.year
            memories.append((years_ago, entry))
    return memories

# ─── Cinematic Replay ──────────────────────────────────
def cinematic_replay(entry: dict):
    clear()
    date = datetime.datetime.fromisoformat(entry["date"])
    date_str = date.strftime("%A, %B %d %Y · %I:%M %p")
    mood_score = entry.get("mood", 3)
    mc = MOOD_COLOR.get(mood_score, C.WHITE)

    # Film strip header
    film = "▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░"
    w = term_width()
    print(col(film[:w], C.GRAY))
    print()
    center(col(f"🎞  MEMORY REPLAY", C.BOLD + C.BMAGENTA))
    center(col(f"[ {date_str} ]", C.GRAY))
    print()
    center(col(f"{'─' * 40}", C.GRAY))
    print()

    # Title
    if entry.get("title"):
        center(col(entry["title"], C.BOLD + C.BWHITE))
        print()

    # Mood indicator
    emoji = MOOD_EMOJI.get(mood_score, "😐")
    center(col(f"{emoji}  Mood: {MOOD_LABEL.get(mood_score, 'Unknown')}  {emoji}", mc))
    print()
    center(col(f"{'─' * 40}", C.GRAY))
    print()

    # Typewrite the entry
    words = entry["text"].split()
    ww = term_width() - 12
    wrapped = textwrap.fill(entry["text"], width=ww)
    lines = wrapped.split("\n")

    indent = " " * 6
    for line in lines:
        sys.stdout.write(indent + C.ITALIC + C.BWHITE)
        for ch in line:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(0.01)
        sys.stdout.write(C.RESET + "\n")
        sys.stdout.flush()

    print()
    print(col(film[:w], C.GRAY))
    print()

# ─── Write Entry (Interactive) ─────────────────────────
def write_entry():
    clear()
    splash()
    print()
    print(col("  ✍️   NEW ENTRY", C.BOLD + C.BWHITE))
    hr()
    print(col("  Enter a title (or press Enter to auto-title):", C.GRAY))
    title = input("  → ").strip()

    print()
    print(col("  What's on your mind today?", C.BOLD + C.CYAN))
    print(col("  (Type your entry. When done, type a line with just 'DONE' or press Ctrl+D)", C.GRAY))
    print()

    lines = []
    while True:
        try:
            line = input("  ")
            if line.strip().upper() == "DONE":
                break
            lines.append(line)
        except EOFError:
            break

    if not lines:
        print(col("\n  Nothing written. Entry cancelled.", C.YELLOW))
        return

    text = "\n".join(lines)
    print()
    print(col("  Analyzing your entry...", C.GRAY))
    time.sleep(0.6)

    entry, mood = add_entry(text, title)

    # Animation
    for i in range(3):
        sys.stdout.write(f"\r  {'█' * (i+1)}{'░' * (2-i)}  Saving...")
        sys.stdout.flush()
        time.sleep(0.2)
    print(col("\r  ✅  Entry saved!", C.BGREEN))

    render_mood_card(entry, mood)

    # On this day trigger
    entries = load_entries()
    memories = on_this_day(entries[:-1])  # exclude just-written
    if memories:
        print()
        print(col(f"  🕰️   On This Day  — {len(memories)} memory from the past!", C.BMAGENTA + C.BOLD))
        for years_ago, mem in memories[:2]:
            d = datetime.datetime.fromisoformat(mem["date"])
            print(col(f"  {years_ago} year{'s' if years_ago > 1 else ''} ago ({d.strftime('%B %d, %Y')}): ", C.GRAY)
                  + col(f'"{mem["title"]}"', C.BWHITE))
        print(col("  → Run `lifereplay replay` to relive them!", C.CYAN))

    pause()

# ─── View Entries ──────────────────────────────────────
def list_entries():
    entries = load_entries()
    clear()
    splash()
    print(col(f"  📓  YOUR JOURNAL  ({len(entries)} entries)", C.BOLD + C.BWHITE))
    hr()

    if not entries:
        print(col("\n  No entries yet! Run `lifereplay write` to start.\n", C.GRAY))
        return

    for entry in reversed(entries[-20:]):
        date = datetime.datetime.fromisoformat(entry["date"])
        mood_score = entry.get("mood", 3)
        mc = MOOD_COLOR.get(mood_score, C.WHITE)
        emoji = MOOD_EMOJI.get(mood_score, "")

        date_str = date.strftime("%b %d %Y")
        preview = entry["text"][:60].replace("\n", " ") + ("…" if len(entry["text"]) > 60 else "")

        print(f"  {col(str(entry['id']).rjust(3), C.GRAY)}  "
              f"{col(date_str, C.CYAN)}  "
              f"{col(emoji + ' ' + MOOD_LABEL.get(mood_score,'').ljust(10), mc)}  "
              f"{col(entry['title'][:25], C.BOLD + C.BWHITE)}")
        print(f"       {col(preview, C.DIM)}")
        print()

    # Streaks
    s = get_streaks(entries)
    print(col(f"  🔥 Current Streak: {s['current']} days", C.BYELLOW + C.BOLD)
          + col(f"   |   🏆 Longest: {s['longest']} days", C.GRAY))
    print()
    render_mood_graph(entries)

# ─── Replay a specific entry ────────────────────────────
def replay_entry(entry_id: int = None):
    entries = load_entries()
    if not entries:
        print(col("  No entries to replay!", C.YELLOW))
        return

    if entry_id:
        matches = [e for e in entries if e["id"] == entry_id]
        if not matches:
            print(col(f"  Entry #{entry_id} not found.", C.BRED))
            return
        entry = matches[0]
    else:
        # Show memories from this day, or a random old entry
        memories = on_this_day(entries)
        if memories:
            print()
            print(col(f"  🕰️   On This Day in History:", C.BMAGENTA + C.BOLD))
            for i, (years, mem) in enumerate(memories):
                d = datetime.datetime.fromisoformat(mem["date"])
                print(col(f"  [{i+1}] {years}yr ago – {d.strftime('%b %d %Y')} – {mem['title']}", C.BWHITE))
            print(col("  [r] Random entry", C.GRAY))
            choice = input(col("\n  Pick a memory: ", C.CYAN)).strip()
            if choice.isdigit() and 1 <= int(choice) <= len(memories):
                entry = memories[int(choice) - 1][1]
            else:
                entry = random.choice(entries)
        else:
            entry = random.choice(entries)

    cinematic_replay(entry)
    pause()

# ─── Export summary ────────────────────────────────────
def export_summary():
    entries = load_entries()
    if not entries:
        print(col("  No entries to export!", C.YELLOW))
        return

    today = datetime.date.today()
    path = Path.home() / f"lifereplay_summary_{today}.txt"
    lines = [
        "═" * 60,
        "  L I F E R E P L A Y — Journal Export",
        f"  Generated: {today.strftime('%B %d, %Y')}",
        f"  Total Entries: {len(entries)}",
        "═" * 60, "",
    ]

    monthly = defaultdict(list)
    for e in entries:
        d = datetime.datetime.fromisoformat(e["date"])
        key = d.strftime("%B %Y")
        monthly[key].append(e)

    for month, mes in monthly.items():
        avg_mood = sum(m["mood"] for m in mes) / len(mes)
        lines.append(f"\n── {month}  (avg mood {avg_mood:.1f}/5)  ──")
        for e in mes:
            d = datetime.datetime.fromisoformat(e["date"])
            emoji = MOOD_EMOJI.get(e["mood"], "")
            lines.append(f"\n  {d.strftime('%b %d')}  {emoji}  {e['title']}")
            lines.append(f"  {e['text'][:200]}{'…' if len(e['text']) > 200 else ''}")

    lines += ["", "═" * 60, "  End of Journal", "═" * 60]
    with open(path, "w") as f:
        f.write("\n".join(lines))

    print(col(f"\n  ✅  Journal exported to: {path}", C.BGREEN))

# ─── CLI Entry Point ───────────────────────────────────
HELP_TEXT = f"""
{col('L I F E R E P L A Y', C.BOLD + C.BCYAN)} — Your Terminal Time-Capsule Diary

{col('COMMANDS', C.BOLD + C.BWHITE)}
  {col('write', C.BGREEN)}      Write a new journal entry
  {col('list', C.BGREEN)}       Browse all your entries + mood graph
  {col('replay', C.BGREEN)}     Cinematic replay of a memory (by ID or on-this-day)
  {col('export', C.BGREEN)}     Export your full journal as a plain-text summary
  {col('graph', C.BGREEN)}      Just show the mood graph
  {col('help', C.BGREEN)}       Show this help

{col('EXAMPLES', C.BOLD + C.BWHITE)}
  python lifereplay.py write
  python lifereplay.py list
  python lifereplay.py replay
  python lifereplay.py replay 7      {col('# replay entry #7', C.GRAY)}
  python lifereplay.py export
"""

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("command", nargs="?", default="help")
    parser.add_argument("arg", nargs="?", default=None)
    args = parser.parse_args()

    cmd = args.command.lower()

    if cmd == "write":
        write_entry()
    elif cmd == "list":
        list_entries()
        pause()
    elif cmd == "replay":
        eid = int(args.arg) if args.arg and args.arg.isdigit() else None
        replay_entry(eid)
    elif cmd == "graph":
        entries = load_entries()
        render_mood_graph(entries)
    elif cmd == "export":
        export_summary()
    else:
        splash()
        print(HELP_TEXT)

if __name__ == "__main__":
    main()
