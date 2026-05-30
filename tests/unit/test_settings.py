import pytest

from music_generator.domain.settings import PlaybackSettings


def test_valid_playback_settings_are_created() -> None:
    settings = PlaybackSettings(
        bpm=120,
        initial_volume=80,
        default_octave=4,
        initial_instrument=0,
    )

    assert settings.bpm == 120
    assert settings.initial_volume == 80
    assert settings.default_octave == 4
    assert settings.initial_instrument == 0


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("bpm", 0, "bpm"),
        ("initial_volume", -1, "initial_volume"),
        ("initial_volume", 128, "initial_volume"),
        ("default_octave", -1, "default_octave"),
        ("default_octave", 10, "default_octave"),
        ("initial_instrument", -1, "initial_instrument"),
        ("initial_instrument", 128, "initial_instrument"),
    ],
)
def test_invalid_playback_settings_raise_useful_errors(
    field: str,
    value: int,
    message: str,
) -> None:
    kwargs = {
        "bpm": 120,
        "initial_volume": 80,
        "default_octave": 4,
        "initial_instrument": 0,
    }
    kwargs[field] = value

    with pytest.raises(ValueError, match=message):
        PlaybackSettings(**kwargs)


def test_playback_settings_are_immutable() -> None:
    settings = PlaybackSettings(
        bpm=120,
        initial_volume=80,
        default_octave=4,
        initial_instrument=0,
    )

    with pytest.raises(Exception):
        settings.bpm = 90  # type: ignore[misc]
