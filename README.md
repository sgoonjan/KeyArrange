---
title: KeyArrange
emoji: 🎹
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# KeyArrange

**Upload a song. Get sheet music you can actually play.**

[Try the Live Demo 🤗](https://huggingface.co/spaces/Goonjan/KeyArrange) · [Sample Outputs](#sample-outputs)

> **Status:** The end-to-end pipeline is actively being built. See the [Roadmap](#roadmap) for what's done and what's next.

---

## The Problem

I play piano at an intermediate level — arpeggios, chord progressions, songs I've learned by feel. But I have no ear training. When I hear a song I want to learn, I can't transcribe it myself, and I can't find a playable arrangement for most of it.

The tools that exist don't solve this:

| Tool | What it does | Why it falls short |
|---|---|---|
| Synthesia / YouTube tutorials | Walks you through notes visually | You follow, you don't learn. No sheet music. |
| AnthemScore / Transcribe! | Full polyphonic transcription | Outputs every instrument. Unplayable by one person. |
| MuseScore built-in import | Converts MIDI you already have | Assumes you already have a clean source. |
| Online MIDI converters | Audio → raw MIDI | Raw transcription dump. No arrangement, no playability logic. |

None of them answer the actual question: *I heard this song. Can I play it on piano tonight?*

KeyArrange does. It takes any pop song as audio input, separates the musical roles, and produces a two-hand beginner–intermediate piano arrangement — physically playable, sheet music included.

---

## Demo

> Upload an MP3. Download a PDF and MIDI you can open in any DAW or print and play.

```
[  Choose file  ]   →   [ Arrange ]   →   [ Download PDF ]  [ Download MIDI ]
```

[*Live demo (v1) is now live on Hugging Face Spaces!*](https://huggingface.co/spaces/Goonjan/KeyArrange)

### Sample Outputs

| Song | Original | Arranged MIDI | Sheet Music PDF |
|---|---|---|---|
| Coming soon | — | — | — |

---

## What "playable" actually means

This is the core design constraint the whole project is built around. Playable doesn't mean "renders correctly in a DAW." It means a real pianist can sit down and play it.

- Max hand span: one octave (~9 white keys)
- Max notes per hand at any moment: 3
- Note density matched to tempo — no sixteenth-note runs at 160 BPM
- Clear left hand / right hand separation — no ambiguous voicings
- Repeated notes spaced so a human can re-strike them

The quick test: can a pianist sight-read it at moderate tempo, clearly assign hands, and not need to rearrange anything? If yes, it passes.

---

## Stack

- **[Demucs](https://github.com/facebookresearch/demucs)** (Facebook Research) — source separation into vocals, bass, drums, and other
- **[Basic Pitch](https://github.com/spotify/basic-pitch)** (Spotify) — lightweight polyphonic audio-to-MIDI transcription
- **[music21](https://web.mit.edu/music21/)** — chord analysis, key detection, voice leading
- **[pretty_midi](https://github.com/craffel/pretty-midi)** — MIDI read/write
- **[MuseScore CLI](https://musescore.org)** — sheet music rendering
- **[FastAPI](https://fastapi.tiangolo.com)** — web API
- **Python 3.11+**

---

## Roadmap

**v1 — complete**
- [x] End-to-end pipeline: audio → MIDI
- [x] Three core playability transforms (density, span, note cap)
- [x] Web UI with MIDI download

**v2 — in progress**
- [ ] Chord-aware left hand voicing (root + third + fifth from chord analysis)
- [ ] MuseScore PDF rendering

**v3 — planned**
- [ ] Beat tracking with madmom for better metric strength scoring
- [ ] Melody smoothing — strip ornaments and melisma from vocal transcription

**Later**
- [ ] Fine-tuned arrangement model on POP909 dataset
- [ ] Difficulty levels (beginner / intermediate / advanced)
- [ ] Style options (ballad, jazz voicings)

---

## Project Structure

```
KeyArrange/
├── README.md
├── DECISIONS.md          ← key tradeoffs and why
├── src/keyarrange/
│   ├── audio/            ← loading, normalization
│   ├── separation/       ← Demucs wrapper
│   ├── analysis/         ← tempo, beat, key
│   ├── structure/        ← transcription, chord estimation
│   ├── piano/            ← arrangement engine
│   ├── render/           ← MIDI + PDF output
│   ├── api/              ← FastAPI app
│   └── cli.py
├── web/                  ← single-page frontend
├── tests/
└── examples/sample_outputs/
```

---

## License

MIT. Audio files are user-provided. Output MIDI is a derivative arrangement. No original audio is stored or redistributed.
