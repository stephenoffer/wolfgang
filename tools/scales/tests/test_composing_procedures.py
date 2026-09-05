"""The composers with the largest corpora had no worked composing procedure.

`phrase_prototypes` is extracted from ```json blocks in `composition-guide.md`
and read by `style_resolver`. It was empty for 33 packs — and that turned out
NOT to be an extractor bug. Measuring the guides:

    chopin      617 lines   13 json blocks   33 shorthand examples
    mozart      237          2                4
    haydn        59          0                0     <-  3,022 armed bars
    palestrina   24          0                0     <- 60,677 armed bars
    monteverdi   20          0                0     <-  3,885 armed bars

Their guides were good — five sharp fingerprints each and a "what this style
will not do" section — but they described the style without ever showing how to
write one. Chopin's guide walks through composing a phrase step by step with
real notes; theirs stopped at the traits.

So this was writing, not repair. Four worked procedures now exist:

    palestrina   a point of imitation: subject, staggered entries, the
                 continuation that RESTS to expose the next entry, the 7-6
                 suspension into a Dorian clausula with its musica ficta, and
                 the overlap into the next point
    monteverdi   set it correctly first, find the one word that hurts, break
                 exactly one rule there
    handel       bass first and walking, a leaping vocal line over it, exact
                 sequence, terraced echo, the grand pause
    haydn        a plain idea, then break the phrase length, then the silence

These tests check the thing that matters about a worked example: that its notes
are real. A procedure whose example does not play is worse than no procedure.
"""

import glob
from pathlib import Path

import pytest

from scales.context_compiler import ContextCompiler
from scales.duration import dur_to_beats
from scales.pitch import pitch_to_midi

#: Composers given a worked composing procedure, ordered by corpus size. Each
#: had a guide that described the style without ever showing how to write one.
_WRITTEN = (
    "palestrina",  # 60,677 armed bars, a 24-line guide
    "monteverdi",  #  3,885 bars, 20 lines
    "haydn",  #  3,022 bars, 59 lines
    "handel",  #  1,794 bars
    "mendelssohn",  #  1,774 bars
    "schumann",  #  1,456 bars
    "satie",  #    913 bars
    "faure",  #    517 bars
    "mussorgsky",  #    458 bars
    "liszt",  #    437 bars
    "vivaldi",  #    421 bars
    "rimsky-korsakov",  #    352 bars
)


def _prototypes(composer):
    hits = glob.glob(f".claude/context/*/composer-profiles/{composer}/")
    if not hits:
        pytest.skip(f"{composer} has no profile")
    compiler = ContextCompiler.__new__(ContextCompiler)
    return compiler._pass_prototypes(Path(hits[0]))["prototypes"]


@pytest.mark.parametrize("composer", _WRITTEN)
def test_the_composer_has_a_worked_procedure(composer):
    assert len(_prototypes(composer)) >= 3, (
        f"{composer} has no worked composing procedure — his guide describes the "
        "style without showing how to write one"
    )


@pytest.mark.parametrize("composer", _WRITTEN)
def test_every_note_in_every_example_is_playable(composer):
    """A worked example whose notes do not play is worse than no example."""
    for proto in _prototypes(composer):
        for name, events in proto["data"].items():
            assert isinstance(events, list) and events, f"{composer}/{name} is empty"
            for event in events:
                assert "p" in event and "d" in event, f"{composer}/{name}: {event}"
                for pitch in event["p"] if isinstance(event["p"], list) else [event["p"]]:
                    if pitch == "rest":
                        continue
                    assert pitch_to_midi(pitch) is not None, f"{composer}/{name}: {pitch}"
                assert dur_to_beats(event["d"]) > 0, f"{composer}/{name}: {event['d']}"


@pytest.mark.parametrize("composer", _WRITTEN)
def test_the_procedure_names_its_steps(composer):
    hits = glob.glob(f".claude/context/*/composer-profiles/{composer}/composition-guide.md")
    text = Path(hits[0]).read_text()
    assert "step by step" in text.lower()
    assert text.count("### Step") >= 4, "a procedure with fewer than four steps is a list"


# ─── The examples must be the composer's own idiom, not generic ──────────────


def test_palestrina_rests_before_an_entry():
    """A texture that never thins has no imitation in it, only simultaneity —
    so the continuation example must actually contain the rest."""
    protos = {k: v for p in _prototypes("palestrina") for k, v in p["data"].items()}
    continuation = protos.get("altus_continuation")
    assert continuation, "no continuation example"
    assert any(e["p"] == "rest" for e in continuation)


def test_palestrina_raises_the_leading_tone_only_at_the_cadence():
    """Musica ficta: an accidental at the clausula and nowhere else."""
    protos = {k: v for p in _prototypes("palestrina") for k, v in p["data"].items()}
    cadence = " ".join(str(e["p"]) for e in protos.get("tenor_cadence", []))
    subject = " ".join(str(e["p"]) for e in protos.get("subject", []))
    assert "#" in cadence, "the cadence has no raised leading tone"
    assert "#" not in subject, "the subject carries an accidental it should not"


def test_haydn_writes_a_real_silence():
    protos = {k: v for p in _prototypes("haydn") for k, v in p["data"].items()}
    pause = protos.get("the_pause")
    assert pause and sum(1 for e in pause if e["p"] == "rest") >= 2


def test_handel_terraces_rather_than_tapering():
    """The echo is the period's dynamic vocabulary; a hairpin is anachronistic."""
    protos = {k: v for p in _prototypes("handel") for k, v in p["data"].items()}
    echo = protos.get("echo_pair")
    assert echo and {e.get("dyn") for e in echo} == {"f", "p"}
    guide = glob.glob(".claude/context/*/composer-profiles/handel/composition-guide.md")[0]
    assert "hairpin" in Path(guide).read_text().lower(), "the guide must warn against them"


# ─── Each procedure must teach that composer, not a generic one ──────────────


def test_liszt_is_told_to_write_chords_and_rimsky_too():
    """Measured: 50% of Liszt's right-hand attacks and 62% of Rimsky's carry
    more than one note. A procedure that showed a single-line melody would
    teach the opposite of the corpus."""
    for composer in ("liszt", "rimsky-korsakov"):
        protos = _prototypes(composer)
        chorded = sum(
            1
            for p in protos
            for events in p["data"].values()
            for e in events
            if isinstance(e["p"], list)
        )
        assert chorded >= 3, f"{composer}'s worked example is a single line"


def test_satie_leaves_the_middle_register_empty():
    """Measured 21 semitones between his hands — the widest of any armed
    composer. The emptiness is the sound."""
    protos = {k: v for p in _prototypes("satie") for k, v in p["data"].items()}
    bass = protos.get("gymnopedie_bass")
    assert bass, "no bass example"
    lows = [pitch_to_midi(e["p"]) for e in bass if isinstance(e["p"], str) and e["p"] != "rest"]
    chords = [e["p"] for e in bass if isinstance(e["p"], list)]
    assert lows and chords
    assert min(pitch_to_midi(n) for n in chords[0]) - min(lows) >= 12


def test_mussorgsky_never_arpeggiates_and_stops_dead():
    protos = {k: v for p in _prototypes("mussorgsky") for k, v in p["data"].items()}
    assert any(e["p"] == "rest" for e in protos.get("sudden_silence", []))
    assert all(isinstance(e["p"], list) for e in protos.get("struck_block", []))


def test_schumann_displaces_the_melody_off_the_beat():
    protos = {k: v for p in _prototypes("schumann") for k, v in p["data"].items()}
    melody = protos.get("displaced_melody")
    assert melody and melody[0]["p"] == "rest", "the melody starts on the beat"
    assert any(e.get("tie") for e in melody), "nothing ties across the barline"


def test_every_procedure_says_what_to_check_afterwards():
    """A procedure without a way to tell whether you followed it is advice."""
    for composer in _WRITTEN:
        hits = glob.glob(f".claude/context/*/composer-profiles/{composer}/composition-guide.md")
        text = Path(hits[0]).read_text().lower()
        assert "checking a finished" in text, composer
