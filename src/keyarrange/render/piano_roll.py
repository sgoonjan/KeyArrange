"""Renders a static piano roll PNG from right and left hand note lists."""
import logging

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pretty_midi

from keyarrange.dataclasses import Note

logger = logging.getLogger(__name__)

PITCH_LOW  = 36
PITCH_HIGH = 84

RIGHT_COLOR = "#4a9eff"
LEFT_COLOR  = "#ff6b6b"
BG_COLOR    = "#0d0d0d"
SURFACE     = "#141414"
ACCENT      = "#c8f043"


def render_piano_roll(
    right_hand: list[Note],
    left_hand: list[Note],
    output_path: str,
    duration: float | None = None,
) -> str:
    """Write piano roll PNG to output_path, return output_path."""
    all_notes = right_hand + left_hand
    if not all_notes:
        raise ValueError("No notes to render.")

    if duration is None:
        duration = max(n.start + n.duration for n in all_notes)

    fig_w, fig_h = 14, 5
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(SURFACE)

    note_height = 0.75

    for t in range(0, int(duration) + 1, 2):
        ax.axvline(x=t, color="white", alpha=0.08, linewidth=0.5, zorder=1)

    ax.axhline(y=60, color="white", alpha=0.25, linewidth=0.8, linestyle="--", zorder=2)
    ax.text(duration * 0.01, 60.3, "C4 · middle C",
            color="white", alpha=0.35, fontsize=7, fontfamily="monospace")

    for notes, color in ((right_hand, RIGHT_COLOR), (left_hand, LEFT_COLOR)):
        for note in notes:
            if not (PITCH_LOW <= note.pitch <= PITCH_HIGH):
                continue
            rect = mpatches.FancyBboxPatch(
                (note.start, note.pitch - note_height / 2),
                note.duration,
                note_height,
                boxstyle="round,pad=0.02",
                linewidth=0,
                facecolor=color,
                alpha=0.85,
                zorder=3,
            )
            ax.add_patch(rect)

    _draw_keyboard_strip(ax, duration)

    ax.set_xlim(0, duration)
    ax.set_ylim(PITCH_LOW - 1, PITCH_HIGH + 1)
    ax.set_xlabel("Time (seconds)", color="#666", fontsize=9, labelpad=6)
    ax.tick_params(colors="#444")
    ax.spines[:].set_visible(False)

    octave_ticks = [p for p in range(PITCH_LOW, PITCH_HIGH + 1) if p % 12 == 0]
    ax.set_yticks(octave_ticks)
    ax.set_yticklabels([pretty_midi.note_number_to_name(p) for p in octave_ticks],
                       color="#555", fontsize=8)

    legend_patches = [
        mpatches.Patch(color=RIGHT_COLOR, label="Right hand (melody)"),
        mpatches.Patch(color=LEFT_COLOR,  label="Left hand (harmony)"),
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
    strip_width = duration * 0.012
    x0 = -strip_width * 1.1
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