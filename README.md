<div align="center">

# 🎬 Scired

### Turn YouTube videos into personalized language learning material

*Analyze video complexity → Extract difficult words → Auto-create Anki flashcards*

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status: In Development](https://img.shields.io/badge/Status-In%20Development-yellow)]()
[![Platform: Linux | macOS | Windows](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey?logo=linux&logoColor=white)]()

</div>

---

## 🤔 The Problem

Language learners face a paradox:

> *"I want to watch videos in English/German, but I don't know which ones
> match my level. And when I do understand them — I forget the new words."*

| Pain | Current reality | With Scired |
|------|:---:|:---:|
| Don't know video difficulty | Trial and error | ✅ Auto CEFR classification |
| Forget new words | Write them down manually (or don't) | ✅ Auto Anki flashcards |
| No context for vocabulary | Dictionary gives abstract translations | ✅ Sentence + timestamp from video |
| No learning statistics | No tracking | ✅ Word count, level breakdown |

---

## 💡 The Solution

**Scired** takes a YouTube video URL and:

1. 🎙️ **Transcribes** it (YouTube subtitles → Whisper fallback)
2. 📊 **Analyzes** complexity on the CEFR scale (A1–C2)
3. 🔍 **Extracts** words above your threshold
4. 🃏 **Creates** Anki flashcards with context and timestamps

**One command. Zero manual work.**

```bash
$ scired run "https://youtube.com/watch?v=dQw4w9WgXcQ"

  🎬 Processing: https://youtube.com/watch?v=dQw4w9WgXcQ
  ──────────────────────────────────────────────────────────
  ✅ Transcribed: 2,847 words (source: youtube_subs)
  📊 Level: B2 | Words: 2847
  🔍 Difficult words: 47 (threshold: B2+)
  💾 Saved to database (47 new words)
  🃏 Anki cards created: 47 → "Scired::Vocabulary"
  ──────────────────────────────────────────────────────────
  📝 "How the German Economy Works"
  📺 Channel: DW Documentaries
  ⏱️  Duration: 14 min
```

---

## ✨ Features

- **🌐 Multi-language**: English and German
- **🎯 CEFR classification**: Every video gets an A1–C2 rating
- **📝 Smart transcription**: YouTube subtitles first, Whisper as fallback
- **🃏 Anki integration**: Auto-created flashcards via AnkiConnect
- **⏱️ Timestamps**: Each card links back to the exact moment in the video
- **📈 Statistics**: Word count, level distribution, learning progress
- **💾 Local-first**: SQLite storage, no cloud dependency
- **⚡ Idempotent**: Re-running never creates duplicates
- **🖥️ Cross-platform**: Linux, macOS, Windows

---

## 📦 Installation

Scired works on **Linux**, **macOS**, and **Windows**. Follow the instructions
for your operating system.

---

### 🐧 Linux

#### Step 1: Install system dependencies

```bash
# Fedora / RHEL
sudo dnf install python3 python3-pip ffmpeg git

# Ubuntu / Debian
sudo apt install python3 python3-pip ffmpeg git

# Arch Linux
sudo pacman -S python pip ffmpeg git
```

#### Step 2: Clone and install Scired

```bash
git clone git@github.com:cabacy/Scired.git
cd Scired

python3 -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
python -c "import nltk; nltk.download('punkt')"
```

#### Step 3: Configure

```bash
cp .env.example .env
```

---

### 🍎 macOS

#### Step 1: Install Homebrew (if not installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Step 2: Install system dependencies

```bash
brew install python ffmpeg git
```

#### Step 3: Clone and install Scired

```bash
git clone git@github.com:cabacy/Scired.git
cd Scired

python3 -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
python -c "import nltk; nltk.download('punkt')"
```

#### Step 4: Configure

```bash
cp .env.example .env
```

---

### 🪟 Windows

#### Step 1: Install prerequisites

Download and install:

| Software | Where to get | Notes |
|----------|-------------|-------|
| **Python 3.10+** | [python.org/downloads](https://www.python.org/downloads/) | ✅ Check **"Add Python to PATH"** during install |
| **ffmpeg** | [ffmpeg.org/download](https://ffmpeg.org/download.html) | Or: `winget install ffmpeg` |
| **Git** | [git-scm.com](https://git-scm.com/download/win) | Use default settings |

**Or install everything via winget (PowerShell as Admin):**

```powershell
winget install Python.Python.3.12
winget install ffmpeg
winget install Git.Git
```

#### Step 2: Clone and install Scired

Open **PowerShell** or **Command Prompt**:

```powershell
git clone git@github.com:cabacy\Scired.git
cd Scired

py -3 -m venv .venv
.venv\Scripts\activate

pip install -e ".[dev]"
python -c "import nltk; nltk.download('punkt')"
```

#### Step 3: Configure

```powershell
copy .env.example .env
```

---

## 🃏 Setting Up Anki + AnkiConnect

Scired creates flashcards in [Anki](https://apps.ankiweb.net/) through the
[AnkiConnect](https://ankiweb.net/shared/info/2055492159) plugin.

### Step 1: Install Anki

| OS | Installation |
|----|-------------|
| 🐧 **Linux** | `sudo dnf install anki` (Fedora) or download from [apps.ankiweb.net](https://apps.ankiweb.net/) |
| 🍎 **macOS** | `brew install --cask anki` or download `.dmg` from [apps.ankiweb.net](https://apps.ankiweb.net/) |
| 🪟 **Windows** | Download `.exe` installer from [apps.ankiweb.net](https://apps.ankiweb.net/) |

### Step 2: Install AnkiConnect Plugin

1. **Open Anki**
2. Go to **Tools → Add-ons**
3. Click **Get Add-ons...**
4. Enter the AnkiConnect add-on code: **`2055492159`**
5. Click **OK**
6. **Restart Anki**

### Step 3: Verify AnkiConnect is running

With Anki **open**, run in your terminal:

**Linux / macOS:**
```bash
curl http://127.0.0.1:8765 -d '{"action": "version", "version": 6}'
```

**Windows (PowerShell):**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8765" -Method Post -Body '{"action": "version", "version": 6}'
```

**Expected response:**
```json
{"result": 6, "error": null}
```

If you see this — AnkiConnect is working and Scired can create cards. ✅

### Troubleshooting Anki

| Problem | Solution |
|---------|----------|
| `Connection refused` | Anki is not running. Open Anki first. |
| `Connection refused` after install | Restart Anki after installing AnkiConnect. |
| Cards not appearing | Check deck name: `Scired::Vocabulary` |
| Plugin not found | Reinstall: Tools → Add-ons → Get Add-ons → `2055492159` |
| Windows: firewall blocks | Allow Python through Windows Firewall |

---

## 🚀 Usage

### Full pipeline (recommended)

```bash
scired run "https://youtube.com/watch?v=VIDEO_ID"
```

### Transcribe only

```bash
scired transcribe "https://youtube.com/watch?v=VIDEO_ID"
```

### Specify language

```bash
# English (default)
scired run "https://youtube.com/watch?v=VIDEO_ID"

# German
scired run --lang de "https://youtube.com/watch?v=VIDEO_ID"
```

### Set difficulty threshold

```bash
# Only C1+ words (fewer cards)
scired run --threshold C1 "https://youtube.com/watch?v=VIDEO_ID"

# B1+ words (more cards, default: B2+)
scired run --threshold B1 "https://youtube.com/watch?v=VIDEO_ID"
```

### Skip Anki sync

```bash
scired run --no-anki "https://youtube.com/watch?v=VIDEO_ID"
```

### View statistics

```bash
scired stats
```

---

## ⚙️ Configuration

All settings are in `.env` file:

```bash
# ─── Logging ─────────────────────────────────────────────
SCIRED_LOG_LEVEL=INFO

# ─── Transcription ───────────────────────────────────────
SCIRED_PREFERRED_SUBTITLE_LANG=en
SCIRED_FALLBACK_TO_WHISPER=true
SCIRED_WHISPER_MODEL=base          # tiny|base|small|medium|large

# ─── Analysis ────────────────────────────────────────────
SCIRED_DEFAULT_THRESHOLD=B2
SCIRED_MIN_WORD_LENGTH=3

# ─── Anki ────────────────────────────────────────────────
SCIRED_ANKI_URL=http://127.0.0.1:8765
SCIRED_ANKI_DECK_NAME=Scired::Vocabulary
```

### Whisper Model Comparison

| Model | Size | Speed (CPU) | Quality | Use case |
|-------|------|-------------|---------|----------|
| `tiny` | 75 MB | ~1 min / 10 min video | Low | Quick testing |
| `base` | 142 MB | ~2 min / 10 min video | Good | **Recommended** |
| `small` | 466 MB | ~5 min / 10 min video | Better | Higher accuracy |
| `medium` | 1.5 GB | ~12 min / 10 min video | High | Quality matters |
| `large` | 3 GB | ~25 min / 10 min video | Best | GPU recommended |

---


## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Language | Python 3.10+ | Core development |
| Transcription | `youtube-transcript-api` | YouTube subtitles |
| Transcription (fallback) | `faster-whisper` | Local speech-to-text |
| Audio download | `yt-dlp` | Extract audio for Whisper |
| Word frequency | `wordfreq` | CEFR level estimation |
| Tokenization | `nltk` | Text processing |
| Data validation | `pydantic` | Models & config |
| Storage | `sqlite3` | Local database |
| Anki | `AnkiConnect` API | Flashcard creation |
| CLI | `argparse` | User interface |
| Testing | `pytest` | Quality assurance |

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License.

---

## 👤 Author

**cabacy** — [@cabacy](https://github.com/cabacy)

---

<div align="center">

*Built with ❤️ for language learners who prefer watching over reading.*

</div>
