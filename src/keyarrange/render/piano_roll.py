"""Renders a static piano roll PNG from a two-track arranged MIDI file."""
import logging

import matplotlib
matplotlib.use("Agg")  # non-interactive backend — safe for server use
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pretty_midi

logger = logging.getLogger(__name__)

# Pitch range displayed (covers standard piano arrangement output)
PITCH_LOW = 36   # C2
PITCH_HIGH = 84  # C6

RIGHT_COLOR = "#4a9eff"   # blue — right hand (vocals/melody)
LEFT_COLOR  = "#ff6b6b"   # red  — left hand (bass/harmony)
BG_COLOR    = "#0d0d0d"
SURFACE     = "#141414"
ACCENT      = "#c8f043"


def render_piano_roll(midi_path: str, output_path: str) -> str:
    """Read MIDI at midi_path, write piano roll PNG to output_path, return output_path."""
    pm = pretty_midi.PrettyMIDI(midi_path)
    duration = pm.get_end_time()
    if duration == 0:
        raise ValueError("MIDI file has no notes.")

    fig_w, fig_h = 14, 5
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(SURFACE)

    pitch_range = PITCH_HIGH - PITCH_LOW
    note_height = 0.75  # in pitch units

    # --- time grid lines every 2 seconds ---
    for t in range(0, int(duration) + 1, 2):
        ax.axvline(x=t, color="white", alpha=0.08, linewidth=0.5, zorder=1)

    # --- middle C divider (pitch 60) ---
    ax.axhline(y=60, color="white", alpha=0.25, linewidth=0.8, linestyle="--", zorder=2)
    ax.text(duration * 0.01, 60.3, "C4 · middle C",
            color="white", alpha=0.35, fontsize=7, fontfamily="monospace")

    # --- draw notes per track ---
    colors = [RIGHT_COLOR, LEFT_COLOR]
    labels = ["Right hand (melody)", "Left hand (harmony)"]

    for track_idx, instrument in enumerate(pm.instruments[:2]):
        color = colors[track_idx] if track_idx < len(colors) else "#aaaaaa"
        for note in instrument.notes:
            if not (PITCH_LOW <= note.pitch <= PITCH_HIGH):
                continue
            rect = mpatches.FancyBboxPatch(
                (note.start, note.pitch - note_height / 2),
                note.end - note.start,
                note_height,
                boxstyle="round,pad=0.02",
                linewidth=0,
                facecolor=color,
                alpha=0.85,
                zorder=3,
            )
            ax.add_patch(rect)

    # --- keyboard strip on left edge ---
    _draw_keyboard_strip(ax, duration)

    # --- axes ---
    ax.set_xlim(0, duration)
    ax.set_ylim(PITCH_LOW - 1, PITCH_HIGH + 1)
    ax.set_xlabel("Time (seconds)", color="#666", fontsize=9, labelpad=6)
    ax.tick_params(colors="#444")
    ax.spines[:].set_visible(False)

    # y-axis: show octave labels only
    octave_ticks = [p for p in range(PITCH_LOW, PITCH_HIGH + 1) if p % 12 == 0]
    ax.set_yticks(octave_ticks)
    ax.set_yticklabels([pretty_midi.note_number_to_name(p) for p in octave_ticks],
                       color="#555", fontsize=8)

    # --- legend ---
    legend_patches = [
        mpatches.Patch(color=RIGHT_COLOR, label=labels[0]),
        mpatches.Patch(color=LEFT_COLOR,  label=labels[1]),
    ]
    ax.legend(handles=legend_patches, loc="upper right",
              facecolor="#1a1a1a", edgecolor="#333",
              labelcolor="white", fontsize=9, framealpha=0.9)

    plt.tight_layout(pad=0.5)
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close(fig)
    logger.info(f"Piano roll saved: {output_path}")
    return output_path


def _draw_keyboard_strip(ax, duration):
    """Draws a minimal keyboard indicator along the left edge of the plot."""
    strip_width = duration * 0.012  # ~1.2% of total width
    x0 = -strip_width * 1.1

    # Black key pitches within an octave (semitone offsets: 1,3,6,8,10)
    black_offsets = {1, 3, 6, 8, 10}

    for pitch in range(PITCH_LOW, PITCH_HIGH + 1):
        is_black = (pitch % 12) in black_offsets
        color = "#111" if is_black else "#ddd"
        rect = mpatches.Rectangle(
            (x0, pitch - 0.45),
            strip_width * (0.6 if is_black else 1.0),
            0.88,
            linewidth=0.3,
            edgecolor="#333",
            facecolor=color,
            zorder=4,
            clip_on=False,
        )
        ax.add_patch(rect)
