# 🎞️ LifeReplay — Your Terminal Time-Capsule Diary

> *Write today. Rediscover tomorrow.*

LifeReplay is a beautifully minimal Python CLI diary that lives in your terminal. No apps, no cloud, no subscriptions — just you and your thoughts, with a sprinkle of magic.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📝 **Write Entries** | Write freely in your terminal — multiline, titled, private |
| 🧠 **Mood Analysis** | Pure-Python NLP lexicon detects your mood (1–5 scale) with emoji |
| 📈 **ASCII Mood Graph** | Visualize your emotional journey over time — right in the terminal |
| 🎞️ **Cinematic Replay** | Entries typewrite back to life like a movie scene |
| 🕰️ **On This Day** | Get surprised by memories from past years — the same day |
| 🔥 **Streak Tracking** | Track your journaling streaks and personal bests |
| 📤 **Export** | One-click export your full journal to a beautifully formatted .txt |

---

## 🚀 Quick Start

```bash
# Clone or download the file
python lifereplay.py write      # Write your first entry
python lifereplay.py list       # Browse entries + mood graph
python lifereplay.py replay     # Relive a memory cinematically
python lifereplay.py graph      # Just the mood graph
python lifereplay.py export     # Export your journal
```

**No dependencies.** Requires only Python 3.7+.

---

## 📸 Screenshots

```
╔══════════════════════════════════════╗
║  🌟  Mood Analysis                   ║
║                                      ║
║  Mood Score :  █████  5/5  Euphoric  ║
║  Word Count :  148  — You opened up  ║
║                                      ║
║  ✦  You're radiating golden energy.  ║
╚══════════════════════════════════════╝
```

```
  📈  Mood Timeline  (last 14 entries)

  5 ✦  · · ● · · · · ● · · · · · ●
  4 😊  · · ▓ · ● · ● ▓ ● · ● · ●  
  3 😐  ● ● ▓ ● ▓ ● ▓ ▓ ▓ ● ▓ ● ▓
  2 😔  ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓
  1 😞  · · · · · · · · · · · · · ·
        ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
```

---

## 💾 Data Storage

All your entries are stored **locally** in `~/.lifereplay/entries.json`. Your words never leave your machine.

---

## 🎨 Philosophy

Most journaling apps are heavy, cloud-dependent, or distracting. LifeReplay is the opposite:
- Runs in 50 lines of imports
- Zero dependencies beyond Python stdlib
- Your data, your machine, your story

---

## 📄 License

MIT — free to use, share, and remix.

---

*Built with ❤️ and pure Python.*
