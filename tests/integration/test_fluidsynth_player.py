import os

import pytest

from music_generator.domain.composition import MusicalComposition
from music_generator.domain.events import InstrumentChangeEvent, NoteEvent
from music_generator.infrastructure.audio.fluidsynth_player import FluidSynthPlayer


@pytest.mark.integration
def test_fluidsynth_player_can_play_short_composition() -> None:
    soundfont_path = os.environ.get("SOUNDFONT_PATH")
    if not soundfont_path:
        pytest.skip("SOUNDFONT_PATH is not configured.")

    composition = MusicalComposition(
        events=[
            InstrumentChangeEvent(instrument=0),
            NoteEvent(
                note_name="C",
                midi_number=60,
                octave=4,
                volume=60,
                instrument=0,
                duration_beats=0.05,
            ),
        ],
        initial_bpm=120,
    )

    player = FluidSynthPlayer(soundfont_path=soundfont_path)
    try:
        player.play(composition)
    finally:
        player.close()
