#!/usr/bin/env python3
"""
Style Analyzer for Wolfgang v2.

Extracts quantitative style fingerprints from kern/MIDI/MusicXML scores.
Used by ``review_style_gate`` (and through it /w-review) to compare composed
output against corpus-derived style targets.

This is a GUARDRAIL tool — it catches gross statistical failures (0% triplets,
half the expected density, zero dynamics). Subtle musical quality is evaluated
by the agent, not by this script.

Usage:
    python3 tools/style_analyzer.py <score-file>                      # single file → JSON
    python3 tools/style_analyzer.py --batch <directory> [--filter piano] [--json-dir <dir>]
    python3 tools/style_analyzer.py --aggregate <json-dir> --output <style-targets.json>
"""

import argparse
import json
import os
import sys
import warnings
from collections import Counter

# NOT `warnings.filterwarnings("ignore")` at import time. This module is
# imported by the review path, and a global filter silenced every warning in the
# whole process — including music21's warnings about malformed scores, which are
# exactly the signal this project needs. Warnings are suppressed only around the
# parse calls that legitimately produce noise (see `_quiet`).
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from music21 import chord as m21chord
    from music21 import converter, interval, note
except ImportError as exc:  # pragma: no cover - environment guard
    # A library module must RAISE, not kill the interpreter. `sys.exit(1)` here
    # meant that importing this module anywhere without music21 terminated the
    # process, with no traceback and no chance for a caller to fall back.
    raise ImportError(
        "music21 is required for style analysis. Install with: pip install music21"
    ) from exc


@contextmanager
def _quiet():
    """Suppress warnings for one parse, not for the whole process."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        yield


# ── Metric Extraction ──


def analyze_score(filepath: str) -> Optional[Dict[str, Any]]:
    """Extract all style metrics from a single score file.

    Returns a dict with ~25 metrics, or None if parsing fails.
    """
    try:
        with _quiet():
            score = converter.parse(filepath)
    except Exception as e:
        print(f"  WARN: Could not parse {filepath}: {e}", file=sys.stderr)
        return None

    parts = list(score.parts)
    if not parts:
        return None

    measures = list(parts[0].getElementsByClass("Measure"))
    nb = max(len(measures), 1)
    all_notes = list(score.recurse().getElementsByClass(["Note", "Chord"]))
    total_events = len(all_notes)
    if total_events == 0:
        return None

    result: Dict[str, Any] = {
        "file": os.path.basename(filepath),
        "bars": nb,
        "total_events": total_events,
    }

    # ── RHYTHM METRICS ──

    result["events_per_bar"] = round(total_events / nb, 1)

    rh_events = len(list(parts[0].recurse().getElementsByClass(["Note", "Chord"])))
    lh_events = (
        len(list(parts[1].recurse().getElementsByClass(["Note", "Chord"]))) if len(parts) > 1 else 0
    )
    result["events_per_bar_rh"] = round(rh_events / nb, 1)
    result["events_per_bar_lh"] = round(lh_events / nb, 1)

    # Duration distribution
    dur_counts: Counter = Counter()
    triplet_count = 0
    for n in all_notes:
        ql = round(float(n.duration.quarterLength), 3)
        dur_counts[ql] += 1
        if abs(ql - 0.333) < 0.02 or abs(ql - 0.167) < 0.02 or abs(ql - 0.667) < 0.02:
            triplet_count += 1

    result["triplet_pct"] = round(triplet_count / total_events * 100, 1)
    result["duration_top5"] = [
        (round(d, 3), c, round(c / total_events * 100, 1)) for d, c in dur_counts.most_common(5)
    ]
    result["rhythmic_variety"] = len(dur_counts)

    # Rest ratio
    rests = list(score.recurse().getElementsByClass("Rest"))
    rest_beats = sum(float(r.duration.quarterLength) for r in rests)
    note_beats = sum(float(n.duration.quarterLength) for n in all_notes)
    result["rest_ratio"] = round(rest_beats / max(rest_beats + note_beats, 0.01) * 100, 1)

    # Phrase length (by rests in top voice)
    rh_all = list(parts[0].recurse().getElementsByClass(["Note", "Chord", "Rest"]))
    phrase_lengths: List[float] = []
    curr_phrase = 0.0
    for el in rh_all:
        ql = float(el.duration.quarterLength)
        if isinstance(el, note.Rest) and ql >= 0.5:
            if curr_phrase > 1:
                phrase_lengths.append(round(curr_phrase, 1))
            curr_phrase = 0
        else:
            curr_phrase += ql
    if curr_phrase > 1:
        phrase_lengths.append(round(curr_phrase, 1))
    result["phrase_length_avg"] = round(sum(phrase_lengths) / max(len(phrase_lengths), 1), 1)
    result["phrase_count"] = len(phrase_lengths)

    # Bass change rate
    if len(parts) >= 2:
        lh_notes = [n for n in parts[1].recurse().getElementsByClass("Note")]
        bass_changes = 0
        prev_midi = None
        for n in lh_notes[:300]:
            curr = n.pitch.midi
            if prev_midi is not None and curr != prev_midi:
                bass_changes += 1
            prev_midi = curr
        result["bass_change_rate"] = round(bass_changes / nb, 1)
    else:
        result["bass_change_rate"] = 0

    # ── MELODY METRICS ──

    rh_pitched = [n for n in parts[0].recurse().getElementsByClass("Note")]
    intervals_abs: List[int] = []
    for i in range(1, min(len(rh_pitched), 500)):
        try:
            intv = abs(int(interval.Interval(rh_pitched[i - 1], rh_pitched[i]).semitones))
            intervals_abs.append(intv)
        except Exception:
            pass

    total_intv = max(len(intervals_abs), 1)
    stepwise = sum(1 for i in intervals_abs if i <= 2)
    leaps = sum(1 for i in intervals_abs if i >= 5)
    large_leaps = sum(1 for i in intervals_abs if i >= 8)

    result["stepwise_pct"] = round(stepwise / total_intv * 100, 1)
    result["leap_pct"] = round(leaps / total_intv * 100, 1)
    result["large_leap_pct"] = round(large_leaps / total_intv * 100, 1)
    result["max_leap"] = max(intervals_abs) if intervals_abs else 0

    # Direction changes
    direction_changes = 0
    curr_dir = 0
    for intv_val in intervals_abs:
        new_dir = 1 if intv_val > 0 else 0
        # We need signed intervals for direction
        pass
    # Re-compute with signed intervals
    signed_intervals: List[int] = []
    for i in range(1, min(len(rh_pitched), 500)):
        try:
            intv = int(interval.Interval(rh_pitched[i - 1], rh_pitched[i]).semitones)
            signed_intervals.append(intv)
        except Exception:
            pass
    direction_changes = 0
    curr_dir = 0
    for intv_val in signed_intervals:
        new_dir = 1 if intv_val > 0 else (-1 if intv_val < 0 else 0)
        if new_dir != 0 and new_dir != curr_dir:
            direction_changes += 1
        if new_dir != 0:
            curr_dir = new_dir
    result["direction_changes_per_bar"] = round(direction_changes / nb, 1)

    # Register
    all_midi: List[int] = []
    for n in all_notes:
        if isinstance(n, note.Note):
            all_midi.append(n.pitch.midi)
        elif isinstance(n, m21chord.Chord):
            for p in n.pitches:
                all_midi.append(p.midi)
    if all_midi:
        result["register_low"] = min(all_midi)
        result["register_high"] = max(all_midi)
        result["register_range"] = max(all_midi) - min(all_midi)
        result["register_center"] = round(sum(all_midi) / len(all_midi), 1)

    # Chromatic percentage
    accidental_count = sum(
        1
        for n in score.recurse().getElementsByClass("Note")
        if n.pitch.accidental and n.pitch.accidental.name != "natural"
    )
    total_pitched = max(len(list(score.recurse().getElementsByClass("Note"))), 1)
    result["chromatic_pct"] = round(accidental_count / total_pitched * 100, 1)

    # ── HARMONY METRICS ──

    chords = [n for n in all_notes if isinstance(n, m21chord.Chord)]
    result["chord_pct"] = round(len(chords) / total_events * 100, 1)

    chord_sizes: Counter = Counter()
    chord_spans: List[int] = []
    for c in chords:
        chord_sizes[len(c.pitches)] += 1
        if len(c.pitches) >= 2:
            chord_spans.append(c.pitches[-1].midi - c.pitches[0].midi)
    result["chord_size_distribution"] = dict(sorted(chord_sizes.items()))
    result["avg_chord_span"] = (
        round(sum(chord_spans) / max(len(chord_spans), 1), 1) if chord_spans else 0
    )

    # Parallel vs contrary motion at bar boundaries
    if len(parts) >= 2:
        parallel = contrary = oblique = 0
        rh_measures = list(parts[0].getElementsByClass("Measure"))
        lh_measures = list(parts[1].getElementsByClass("Measure"))
        for m_idx in range(1, min(len(rh_measures), len(lh_measures), 50)):
            try:
                rh_prev = list(rh_measures[m_idx - 1].recurse().getElementsByClass("Note"))
                rh_curr = list(rh_measures[m_idx].recurse().getElementsByClass("Note"))
                lh_prev = list(lh_measures[m_idx - 1].recurse().getElementsByClass("Note"))
                lh_curr = list(lh_measures[m_idx].recurse().getElementsByClass("Note"))
                if rh_prev and rh_curr and lh_prev and lh_curr:
                    rh_dir = rh_curr[0].pitch.midi - rh_prev[-1].pitch.midi
                    lh_dir = lh_curr[0].pitch.midi - lh_prev[-1].pitch.midi
                    if rh_dir == 0 or lh_dir == 0:
                        oblique += 1
                    elif (rh_dir > 0 and lh_dir > 0) or (rh_dir < 0 and lh_dir < 0):
                        parallel += 1
                    else:
                        contrary += 1
            except Exception:
                pass
        total_motion = max(parallel + contrary + oblique, 1)
        result["parallel_motion_pct"] = round(parallel / total_motion * 100, 1)
        result["contrary_motion_pct"] = round(contrary / total_motion * 100, 1)

    # Suspension percentage (tied notes)
    ties = sum(1 for n in all_notes if hasattr(n, "tie") and n.tie is not None)
    result["suspension_pct"] = round(ties / total_events * 100, 1)

    # ── DYNAMICS METRICS ──

    dyn_list = list(score.recurse().getElementsByClass("Dynamic"))
    result["dynamic_markings"] = len(dyn_list)
    result["dynamic_markings_per_bar"] = round(len(dyn_list) / nb, 2)

    sf_count = sum(1 for d in dyn_list if any(x in str(d.value) for x in ["sf", "fp", "rfz"]))
    result["sf_density"] = round(sf_count / nb, 2)

    # Subito changes (jumps ≥2 dynamic levels)
    dyn_levels = {"ppp": 1, "pp": 2, "p": 3, "mp": 4, "mf": 5, "f": 6, "ff": 7, "fff": 8}
    subito_count = 0
    prev_level = None
    for d in dyn_list:
        val = d.value if hasattr(d, "value") else str(d)
        curr_level = dyn_levels.get(val)
        if curr_level and prev_level and abs(curr_level - prev_level) >= 2:
            subito_count += 1
        if curr_level:
            prev_level = curr_level
    result["subito_changes"] = subito_count

    # ── TEXTURE METRICS ──

    # Per-bar density is summed across ALL staves (both hands), matching
    # corpus_metrics.bar_metrics. A piano's texture ebb-and-flow lives mostly
    # in the LH accompaniment; counting only parts[0] (the RH melody, which is
    # naturally uniform at ~3-6 notes/bar) badly undercounts texture change.
    part_measures = [list(p.getElementsByClass("Measure")) for p in parts]
    bar_densities: List[int] = []
    bar_rhythms: List[tuple] = []
    for i in range(min(len(measures), 100)):
        n_in_bar = 0
        rhythm_notes = []
        for pm in part_measures:
            if i < len(pm):
                notes = list(pm[i].recurse().getElementsByClass(["Note", "Chord"]))
                n_in_bar += len(notes)
                rhythm_notes.extend(notes)
        bar_densities.append(n_in_bar)
        bar_rhythms.append(
            tuple(round(float(n.duration.quarterLength), 2) for n in rhythm_notes[:12])
        )

    # Texture change rate (density shifts ≥4)
    texture_shifts = sum(
        1 for i in range(1, len(bar_densities)) if abs(bar_densities[i] - bar_densities[i - 1]) >= 4
    )
    result["texture_change_pct"] = round(texture_shifts / nb * 100, 1)

    # Identical consecutive bars
    consec_same = sum(
        1
        for i in range(1, len(bar_rhythms))
        if bar_rhythms[i] == bar_rhythms[i - 1] and len(bar_rhythms[i]) > 2
    )
    result["identical_consecutive_pct"] = round(consec_same / nb * 100, 1)

    # Hand simultaneity
    if len(parts) >= 2:
        rh_onsets = set()
        lh_onsets = set()
        for n in parts[0].recurse().getElementsByClass(["Note", "Chord"]):
            rh_onsets.add(round(float(n.offset), 3))
        for n in parts[1].recurse().getElementsByClass(["Note", "Chord"]):
            lh_onsets.add(round(float(n.offset), 3))
        all_onsets = rh_onsets | lh_onsets
        simultaneous = len(rh_onsets & lh_onsets)
        result["hand_simultaneity_pct"] = round(simultaneous / max(len(all_onsets), 1) * 100, 1)

    # Density coefficient of variation
    if bar_densities:
        mean_d = sum(bar_densities) / len(bar_densities)
        std_d = (sum((d - mean_d) ** 2 for d in bar_densities) / len(bar_densities)) ** 0.5
        result["density_cv"] = round(std_d / max(mean_d, 0.01), 2)
        result["density_min"] = min(bar_densities)
        result["density_max"] = max(bar_densities)

    # ── ADVANCED METRICS (harmonic rhythm, cadences, voice independence, etc.) ──

    result.update(analyze_harmonic_rhythm(score))
    result.update(analyze_cadences(score))
    result.update(analyze_voice_independence(score))
    result.update(analyze_articulations(score))
    result.update(analyze_modulations(score))
    result.update(analyze_chord_quality(score))
    result.update(analyze_voicing_smoothness(score))

    return result


# ── Advanced Metric Functions ──


def analyze_harmonic_rhythm(score, max_measures=150):
    """Analyze how frequently chords change."""
    try:
        chordified = score.chordify()
        measures = list(chordified.recurse().getElementsByClass("Measure"))[:max_measures]

        chord_changes = 0
        total_beats = 0
        prev_chord_name = None
        change_intervals = []
        beats_since_change = 0

        for m in measures:
            for chord in m.recurse().getElementsByClass("Chord"):
                total_beats += chord.quarterLength
                beats_since_change += chord.quarterLength
                current_name = chord.pitchedCommonName
                if prev_chord_name is not None and current_name != prev_chord_name:
                    chord_changes += 1
                    change_intervals.append(beats_since_change)
                    beats_since_change = 0
                prev_chord_name = current_name

        if chord_changes == 0:
            return {"harmonic_rhythm_avg": None, "harmonic_rhythm_cv": None}

        avg = sum(change_intervals) / len(change_intervals) if change_intervals else None
        if avg and len(change_intervals) > 1:
            import statistics

            stdev = statistics.stdev(change_intervals)
            cv = stdev / avg if avg > 0 else 0
        else:
            cv = None

        return {
            "harmonic_rhythm_avg": round(avg, 2) if avg else None,
            "harmonic_rhythm_cv": round(cv, 3) if cv else None,
        }
    except Exception:
        return {"harmonic_rhythm_avg": None, "harmonic_rhythm_cv": None}


def analyze_cadences(score, max_measures=100):
    """Detect cadence types at phrase boundaries."""
    try:
        from music21 import roman

        score_key = score.analyze("key")
        chordified = score.chordify()
        measures = list(chordified.recurse().getElementsByClass("Measure"))[:max_measures]

        # Find phrase boundaries (rests in top voice)
        top_part = score.parts[0] if score.parts else score
        phrase_end_measures = set()
        for n in top_part.recurse().getElementsByClass("Rest"):
            if n.quarterLength >= 0.5:
                phrase_end_measures.add(n.measureNumber)

        cadence_types = {"PAC": 0, "IAC": 0, "HC": 0, "deceptive": 0, "plagal": 0, "other": 0}
        total_cadences = 0

        for m_num in phrase_end_measures:
            try:
                # Get the last two chords near the phrase boundary
                target_m = None
                prev_m = None
                for m in measures:
                    if m.number == m_num:
                        target_m = m
                    elif m.number == m_num - 1:
                        prev_m = m

                if not target_m or not prev_m:
                    continue

                chords_prev = list(prev_m.recurse().getElementsByClass("Chord"))
                chords_curr = list(target_m.recurse().getElementsByClass("Chord"))

                if not chords_prev or not chords_curr:
                    continue

                penult = chords_prev[-1]
                final = chords_curr[0] if chords_curr else chords_prev[-1]

                try:
                    rn_penult = roman.romanNumeralFromChord(penult, score_key)
                    rn_final = roman.romanNumeralFromChord(final, score_key)
                except Exception:
                    continue

                penult_fig = rn_penult.romanNumeralAlone.upper()
                final_fig = rn_final.romanNumeralAlone.upper()

                total_cadences += 1

                if penult_fig == "V" and final_fig == "I":
                    cadence_types["PAC"] += 1
                elif penult_fig == "V" and final_fig == "VI":
                    cadence_types["deceptive"] += 1
                elif final_fig == "V":
                    cadence_types["HC"] += 1
                elif penult_fig == "IV" and final_fig == "I":
                    cadence_types["plagal"] += 1
                else:
                    cadence_types["other"] += 1
            except Exception:
                continue

        total_bars = len(measures)
        cadence_freq = (total_cadences / (total_bars / 8.0)) if total_bars > 0 else None
        deceptive_pct = (
            (cadence_types["deceptive"] / total_cadences * 100) if total_cadences > 0 else 0
        )
        half_cadence_pct = (cadence_types["HC"] / total_cadences * 100) if total_cadences > 0 else 0

        return {
            "cadence_frequency": round(cadence_freq, 2) if cadence_freq else None,
            "deceptive_cadence_pct": round(deceptive_pct, 1),
            "half_cadence_pct": round(half_cadence_pct, 1),
            "cadence_types": cadence_types,
        }
    except Exception:
        return {
            "cadence_frequency": None,
            "deceptive_cadence_pct": None,
            "half_cadence_pct": None,
            "cadence_types": None,
        }


def analyze_voice_independence(score, max_measures=100):
    """Measure how independently voices move relative to each other."""
    try:
        parts = score.parts
        if len(parts) < 2:
            return {"voice_independence_score": None}

        # Compare first two parts (or top and bottom)
        top = parts[0]
        bottom = parts[-1] if len(parts) > 1 else parts[0]

        contrary = 0
        parallel = 0
        oblique = 0
        total = 0

        top_notes = [n for n in top.recurse().getElementsByClass("Note")][:500]
        bottom_notes = [n for n in bottom.recurse().getElementsByClass("Note")][:500]

        for i in range(1, min(len(top_notes), len(bottom_notes))):
            top_dir = top_notes[i].pitch.midi - top_notes[i - 1].pitch.midi
            bot_dir = bottom_notes[i].pitch.midi - bottom_notes[i - 1].pitch.midi
            total += 1

            if top_dir == 0 or bot_dir == 0:
                oblique += 1
            elif (top_dir > 0 and bot_dir < 0) or (top_dir < 0 and bot_dir > 0):
                contrary += 1
            else:
                parallel += 1

        independence = (contrary + oblique) / total if total > 0 else None

        return {"voice_independence_score": round(independence, 3) if independence else None}
    except Exception:
        return {"voice_independence_score": None}


def analyze_articulations(score, max_notes=500):
    """Analyze balance of articulation types."""
    try:
        from music21 import spanner

        notes = list(score.recurse().getElementsByClass("Note"))[:max_notes]
        total = len(notes)
        if total == 0:
            return {"staccato_pct": None, "legato_span_avg": None, "articulation_variety": None}

        staccato_count = 0
        tenuto_count = 0
        accent_count = 0
        marcato_count = 0
        art_types = set()

        for n in notes:
            for art in n.articulations:
                art_name = type(art).__name__.lower()
                art_types.add(art_name)
                if "staccato" in art_name:
                    staccato_count += 1
                elif "tenuto" in art_name:
                    tenuto_count += 1
                elif "accent" in art_name:
                    accent_count += 1
                elif "marcato" in art_name:
                    marcato_count += 1

        # Slur spans
        slurs = list(score.recurse().getElementsByClass(spanner.Slur))
        slur_lengths = []
        for s in slurs[:100]:
            try:
                slur_lengths.append(len(s.getSpannedElements()))
            except Exception:
                pass

        legato_avg = sum(slur_lengths) / len(slur_lengths) if slur_lengths else 0

        return {
            "staccato_pct": round(staccato_count / total * 100, 1),
            "legato_span_avg": round(legato_avg, 1),
            "articulation_variety": len(art_types),
        }
    except Exception:
        return {"staccato_pct": None, "legato_span_avg": None, "articulation_variety": None}


def analyze_modulations(score, window_size=8, max_measures=150):
    """Track key changes across windowed segments."""
    try:
        measures = list(score.recurse().getElementsByClass("Measure"))[:max_measures]
        if len(measures) < window_size:
            return {
                "modulations_per_section": None,
                "tonal_stability": None,
                "key_area_count": None,
            }

        global_key = score.analyze("key")

        keys_detected = []
        for i in range(0, len(measures) - window_size + 1, window_size // 2):  # 50% overlap
            window = score.measures(
                measures[i].number, measures[min(i + window_size - 1, len(measures) - 1)].number
            )
            try:
                local_key = window.analyze("key")
                keys_detected.append(local_key.tonic.name + " " + local_key.mode)
            except Exception:
                keys_detected.append(None)

        # Count key changes
        modulations = 0
        unique_keys = set()
        for i in range(1, len(keys_detected)):
            if (
                keys_detected[i]
                and keys_detected[i - 1]
                and keys_detected[i] != keys_detected[i - 1]
            ):
                modulations += 1
            if keys_detected[i]:
                unique_keys.add(keys_detected[i])

        # Tonal stability = % of windows matching global key
        global_key_str = global_key.tonic.name + " " + global_key.mode
        matching = sum(1 for k in keys_detected if k == global_key_str)
        stability = matching / len(keys_detected) * 100 if keys_detected else None

        return {
            "modulations_per_section": modulations,
            "tonal_stability": round(stability, 1) if stability else None,
            "key_area_count": len(unique_keys),
        }
    except Exception:
        return {"modulations_per_section": None, "tonal_stability": None, "key_area_count": None}


def analyze_chord_quality(score, max_measures=150):
    """Classify chord qualities across the piece."""
    try:
        chordified = score.chordify()
        chords = list(chordified.recurse().getElementsByClass("Chord"))[:500]

        if not chords:
            return {
                "major_chord_pct": None,
                "minor_chord_pct": None,
                "dim_chord_pct": None,
                "dom7_chord_pct": None,
            }

        total = len(chords)
        qualities = {
            "major": 0,
            "minor": 0,
            "diminished": 0,
            "augmented": 0,
            "dominant-seventh": 0,
            "other": 0,
        }

        for c in chords:
            q = c.quality
            if q in qualities:
                qualities[q] += 1
            elif "dominant" in str(c.commonName).lower() and "seventh" in str(c.commonName).lower():
                qualities["dominant-seventh"] += 1
            else:
                qualities["other"] += 1

        return {
            "major_chord_pct": round(qualities["major"] / total * 100, 1),
            "minor_chord_pct": round(qualities["minor"] / total * 100, 1),
            "dim_chord_pct": round(qualities["diminished"] / total * 100, 1),
            "dom7_chord_pct": round(qualities["dominant-seventh"] / total * 100, 1),
        }
    except Exception:
        return {
            "major_chord_pct": None,
            "minor_chord_pct": None,
            "dim_chord_pct": None,
            "dom7_chord_pct": None,
        }


def analyze_voicing_smoothness(score, max_measures=150):
    """Measure voice-leading distance between consecutive chords."""
    try:
        chordified = score.chordify()
        chords = list(chordified.recurse().getElementsByClass("Chord"))[:500]

        if len(chords) < 2:
            return {"voice_leading_distance_avg": None, "voice_leading_distance_max": None}

        distances = []
        for i in range(1, len(chords)):
            prev_pitches = sorted([p.midi for p in chords[i - 1].pitches])
            curr_pitches = sorted([p.midi for p in chords[i].pitches])

            # Match voices by proximity (greedy)
            min_len = min(len(prev_pitches), len(curr_pitches))
            if min_len == 0:
                continue

            total_dist = sum(abs(curr_pitches[j] - prev_pitches[j]) for j in range(min_len))
            distances.append(total_dist)

        if not distances:
            return {"voice_leading_distance_avg": None, "voice_leading_distance_max": None}

        return {
            "voice_leading_distance_avg": round(sum(distances) / len(distances), 2),
            "voice_leading_distance_max": max(distances),
        }
    except Exception:
        return {"voice_leading_distance_avg": None, "voice_leading_distance_max": None}


# ── Aggregation ──


def aggregate_results(results: List[Dict]) -> Dict[str, Any]:
    """Compute mean/median/stdev for each metric across multiple analyses."""
    if not results:
        return {}

    numeric_keys = set()
    for r in results:
        for k, v in r.items():
            if isinstance(v, (int, float)) and k not in ("bars", "total_events"):
                numeric_keys.add(k)

    targets: Dict[str, Dict] = {}
    for key in sorted(numeric_keys):
        vals = [r[key] for r in results if key in r and isinstance(r[key], (int, float))]
        if not vals:
            continue
        vals_sorted = sorted(vals)
        n = len(vals)
        mean_val = sum(vals) / n
        median_val = (
            vals_sorted[n // 2] if n % 2 else (vals_sorted[n // 2 - 1] + vals_sorted[n // 2]) / 2
        )
        stdev_val = (sum((v - mean_val) ** 2 for v in vals) / n) ** 0.5

        targets[key] = {
            "mean": round(mean_val, 2),
            "median": round(median_val, 2),
            "stdev": round(stdev_val, 2),
            "min": round(min(vals), 2),
            "max": round(max(vals), 2),
            "n": n,
        }

    return targets


# ── CLI ──


def main():
    parser = argparse.ArgumentParser(description="Style Analyzer for Wolfgang v2")
    parser.add_argument("input", nargs="?", help="Score file to analyze (kern, MIDI, MusicXML)")
    parser.add_argument("--batch", help="Directory of score files to analyze in batch")
    parser.add_argument("--filter", help="Filter batch files by keyword (e.g., 'piano')")
    parser.add_argument(
        "--json-dir", help="Output directory for per-file JSON results (batch mode)"
    )
    parser.add_argument("--aggregate", help="Directory of per-file JSON results to aggregate")
    parser.add_argument("--output", help="Output file for aggregated style targets")
    parser.add_argument("--json", action="store_true", help="Output as JSON (single file mode)")
    args = parser.parse_args()

    if args.aggregate:
        # Aggregate mode
        json_dir = Path(args.aggregate)
        results = []
        for f in sorted(json_dir.glob("*.json")):
            try:
                data = json.loads(f.read_text())
                results.append(data)
            except Exception:
                pass
        targets = aggregate_results(results)
        output = {
            "reference_count": len(results),
            "reference_files": [r.get("file", "?") for r in results],
            "targets": targets,
        }
        if args.output:
            Path(args.output).write_text(json.dumps(output, indent=2))
            print(f"✓ Aggregated {len(results)} results → {args.output}")
        else:
            print(json.dumps(output, indent=2))
        return

    if args.batch:
        # Batch mode
        batch_dir = Path(args.batch)
        json_out_dir = Path(args.json_dir) if args.json_dir else batch_dir / "analysis"
        json_out_dir.mkdir(parents=True, exist_ok=True)

        files = sorted(batch_dir.glob("*.*"))
        valid_ext = {".krn", ".mid", ".midi", ".musicxml", ".mxl", ".xml"}
        files = [f for f in files if f.suffix.lower() in valid_ext]
        if args.filter:
            files = [f for f in files if args.filter.lower() in f.stem.lower()]

        print(f"Analyzing {len(files)} files from {batch_dir}...")
        for f in files:
            result = analyze_score(str(f))
            if result:
                out_path = json_out_dir / f"{f.stem}.json"
                out_path.write_text(json.dumps(result, indent=2))
                print(
                    f"  ✓ {f.name} → {result['events_per_bar']} epb, {result['triplet_pct']}% triplets"
                )
            else:
                print(f"  ✗ {f.name} — could not analyze")
        print(f"Results in: {json_out_dir}")
        return

    if args.input:
        # Single file mode
        result = analyze_score(args.input)
        if result is None:
            print(f"ERROR: Could not analyze {args.input}", file=sys.stderr)
            sys.exit(1)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(
                f"\nStyle Analysis: {result['file']} ({result['bars']} bars, {result['total_events']} events)"
            )
            print(f"{'─' * 60}")
            print("  Rhythm:")
            print(
                f"    Events/bar: {result['events_per_bar']} (RH: {result['events_per_bar_rh']}, LH: {result['events_per_bar_lh']})"
            )
            print(f"    Triplet %: {result['triplet_pct']}%")
            print(f"    Rest ratio: {result['rest_ratio']}%")
            print(
                f"    Phrase length avg: {result['phrase_length_avg']} beats ({result['phrase_count']} phrases)"
            )
            print(f"    Rhythmic variety: {result['rhythmic_variety']} duration types")
            print(f"    Bass change rate: {result['bass_change_rate']}/bar")
            print("  Melody:")
            print(
                f"    Stepwise: {result['stepwise_pct']}%, Leaps ≥P4: {result['leap_pct']}%, Large ≥P5: {result.get('large_leap_pct', '?')}%"
            )
            print(f"    Max leap: {result['max_leap']} semitones")
            print(
                f"    Register: {result.get('register_low', '?')}-{result.get('register_high', '?')} (span {result.get('register_range', '?')}, center {result.get('register_center', '?')})"
            )
            print(f"    Chromatic: {result['chromatic_pct']}%")
            print("  Harmony:")
            print(f"    Chord %: {result['chord_pct']}%")
            print(
                f"    Motion: {result.get('parallel_motion_pct', '?')}% parallel, {result.get('contrary_motion_pct', '?')}% contrary"
            )
            print(f"    Suspensions: {result['suspension_pct']}%")
            print("  Dynamics:")
            print(
                f"    Markings: {result['dynamic_markings']} ({result['dynamic_markings_per_bar']}/bar)"
            )
            print(f"    sf/sfp/fp density: {result['sf_density']}/bar")
            print(f"    Subito changes: {result['subito_changes']}")
            print("  Texture:")
            print(f"    Texture change: {result.get('texture_change_pct', '?')}%")
            print(f"    Identical consecutive: {result.get('identical_consecutive_pct', '?')}%")
            print(f"    Hand simultaneity: {result.get('hand_simultaneity_pct', '?')}%")
            print(
                f"    Density CV: {result.get('density_cv', '?')} (range {result.get('density_min', '?')}-{result.get('density_max', '?')})"
            )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
