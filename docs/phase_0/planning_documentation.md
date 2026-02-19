# Phase 0: Planning

All Phase 0 planning notes in one place for now. Once things settle, each section gets split into its own `.md` in the repo. Fast iteration first, structure later.

---

## 01\_project\_scope.md

**Goal:** Take a pop song as audio input and produce a piano arrangement a real beginner–intermediate pianist can sit down and play. Not just something that renders correctly — something actually performable.

**What we're balancing:** Musicality, physical playability, faithfulness to the song's identity.

**Input**
- Audio file (MP3 / WAV)
- Optional: tempo hints, key hints

**Output**
- MIDI file (primary)
- Sheet music PDF (Week 2 milestone)
- Web UI with live demo (MVP — not deferred)

**Deferred to later phases**
- Difficulty levels (beginner / intermediate / advanced)
- Style preferences (ballad, jazz)
- Real-time live transcription

---

## 02\_human\_playable.md

This is probably the most important definition in the project. "Human-playable" means a beginner–intermediate pianist can physically perform the output without superhuman reach, speed, or memory.

**Not the same as** (common pitfall to avoid):
- MIDI that merely sounds correct
- Perfect transcription of all instruments
- Virtuoso-level arrangements

**Physical constraints**
- Max hand span ~9–10 white keys (one octave)
- No repeated octave leaps at fast tempos
- No impossible note clusters for a single hand

**Temporal constraints**
- Note density must match tempo (no eighth-note spam at 180+ BPM)
- Repeated notes must be realistically re-strikeable

**Cognitive constraints**
- Clear melody vs. accompaniment separation
- Predictable rhythmic patterns
- ≤ 3 notes per hand at a time

**Quick check:** Can a pianist sight-read it at moderate tempo, clearly assign hands, and not need to rearrange voicings? → Human-playable.

---

## 03\_quality\_bar.md

The bar isn't perfection — it's "would a pianist actually use this?" Two sides to it:

**Musical**
- Preserve main vocal melody
- Preserve harmonic rhythm (chord changes)
- Should feel like a piano arrangement, not a transcription dump

**Playability**
- Playable by a single pianist
- Stick to triads — avoid dense cluster chords
- Prefer broken chords / arpeggios over sustained pads

---

## 04\_non\_goals.md

Explicitly out of scope for v1:
- Perfect transcription of every instrument
- Jazz-grade reharmonization
- Orchestral reduction
- Real-time live transcription

All interesting problems, but each one would balloon scope. Keeping them out of v1 is what lets us actually ship something.

---

## 05\_tracks\_and\_roles.md

The arrangement isn't one stream of notes — it's distinct musical roles. Here's how they map to stems and hands:

**Melody track**
- Source: Demucs vocals stem → transcribed via Basic Pitch
- Monophonic, lightly ornamented
- Default: right hand

**Chord / Harmony track**
- Derived from chord analysis on the "other" stem (guitars, keys)
- Simplified to triads — root + third + fifth within one octave
- Default: left hand

**Bass function**
- Source: Demucs bass stem → used to infer chord roots and movement
- Not transcribed note-for-note — used to drive left hand voicing decisions
- Merged into left-hand harmony to reduce cognitive load

**Drums**
- Discarded entirely

The key design insight: Demucs separates by *musical role*, not by pitch. Those roles map cleanly onto pianist roles — that's why stem separation is done before transcription, not after.

---

## 06\_representation\_choices.md

MIDI is the obvious choice — it's the only format that cleanly separates *what* is played from *how it sounds*.

**Why it works**
- Editable, inspectable, programmatic
- Maps directly to piano keys

**Accepted limitations**
- No articulation nuance by default
- No lyric alignment by default

Both can be layered on later if needed.

---

## 07\_evaluation\_metrics.md

Some of this is measurable, some comes down to gut feel. Both matter.

**Objective (automated)**
- Notes per second per hand
- Max chord size per hand
- Hand span distance over time
- Number of leaps per hand in a time window
- Playability violations flagged vs. auto-corrected

**Subjective**
- Does this feel playable?
- Does this sound like the song?
- Would a pianist keep this arrangement?

---

## 08\_licensing\_and\_ethics.md

- Audio is user-provided
- Output MIDI is a derivative arrangement, not a copy
- No redistribution of original audio
- Project is technical / educational — not a piracy tool

---

## 09\_system\_architecture.md

**Pipeline overview**

```
Audio Input (MP3/WAV)
        ↓
  Source Separation          [Demucs → vocals, bass, other, drums]
        ↓
  Per-Stem Transcription     [Basic Pitch → raw MIDI per stem]
        ↓
  Arrangement Engine         [melody extract → hand split → density reduce → voicing simplify → span check]
        ↓
  Validation                 [playability report + auto-correction]
        ↓
  MIDI Output + PDF Render   [pretty_midi + MuseScore CLI]
        ↓
  Web API                    [FastAPI — serves MIDI + PDF to frontend]
```

Linear pipeline, but each stage is its own module. The key design rule: every step writes its output to disk before the next one runs. No hidden state, nothing coupled. Makes debugging and swapping out algorithms significantly easier.

**Modules**

| Module | Path | Responsibility |
|---|---|---|
| Audio I/O | `audio/` | Load MP3/WAV, convert to mono, normalize sample rate |
| Separation | `separation/` | Run Demucs, extract and save stems |
| Analysis | `analysis/` | Tempo detection, beat tracking, key estimation → timing grid + metadata (JSON) |
| Structure | `structure/` | Per-stem transcription, chord estimation, bar/section segmentation → symbolic musical events |
| Piano Logic | `piano/` | Arrangement engine — note scoring, density reduction, hand assignment, span enforcement, voicing simplification |
| Rendering | `render/` | Symbolic events → MIDI + optional MuseScore PDF |
| API | `api/` | FastAPI app wrapping the pipeline, file upload/download endpoints |

**Arrangement engine internals**

The piano logic module is a transform chain — each pass takes and returns a note list:

```
raw_midi → [melody_extractor] → [hand_splitter] → [density_reducer] → [voicing_simplifier] → [span_checker]
```

Each transform is independently testable. Note prioritization within transforms is score-based:

```
score = w1*(metric_strength) + w2*(duration) + w3*(harmonic_function) + w4*(melodic_peak)
```

When a constraint forces note reduction, highest-scoring notes survive. Weights are tunable — this is where musical judgment gets encoded without being magic.

**Data flow rules**
- No hidden state
- Every stage writes output to disk
- Intermediate formats are human-readable (JSON / CSV) where possible
- Any single module can be swapped out independently

**Error handling** — a degraded output beats no output.
- Invalid audio → fail fast
- Uncertain musical estimates → warn, don't crash
- Always produce something, even if simplified

---

## 10\_cli\_philosophy.md

The idea: drop into any stage of the pipeline without re-running everything before it.

- Each stage is runnable independently
- Every command produces inspectable output
- Intermediate artifacts are saved to disk

```
input audio → separation → analysis → structure → piano logic → MIDI → PDF
```

The CLI is the internal tool. The web UI is the product.

---

## 11\_repository\_structure.md

```
KeyArrange/
├── README.md                  ← product-first: what, who, demo link, then architecture
├── DECISIONS.md               ← key tradeoffs and why
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── docs/
│   └── phase_0/
│       ├── project_scope.md
│       ├── human_playable.md
│       ├── quality_bar.md
│       ├── non_goals.md
│       ├── tracks_and_roles.md
│       ├── representation_choices.md
│       ├── evaluation_metrics.md
│       ├── licensing_and_ethics.md
│       ├── cli_philosophy.md
│       └── system_architecture.md
├── src/
│   └── keyarrange/
│       ├── __init__.py
│       ├── audio/
│       ├── separation/
│       ├── analysis/
│       ├── structure/
│       ├── piano/
│       ├── render/
│       ├── api/
│       └── cli.py
├── web/                       ← minimal frontend (single-page upload + download)
├── tests/
│   └── test_smoke.py
└── examples/
    └── sample_outputs/        ← before/after audio + MIDI examples for README
```

- `docs/` mirrors project phases
- `src/` is production code only
- `web/` is the product face — not an afterthought
- `DECISIONS.md` surfaces engineering judgment, not just engineering output
- `examples/` feeds the README demo — non-technical visitors land here first

---

## 12\_decisions.md

Explicit tradeoffs made and why. This file grows with the project.

**Stem separation before transcription, not after.**
Transcribing a full mix means Basic Pitch is working against overlapping kick drum, bass, vocals, and rhythm guitar simultaneously. Polyphonic transcription on a blended signal is an unsolved problem. Separating first gives each transcription step a cleaner, semantically meaningful signal.

**Vocals → right hand, bass stem → left hand chord roots.**
The bass stem in pop music almost always outlines chord roots and movement — exactly what a beginner left hand should play. The bass is not transcribed note-for-note; it's used to infer harmonic movement and drive a generated voicing pattern. This is more musical and more playable than a literal transcription.

**Rule-based arrangement engine with score-based note prioritization.**
Rule-based gives deterministic, testable, explainable output. Every constraint from `human_playable.md` maps to a concrete function. An LLM layer can be added later for edge cases that are hard to encode as rules, but it's not load-bearing in v1.

**Fixed pitch threshold as hand-split fallback.**
Notes above MIDI 60 → right hand, below → left. Simple, explainable, almost always musically correct for pop songs. The stem-based approach is primary; this is the safety net.

**Web UI is core, not deferred.**
A working URL someone can visit beats a CLI that requires setup. Non-technical stakeholders — including founders evaluating the project — need to be able to use it in 30 seconds. The product loop must close before quality is optimized.

---

## 13\_phase\_overview.md

Each phase has a hard boundary — what it's allowed to solve, what it isn't. This is what prevents scope creep once building starts.

---

### Phase 0 — Planning & Intent
**Purpose:** Lock in terminology, constraints, architecture before writing a line of code.
**Output:** This documentation. Frozen vocabulary and constraints.

---

### Phase 1 — MVP (Days 1–2)

The goal is one thing: audio in, playable MIDI out, web UI up, end-to-end, no crashes. Quality is secondary. Proving the pipeline closes is primary.

**Day 1 — Pipeline skeleton**

*Morning:* Set up environment (Demucs, Basic Pitch, pretty_midi, music21). Wire the first two stages: run Demucs on input audio, extract vocals and bass stems. Run Basic Pitch on each stem separately, save as two raw MIDI files. Write a `load_midi(path) → list[Note]` abstraction that every downstream stage will use. Test on one song you know well.

*Afternoon:* Right hand = vocal MIDI as-is. Left hand = bass MIDI quantized to quarter notes (snap to nearest beat, discard duration detail for now). Merge both hands into a single two-track MIDI file. Play it back. At end of Day 1 there should be something that plays back and is recognizably the song.

**Day 2 — Three essential transforms + web UI**

*Morning:* Implement the transform chain, each as its own function (note list in, note list out):

1. **Density reducer** — for each 500ms window, if note count exceeds `120 / BPM`, keep only the longest-duration notes until under the limit
2. **Span enforcer** — for simultaneous notes in one hand spanning > 9 semitones, drop lowest in right hand or highest in left
3. **Note cap** — reduce each hand to ≤ 3 simultaneous notes, dropping by shortest duration first

*Afternoon:* Minimal web UI — FastAPI backend with a single file upload endpoint + a single-page frontend (file picker, upload button, MIDI download). Deploy to Hugging Face Spaces or Railway. The CLI stays as an internal dev tool. Test end-to-end on 2–3 songs.

**Not in scope:** Output quality, advanced voicings, sheet music.

---

### Phase 2 — Musical Quality (Week 2)

Phase 1 closes the loop. Phase 2 makes the output actually sound like an intentional arrangement.

**Chord-aware left hand.** Use music21's chord detection on the bass + "other" stems together to identify the chord at each beat. Generate the left hand from the chord symbol — root-position triad (root + third + fifth) voiced within one octave — rather than from the raw bass transcription. This is the single highest-impact improvement in the project.

**MuseScore PDF rendering.** Convert output MIDI to MusicXML via music21, call MuseScore's CLI headlessly, render a PDF. Serve it alongside the MIDI in the web UI. A rendered sheet music PDF of a song someone just uploaded is the "wow" demo moment. It makes the project immediately legible to any visitor, musical or not.

**Before/after examples.** Add 3–4 song examples to `examples/sample_outputs/` with the original audio clip, raw transcription MIDI, and final arranged MIDI side by side. This is the most effective way to communicate what the system actually does.

**Output:** Measurably better arrangements + sheet music output + updated README with live examples.

---

### Phase 3 — DSP & Signal Quality (Week 3)

Phase 2 gives us good structure. Phase 3 makes the notes themselves cleaner.

**Beat tracking with madmom.** Replace simple tempo-based timing with proper downbeat detection via madmom's pre-trained RNN. Accurate beat positions make metric strength scoring significantly more reliable and improve every timing-dependent transform.

**Melody smoothing.** After vocal transcription, compute the melodic contour and apply a smoothing pass: remove ornaments, grace notes, and melisma (rapid pitch changes on one syllable). Keep only notes above a minimum duration threshold relative to tempo. This makes the right hand cleaner without losing the melodic shape.

**Dynamic tempo-aware density scaling.** Replace the fixed density threshold with `max_notes_per_beat = 120 / BPM`. Correctly tightens constraints at fast tempos, relaxes them at slow ones.

**Output:** Cleaner melody, better rhythm, tighter playability enforcement.

---

### Phase 4 — AI-Assisted Refinement (Later / Stretch)

Research-grade improvements for when the core pipeline is solid. Single GPU constraint applies to any training.

**Chord recognition upgrade.** Swap music21's built-in key finding for a MIREX-benchmark chord model from HuggingFace. Beat-level chord labels → better left hand voicing decisions throughout.

**Voice leading optimization.** Model the left hand voicing problem as shortest-path search over a chord graph, where edge weights penalize large leaps between successive chords. Music21 has voice leading utilities as a starting point.

**Fine-tuned arrangement model (ambitious).** The research framing: given a raw MIDI sequence, predict a simplified pianist version. Dataset: POP909 (pop songs paired with piano arrangements) + ATEPP (professional performance MIDI), both free and well-documented. A small transformer fine-tuned on POP909 fits on a single GPU and represents genuinely publishable-quality work if done well.

**LLM-assisted post-processing.** Use the Claude API to take a symbolic representation of the arrangement (chord symbols + melody contour as structured text) and suggest corrections to voicing or hand assignment. Effective for edge cases the rule engine misses, fast to prototype.

---

### Phase 5 — Polish & Presentation

**Difficulty scoring.** After arrangement, compute a score from max span, average density, and rhythmic complexity. Display to the user — gives the output a concrete, communicable property.

**README as product document.** Lead with: what this is, who it's for, live demo link, before/after audio examples. Architecture comes after. Most GitHub repos lead with architecture. This one leads with the problem.

**Example gallery.** 4–6 songs covering different tempos, keys, and feels. Shows range and gives visitors something to click.

**Output:** Polished repo, clear project narrative, live demo, sheet music output — something a non-technical founder can evaluate in under a minute.